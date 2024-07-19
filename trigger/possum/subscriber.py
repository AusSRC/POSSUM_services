import json
import asyncio
import logging
import asyncpg

from datetime import datetime
from dateutil import parser
from aio_pika import connect_robust, IncomingMessage, ExchangeType, Message, DeliveryMode
from asyncpg.exceptions import PostgresWarning


logger = logging.getLogger(__name__)


class Subscriber(object):
    CUBE_SUBMITTED = "SELECT COUNT(*) as count FROM possum.observation WHERE cube_state IN ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING')"
    MFS_SUBMITTED = "SELECT COUNT(*) as count FROM possum.observation WHERE mfs_state IN ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING')"
    TILE_SUBMITTED = "SELECT COUNT(*) as count FROM possum.tile WHERE " \
                     "band1_cube_state IN ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING') OR band2_cube_state IN ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING') OR " \
                     "band1_mfs_state in ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING') OR band2_mfs_state IN ('PENDING', 'SUBMITTED', 'QUEUED', 'RUNNING')"

    UPDATE_CUBE_SENT = "UPDATE possum.observation SET cube_sent=true, cube_state='SUBMITTED' WHERE sbid = any($1)"
    UPDATE_CUBE_STATE = 'UPDATE possum.observation SET cube_state=$1, cube_update=$2 WHERE sbid=$3'

    UPDATE_MFS_SENT = "UPDATE possum.observation SET mfs_sent=True, mfs_state='SUBMITTED' WHERE sbid = any($1)"
    UPDATE_MFS_STATE = 'UPDATE possum.observation SET mfs_state=$1, mfs_update=$2 WHERE sbid=$3'

    COMPLETE_TILES_BAND_1 = """
        SELECT tile, obs, band, band1_cube_state FROM
            (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band1_cube_state, t2.band1_cube_sent FROM
                (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN cube_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                    (SELECT tile, observation.name, observation.band, cube_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                    WHERE band=1)
            GROUP BY tile, band) t1
            LEFT JOIN "tile" t2 USING (tile))
        WHERE (n_obs = n_complete) AND (
            band1_cube_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
            band1_cube_state = '' IS NOT FALSE
        ) AND band1_cube_sent = false
        ORDER BY tile;
    """
    COMPLETE_TILES_BAND_2 = """
        SELECT tile, obs, band, band2_cube_state FROM
            (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band2_cube_state, t2.band2_cube_sent FROM
                (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN cube_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                    (SELECT tile, observation.name, observation.band, cube_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                    WHERE band=2)
            GROUP BY tile, band) t1
            LEFT JOIN "tile" t2 USING (tile))
        WHERE (n_obs = n_complete) AND (
            band2_cube_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
            (band2_cube_state = '') IS NOT FALSE
        ) AND band2_cube_sent = false
        ORDER BY tile;
    """
    COMPLETE_TILES_MFS_BAND_1 = """
        SELECT tile, obs, band, band1_mfs_state FROM
            (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band1_mfs_state, t2.band1_mfs_sent FROM
                (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN mfs_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                    (SELECT tile, observation.name, observation.band, mfs_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                    WHERE band=1)
            GROUP BY tile, band) t1
            LEFT JOIN "tile" t2 USING (tile))
        WHERE (n_obs = n_complete) AND (
            band1_mfs_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
            (band1_mfs_state = '') IS NOT FALSE
        ) AND band1_mfs_sent = false
        ORDER BY tile;
    """
    COMPLETE_TILES_MFS_BAND_2 = """
        SELECT tile, obs, band, band2_mfs_state FROM
            (SELECT t1.tile, t1.band, t1.n_obs, t1.n_complete, t1.obs, t2.band2_mfs_state, t2.band2_mfs_sent FROM
                (SELECT tile, band, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, SUM(CASE WHEN mfs_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM
                    (SELECT tile, observation.name, observation.band, mfs_state FROM associated_tile LEFT JOIN observation ON associated_tile.name = observation.name
                    WHERE band=2)
            GROUP BY tile, band) t1
            LEFT JOIN "tile" t2 USING (tile))
        WHERE (n_obs = n_complete) AND (
            band2_mfs_state NOT IN ('COMPLETED', 'SUBMITTED', 'QUEUED', 'RUNNING') OR
            (band2_mfs_state = '') IS NOT FALSE
        ) AND band2_mfs_sent = false
        ORDER BY tile;
    """
    UPDATE_BAND1_CUBE_SENT = "UPDATE possum.tile SET band1_cube_state='SUBMITTED', band1_cube_sent=true WHERE tile=$1"
    UPDATE_BAND2_CUBE_SENT = "UPDATE possum.tile SET band2_cube_state='SUBMITTED', band2_cube_sent=true WHERE tile=$1"

    UPDATE_BAND1_MFS_SENT = "UPDATE possum.tile SET band1_mfs_state='SUBMITTED', band1_mfs_sent=true WHERE tile=$1"
    UPDATE_BAND2_MFS_SENT = "UPDATE possum.tile SET band2_mfs_state='SUBMITTED', band2_mfs_sent=true WHERE tile=$1"


    JOB_SUBMIT_LIMIT = 3


    def __init__(self):
        self.d_dsn = None
        self.d_pool = None
        self.r_conn = None

        self.r_running = True
        self.r_task = None

        self.channel = None
        self.casda_queue = None

        self.casda_exchange = None
        self.workflow_exchange = None

        # key of the pipeline to submit to scheduler
        self.main = None
        self.mfs = None
        self.mosaic = None


    async def setup(self, d_dsn, r_dsn, username, main, mfs, mosaic, loop):
        logging.info('Running subscriber setup')
        self.loop = loop
        self.d_dsn = d_dsn
        self.d_pool = await asyncpg.create_pool(dsn=None, **d_dsn)
        self.r_conn = await connect_robust(r_dsn)

        # Pipeline key
        self.main = main
        self.mfs = mfs
        self.mosaic = mosaic
        self.username = username

        # Creating channel to exchange
        self.channel = await self.r_conn.channel()
        await self.channel.set_qos(prefetch_count=1)

        # Create exchange to workflows
        self.workflow_exchange = await self.channel.declare_exchange(
            "aussrc.workflow.submit",
            ExchangeType.DIRECT,
            durable=True)

        # CASDA exchange
        self.casda_exchange = await self.channel.declare_exchange(
            "aussrc.casda",
            ExchangeType.FANOUT,
            durable=True)

        self.casda_queue = await self.channel.declare_queue(name='aussrc.casda.possum', durable=True)
        await self.casda_queue.bind(self.casda_exchange)

        # State exchange
        self.state_exchange = await self.channel.declare_exchange(
            "aussrc.workflow.state",
            ExchangeType.FANOUT,
            durable=True)

        self.state_queue = await self.channel.declare_queue(name='aussrc.workflow.state.possum', durable=True)
        await self.state_queue.bind(self.state_exchange)

        self.r_task = asyncio.ensure_future(self._loop_send_to_queue())
        logging.info('Subscriber instantiated')


    async def _loop_send_to_queue(self):
        while self.r_running:
            try:
                await self._send_to_queue()
                await asyncio.sleep(30)
            except Exception as e:
                await asyncio.sleep(60)


    async def _mfs_send(self):
        d_conn = None
        try:
            d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
            async with d_conn.transaction():
                results = await d_conn.fetch(Subscriber.MFS_SUBMITTED)
                logging.info(f'mfs_send: {results}')
                count = int(results[0]['count'])
                if count >= Subscriber.JOB_SUBMIT_LIMIT:
                    return

                limit = Subscriber.JOB_SUBMIT_LIMIT - count
                UNSCHEDULED_MFS = f"""SELECT sbid FROM possum.observation WHERE sbid IS NOT NULL AND
                                      validated_state in ('GOOD', 'UNCERTAIN') AND mfs_sent=false order by sbid LIMIT {limit}"""

                # Get observations that we have not sent
                results = await d_conn.fetch(UNSCHEDULED_MFS)
                logging.info(f'mfs_send: {results}')
                if len(results) <= 0:
                    return

                sbid_list = [r['sbid'] for r in results]
                logger.info(f'mfs_send: Sending mfs pipeline(s) to workflow queue: {len(sbid_list)}')

                # Send diffuse out to workflow scheduler
                for sbid in sbid_list:
                    logging.info(f"Submitting mfs pipeline: {self.mfs}, sbid: {sbid}")
                    params = {
                        "pipeline_key": self.mfs,
                        "username": self.username,
                        "params": {"SBID": sbid}
                    }
                    message = Message(
                            json.dumps(params).encode(),
                            delivery_mode=DeliveryMode.PERSISTENT)

                    # Sending the message
                    await self.workflow_exchange.publish(message, routing_key='aussrc.workflow.submit.pull')

                # update diffuse have been sent
                await d_conn.execute(Subscriber.UPDATE_MFS_SENT, sbid_list)

        except Exception as e:
            logger.error("_mfs_send: ", exc_info=True)
            raise

        finally:
            if d_conn:
                try:
                    await d_conn.close()
                except:
                    pass


    async def _cube_send(self):
        d_conn = None
        try:
            d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
            async with d_conn.transaction():
                results = await d_conn.fetch(Subscriber.CUBE_SUBMITTED)
                logging.info(f'cube_send: {results}')
                count = int(results[0]['count'])
                if count >= Subscriber.JOB_SUBMIT_LIMIT:
                    return

                limit = Subscriber.JOB_SUBMIT_LIMIT - count
                UNSCHEDULED_CUBE = f"""SELECT sbid FROM possum.observation WHERE sbid IS NOT NULL
                                       AND validated_state in ('GOOD', 'UNCERTAIN') AND cube_sent=false order by sbid LIMIT {limit}"""

                # Get observations that we have not sent
                results = await d_conn.fetch(UNSCHEDULED_CUBE)
                logging.info(f'cube_send: {results}')
                if len(results) <= 0:
                    return

                sbid_list = [r['sbid'] for r in results]
                logger.info(f'cube_send: Sending cube pipeline(s) to workflow queue: {len(sbid_list)}')

                # Send regions out to workflow scheduler
                for sbid in sbid_list:
                    logging.info(f"Submitting cube pipeline: {self.main}, SBID: {sbid}")
                    params = {
                        "pipeline_key": self.main,
                        "username": self.username,
                        "params": {"SBID": sbid}
                    }
                    message = Message(
                            json.dumps(params).encode(),
                            delivery_mode=DeliveryMode.PERSISTENT)

                    # Sending the message
                    await self.workflow_exchange.publish(message, routing_key='aussrc.workflow.submit.pull')

                # update regions have been sent
                await d_conn.execute(Subscriber.UPDATE_CUBE_SENT, sbid_list)

        except Exception as e:
            logger.error("_cube_send: ", exc_info=True)
            raise

        finally:
            if d_conn:
                try:
                    await d_conn.close()
                except:
                    pass


    async def _mosaic_check_and_submit(self, d_conn, fetch_query, update_query, component):
        """Check existing mosaicking job count. Submit job for band and cube type.

        """
        # check count
        results = await d_conn.fetchrow(Subscriber.TILE_SUBMITTED)
        count = int(dict(results)['count'])
        logging.info(f'_mosaic_send: Existing mosaicking jobs: {count}')
        if count >= Subscriber.JOB_SUBMIT_LIMIT:
            logging.info('_mosaic_send: job limit reached')
            return

        # submit jobs
        limit = Subscriber.JOB_SUBMIT_LIMIT - count
        tiles = await d_conn.fetch(fetch_query)
        tiles = tiles[:limit]
        logging.info(f'_mosaic_send: {tiles}')
        for t in tiles:
            tile = str(dict(t)['tile'])
            params = {
                'TILE_ID': tile,
                'OBS_IDS': str(dict(t)['obs'].replace('WALLABY_', '').replace('EMU_', '')),
                'BAND': int(dict(t)['band']),
                'SURVEY_COMPONENT': component
            }
            logging.info(f'_mosaic_send: Submitting cube mosaicking pipeline for {params}')
            job_params = {
                "pipeline_key": self.mosaic,
                "username": self.username,
                "params": params
            }
            message = Message(
                json.dumps(job_params).encode(),
                delivery_mode=DeliveryMode.PERSISTENT
            )
            await self.workflow_exchange.publish(message, routing_key='aussrc.workflow.submit.pull')
            await d_conn.execute(update_query, int(tile))


    async def _mosaic_send(self):
        d_conn = None
        try:
            d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
            await d_conn.execute('SET search_path TO possum;')
            async with d_conn.transaction():
                await self._mosaic_check_and_submit(d_conn, Subscriber.COMPLETE_TILES_MFS_BAND_1, Subscriber.UPDATE_BAND1_MFS_SENT, 'mfs')
                await self._mosaic_check_and_submit(d_conn, Subscriber.COMPLETE_TILES_MFS_BAND_2, Subscriber.UPDATE_BAND2_MFS_SENT, 'mfs')
                await self._mosaic_check_and_submit(d_conn, Subscriber.COMPLETE_TILES_BAND_1, Subscriber.UPDATE_BAND1_CUBE_SENT, 'survey')
                await self._mosaic_check_and_submit(d_conn, Subscriber.COMPLETE_TILES_BAND_2, Subscriber.UPDATE_BAND2_CUBE_SENT, 'survey')

        except Exception as e:
            logger.info('_mosaic_send: ', exc_info=True)
            raise

        finally:
            if d_conn:
                try:
                    await d_conn.close()
                except:
                    pass


    async def _send_to_queue(self):
        """Periodically submitting workflow jobs

        """
        await self._cube_send()
        await self._mfs_send()
        await self._mosaic_send()


    async def consume(self):
        """Updating database state in response to messages

        """
        self.loop.create_task(self.state_queue.consume(self.on_state_message, no_ack=False))
        self.loop.create_task(self.casda_queue.consume(self.on_casda_message, no_ack=False))


    async def on_state_message(self, message: IncomingMessage):
        try:
            body = json.loads(message.body)
            params = body.get('params', 'null')
            if params == 'null':
                return

            if body['repository'] == 'https://github.com/AusSRC/POSSUM_workflow' and body['main_script'] == 'mfs.nf':
                logging.info(f'POSSUM mfs.nf state change message: {params}')
                params = json.loads(params)
                sbid = params.get('SBID', None)
                if not sbid:
                    logging.error(f'sbid parameter does not exist for pipeline id: {body["pipeline_id"]}')
                    return

                if isinstance(sbid, str):
                    sbid = sbid.replace('"', '')

                logging.info(f"on_state_message [mfs]: Updating pipeline details: {sbid}, state: {body['state']}")

                # Update state
                d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                async with d_conn.transaction():
                    await d_conn.execute(Subscriber.UPDATE_MFS_STATE,
                                        body['state'],
                                        parser.parse(body['updated']),
                                        sbid)

            elif body['repository'] == 'https://github.com/AusSRC/POSSUM_workflow' and body['main_script'] == 'main.nf':
                logging.info(f'POSSUM main.nf state change message: {params}')
                params = json.loads(params)
                sbid = params.get('SBID', None)
                if not sbid:
                    logging.error(f'sbid parameter does not exist for pipeline id: {body["pipeline_id"]}')
                    return

                if isinstance(sbid, str):
                    sbid = sbid.replace('"', '')

                logging.info(f"on_state_message [main]: Updating pipeline details: {sbid}, state: {body['state']}")

                # Update state
                d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                async with d_conn.transaction():
                    await d_conn.execute(
                        Subscriber.UPDATE_CUBE_STATE,
                        body['state'],
                        parser.parse(body['updated']),
                        sbid
                    )

            elif body['repository'] == 'https://github.com/AusSRC/POSSUM_workflow' and body['main_script'] == 'mosaic.nf':
                state = body['state']
                params = json.loads(params)
                survey_component = params.get('SURVEY_COMPONENT', 'survey')
                tile_id = params.get('TILE_ID', None)
                if isinstance(tile_id, str):
                    tile_id = int(tile_id)
                band = params.get('BAND', None)
                if not tile_id or not band:
                    logging.error(f'Parameters {dict(params)} invalid for mosaicking pipeline id: {body["pipeline_id"]}')
                    return

                # cube
                if survey_component == 'survey':
                    logging.info(f'on_state_message [mosaic]: updating POSSUM MFS tile {tile_id} band {band} with state={state}')
                    if band == 1:
                        d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                        await d_conn.execute('UPDATE possum.tile SET band1_cube_state=$1 WHERE tile=$2;',
                            state, tile_id
                        )
                    elif band == 2:
                        d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                        await d_conn.execute(
                            'UPDATE possum.tile SET band2_cube_state=$1 WHERE tile=$2;',
                            state, tile_id
                        )
                # mfs
                elif survey_component == 'mfs':
                    logging.info(f'on_state_message [mosaic]: updating POSSUM cube tile {tile_id} band {band} with state={state}')
                    if band == 1:
                        d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                        await d_conn.execute(
                            'UPDATE possum.tile SET band1_mfs_state=$1 WHERE tile=$2;',
                            state, tile_id
                        )
                    elif band == 2:
                        d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                        await d_conn.execute(
                            'UPDATE possum.tile SET band2_mfs_state=$1 WHERE tile=$2;',
                            state, tile_id
                        )
                else:
                    logging.error(f'Unexpected survey component parameter {survey_component}')
                    return

            await message.ack()

        except PostgresWarning:
            logger.error("on_state_message", exc_info=True)
            await message.nack()
            await asyncio.sleep(30)
            if self.d_pool:
                await self.d_pool.expire_connections()
            return

        except Exception as e:
            logger.error("on_state_message", exc_info=True)
            await message.nack()
            await asyncio.sleep(5)
            if self.d_pool:
                await self.d_pool.expire_connections()
            return


    def extract_name(self, filename):
        if 'meanMap' in filename:
            return None
        if 'componentMap_image' in filename:
            return None
        if 'componentResidual_image' in filename:
            return None
        if 'selavy-image' in filename:
            return None
        if 'image' not in filename:
            return None

        index = filename.find("WALLABY")
        if index == -1:
            index = filename.find("EMU")
            if index == -1:
                return None

        name = filename[index:]
        name = name.split('.')
        return name[0]


    async def on_casda_message(self, message: IncomingMessage):
        try:
            body = json.loads(message.body)

            # Only interested in POSSUM project code
            if body['project_code'] not in ['AS203']:
                await message.ack()
                return

            for f, _, _, quality in body['files']:
                name = self.extract_name(f)
                if name is None:
                    continue

                if f.startswith('image.restored.i.') and f.endswith('.contcube.conv.fits'):
                    logger.info(f"Match. Field Name: {name}, "
                                f"SBID: {body['sbid']}, "
                                f"Event Type: {body['event_type']}, "
                                f"Event Date: {body['event_date']}, "
                                f"Quality: {quality}, "
                                f"Filename: {f}")

                    event_date = datetime.fromisoformat(body['event_date'])
                    obs_start = datetime.fromisoformat(body['obs_start'])
                    event_type = body['event_type']
                    sbid = body['sbid']

                    # clean the observation entry
                    if event_type in ['REJECTED']:
                        async with self.d_pool.acquire() as conn:
                            async with conn.transaction():
                                await conn.execute("""
                                                   UPDATE possum.observation SET
                                                   sbid=null,
                                                   obs_start=null,
                                                   processed_date=null,
                                                   validated_date=null,
                                                   validated_state=$1,
                                                   mfs_state=null,
                                                   mfs_update=null,
                                                   mfs_sent=false,
                                                   cube_state=null,
                                                   cube_update=null,
                                                   cube_sent=false
                                                   WHERE name=$2
                                                   """,
                                                   quality,
                                                   name)

                    elif event_type in ['DEPOSITED']:
                        async with self.d_pool.acquire() as conn:
                            async with conn.transaction():
                                await conn.execute("""
                                                    UPDATE possum.observation SET
                                                    sbid=$1,
                                                    obs_start=$2,
                                                    processed_date=$3,
                                                    validated_state=$4
                                                    WHERE name=$5
                                                    """,
                                                    sbid,
                                                    obs_start,
                                                    event_date,
                                                    quality,
                                                    name)

                    elif event_type in ['RELEASED', 'VALIDATED']:
                        async with self.d_pool.acquire() as conn:
                            async with conn.transaction():
                                logging.info(f'Updated state for observation {sbid} with quality level {quality}')
                                await conn.execute("""
                                                    UPDATE possum.observation SET
                                                    sbid=$1,
                                                    obs_start=$2,
                                                    validated_date=$3,
                                                    validated_state=$4
                                                    WHERE name=$5
                                                    """,
                                                    sbid,
                                                    obs_start,
                                                    event_date,
                                                    quality,
                                                    name)

            await message.ack()

        except PostgresWarning:
            logger.error("on_casda_message", exc_info=True)
            await message.nack()
            await asyncio.sleep(30)
            if self.d_pool:
                await self.d_pool.expire_connections()
            return

        except Exception as e:
            logger.error("on_casda_message", exc_info=True)
            await message.nack()
            await asyncio.sleep(5)
            if self.d_pool:
                await self.d_pool.expire_connections()
            return
