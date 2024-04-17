#!/usr/bin/env python3

import sys
import json
import asyncio
import asyncpg
import optparse
import logging
import configparser
from aio_pika import connect_robust, ExchangeType, Message, DeliveryMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)
streamhdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
streamhdlr.setFormatter(formatter)
logger.addHandler(streamhdlr)


COMPLETE_TILES_BAND_1 = """
    SELECT tile, obs, band, band1_cube_state FROM
        (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band1_cube_state FROM
            (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN cube_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                (SELECT tile, observation.name, observation.band, cube_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                WHERE band=1)
        GROUP BY tile, band) t1
        LEFT JOIN "tile" t2 USING (tile))
    WHERE (n_obs = n_complete) AND (
        band1_cube_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
        band1_cube_state = '' IS NOT FALSE
    );
"""

COMPLETE_TILES_BAND_2 = """
    SELECT tile, obs, band, band2_cube_state FROM
        (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band2_cube_state FROM
            (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN cube_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                (SELECT tile, observation.name, observation.band, cube_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                WHERE band=2)
        GROUP BY tile, band) t1
        LEFT JOIN "tile" t2 USING (tile))
    WHERE (n_obs = n_complete) AND (
        band2_cube_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
        (band2_cube_state = '') IS NOT FALSE
    );
"""

COMPLETE_TILES_MFS_BAND_1 = """
    SELECT tile, obs, band, band1_mfs_state FROM
        (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band1_mfs_state FROM
            (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN mfs_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                (SELECT tile, observation.name, observation.band, mfs_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                WHERE band=1)
        GROUP BY tile, band) t1
        LEFT JOIN "tile" t2 USING (tile))
    WHERE (n_obs = n_complete) AND (
        band1_mfs_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
        (band1_mfs_state = '') IS NOT FALSE
    );
"""

COMPLETE_TILES_MFS_BAND_2 = """
    SELECT tile, obs, band, band2_mfs_state FROM
        (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band2_mfs_state FROM
            (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN mfs_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                (SELECT tile, observation.name, observation.band, mfs_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                WHERE band=2)
        GROUP BY tile, band) t1
        LEFT JOIN "tile" t2 USING (tile))
    WHERE (n_obs = n_complete) AND (
        band2_mfs_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
        (band2_mfs_state = '') IS NOT FALSE
    );
"""


MAX_JOBS = 10


async def mosaic_completed_tiles(*args, **kwargs):
    """Manually trigger mosaicking jobs.
    1. Query observations to identify those with their MFS/cube processing completed
    2. Find tiles with components in ^
    3. Submit mosaicking workflow where a new observation completes an unprocessed tile.

    """
    command_args = optparse.OptionParser()
    command_args.add_option('-c', dest="config", default="./possum.ini")
    options, _ = command_args.parse_args()
    parser = configparser.ConfigParser()
    parser.read(options.config)

    d_sec = parser['Database']
    d_dsn = {'host': d_sec['host'],
             'port': d_sec['port'],
             'user': d_sec['user'],
             'password': d_sec['password'],
             'database': d_sec['database']}

    r_dsn = parser['RabbitMQ']['dsn']
    main = parser['Pipeline']['main']
    mfs = parser['Pipeline']['mfs']
    mosaic = parser['Pipeline']['mosaic']
    username = parser['Pipeline']['username']

    # Setup
    logger.info('Setting up connections to RabbitMQ and database')
    d_conn = await asyncpg.connect(dsn=None, **d_dsn)
    r_conn = await connect_robust(r_dsn)

    # Exchanges and queues
    channel = await r_conn.channel()
    await channel.set_qos(prefetch_count=1)

    # Create exchange to workflows
    workflow_exchange = await channel.declare_exchange(
        "aussrc.workflow.submit",
        ExchangeType.DIRECT,
        durable=True)

    # Create exchange to casda
    casda_exchange = await channel.declare_exchange(
        "aussrc.casda",
        ExchangeType.FANOUT,
        durable=True)

    casda_queue = await channel.declare_queue(name='aussrc.casda.possum', durable=True)
    await casda_queue.bind(casda_exchange)

    state_exchange = await channel.declare_exchange(
        "aussrc.workflow.state",
        ExchangeType.FANOUT,
        durable=True)

    state_queue = await channel.declare_queue(name='aussrc.workflow.state.possum', durable=True)
    await state_queue.bind(state_exchange)

    # Job
    try:
        async with d_conn.transaction():
            await d_conn.execute('SET search_path TO possum;')

            # process complete tiles
            complete_band1_tiles = await d_conn.fetch(COMPLETE_TILES_BAND_1)
            complete_band2_tiles = await d_conn.fetch(COMPLETE_TILES_BAND_2)
            logging.info(f'Incomplete band 1 tiles: {complete_band1_tiles}')
            logging.info(f'Incomplete band 2 tiles: {complete_band2_tiles}')
            complete_tiles = complete_band1_tiles + complete_band2_tiles
            if len(complete_tiles) == 0:
                logging.info('No spectral cube tiles to mosaic')
            for idx, r in enumerate(complete_tiles):
                if idx > MAX_JOBS:
                    logging.info('Submitted max number of survey jobs to cluster. Exiting')
                    break

                tile_id = str(dict(r)['tile'])
                obs_ids = str(dict(r)['obs'].replace('WALLABY_', '').replace('EMU_', ''))
                band = int(dict(r)['band'])
                if (band not in [1, 2]):
                    raise Exception(f'Band value must be 1 or 2 [band={band}]')
                tile_params = {
                    'TILE_ID': tile_id,
                    'OBS_IDS': obs_ids,
                    'BAND': band
                }
                tile_params.update(kwargs)

                logging.info(f"Submitting mosaicking pipeline: {tile_params}")
                job_params = {
                    "pipeline_key": mosaic,
                    "username": username,
                    "params": tile_params
                }
                message = Message(
                    json.dumps(job_params).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT
                )
                await workflow_exchange.publish(
                    message, routing_key='aussrc.workflow.submit.pull'
                )

            # process mfs tiles
            mfs_band1_tiles = await d_conn.fetch(COMPLETE_TILES_MFS_BAND_1)
            mfs_band2_tiles = await d_conn.fetch(COMPLETE_TILES_MFS_BAND_2)
            logging.info(f'Incomplete mfs band 1 tiles: {mfs_band1_tiles}')
            logging.info(f'Incomplete mfs band 2 tiles: {mfs_band2_tiles}')
            mfs_tiles = mfs_band1_tiles + mfs_band2_tiles
            logging.info(f'Incomplete MFS tiles: {mfs_tiles}')
            for idx, r in enumerate(mfs_tiles):
                if idx > MAX_JOBS:
                    logging.info('Submitted max number of MFS jobs to cluster. Exiting')
                    break
                tile_id = str(dict(r)['tile'])
                obs_ids = str(dict(r)['obs'].replace('WALLABY_', '').replace('EMU_', ''))
                band = int(dict(r)['band'])
                if (band not in [1, 2]):
                    raise Exception(f'Band value must be 1 or 2 [band={band}]')
                tile_params = {
                    'TILE_ID': tile_id,
                    'OBS_IDS': obs_ids,
                    'BAND': band,
                    'SURVEY_COMPONENT': 'mfs'
                }
                tile_params.update(kwargs)

                logging.info(f"Submitting mosaicking pipeline: {tile_params}")
                job_params = {
                    "pipeline_key": mosaic,
                    "username": username,
                    "params": tile_params
                }
                message = Message(
                    json.dumps(job_params).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT
                )
                await workflow_exchange.publish(
                    message, routing_key='aussrc.workflow.submit.pull'
                )

    except Exception as e:
        logging.error(e)
        await d_conn.close()
        await r_conn.close()

    finally:
        logging.info('Completed successfully')
        await d_conn.close()
        await r_conn.close()


if __name__ == "__main__":
    asyncio.run(mosaic_completed_tiles())
