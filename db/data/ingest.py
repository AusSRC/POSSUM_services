#!/usr/bin/env python3

import os
import sys
import glob
import csv
from argparse import ArgumentParser
from configparser import ConfigParser
import asyncio
import asyncpg


async def upsert_file(db_pool, file):
    """Insert all relevant data from the CSV files into the database.
    - Insert new tile if required
    - Insert entries for associated tile and field tile tables

    """
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            obs_name = os.path.basename(file).replace('-FULL', '').strip('.csv').rsplit('_', 1)[0]
            print(obs_name)
            with open(file) as csvfile:
                lines = csv.reader(csvfile, delimiter=',')
                next(lines)
                for row in lines:
                    tile_id = int(row[0])  # SBID is the first
                    crpix_ra = float(row[1])
                    crpix_dec = float(row[2])
                    ra = float(row[3])
                    dec = float(row[4])
                    print(tile_id, ra, dec)
                    tile = await conn.fetchrow('SELECT * FROM possum.tile WHERE tile=$1', tile_id)

                    # Create entry if does not exist
                    if not tile:
                        print(f'Creating new tile {tile_id}')
                        res = await conn.execute(
                            'INSERT INTO possum.tile (tile, ra_deg, dec_deg) VALUES ($1, $2, $3)',
                            tile_id, ra, dec
                        )

                    # Database entry for associated tile and field tile
                    res = await conn.execute(
                        'INSERT INTO possum.associated_tile (name, tile) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                        obs_name, tile_id
                    )
                    print(res)
                    res = await conn.execute(
                        'INSERT INTO possum.field_tile (name, tile) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                        obs_name, tile_id
                    )
                    print(res)
            print("\n")
    return


async def main(argv):
    argparser = ArgumentParser()
    argparser.add_argument('-c', '--config', default='./config.ini', required=False)
    argparser.add_argument('-f', '--files', required=True)
    args = argparser.parse_args(argv)
    assert os.path.exists(args.config), 'Provided config file does not exist'
    assert os.path.exists(args.files), 'File directory does not exist'
    config = ConfigParser()
    config.read(args.config)
    database = config['Database']
    dsn = {
        'host': database['host'],
        'port': database['port'],
        'user': database['user'],
        'password': database['password'],
        'database': database['database']
    }

    # Database connection
    db_pool = await asyncpg.create_pool(dsn=None, **dsn)
    csv_files = glob.glob(os.path.join(args.files, '*.csv'))
    tasks = []
    for f in csv_files:
        task = asyncio.create_task(upsert_file(db_pool, f))
        tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    await db_pool.close()


if __name__ == '__main__':
    argv = sys.argv[1:]
    asyncio.run(main(argv))
