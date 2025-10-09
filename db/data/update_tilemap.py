#!/usr/bin/env python3

import os
import sys
import glob
import csv
from argparse import ArgumentParser
from configparser import ConfigParser
import asyncio
import asyncpg


async def insert_tiles(conn, filename):
    """Insert tiles based on a .txt file (copied from the Google Sheet provided by Cameron, tab separated).

    """
    with open(filename, 'r') as tsv_file:
        lines = csv.reader(tsv_file, delimiter='\t')
        next(lines)
        tiles_insert = []
        for idx, row in enumerate(lines):
            tile_id = int(row[0])
            ra_deg = float(row[3])
            dec_deg = float(row[4])
            gl = float(row[5])
            gb = float(row[6])
            tiles_insert.append((tile_id, ra_deg, dec_deg, gl, gb))
    await conn.executemany(
        'INSERT INTO possum.tile (tile, ra_deg, dec_deg, gl, gb) VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING',
        tiles_insert
    )
    print('Inserted tiles')
    return


async def insert_tilemap(conn, filename, prefix):
    print(f'Insert into database for file {filename}')
    with open(filename) as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        next(lines)  # Header
        tile_maps = []
        for idx, row in enumerate(lines):
            values = list(filter(None, row))
            tile_id = int(values[0])
            obs_ids = [f'{prefix}_{v}' for v in values[1:]]
            for o in obs_ids:
                tile_maps.append((o, tile_id))
    await conn.executemany('INSERT INTO possum.associated_tile (name, tile) VALUES ($1, $2)', tile_maps)
    print(f'Insert file {filename} complete')
    return


async def main(argv):
    argparser = ArgumentParser()
    argparser.add_argument('-c', '--config', default='./config.ini', required=False)
    argparser.add_argument('-e', '--emu', help='EMU Tile-map .csv file', required=True)
    argparser.add_argument('-w', '--wallaby', help='WALLABY Tile-map .csv file', required=True)
    argparser.add_argument('-t', '--tiles', help='Tiles .tsv file', required=True)
    args = argparser.parse_args(argv)
    assert os.path.exists(args.config), 'Provided config file does not exist'
    assert os.path.exists(args.emu), 'Provided EMU tile-map file does not exist'
    assert os.path.exists(args.wallaby), 'Provided WALLABY tile-map file does not exist'
    assert os.path.exists(args.tiles), 'Provided tile file does not exist'

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
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            print('Clearing tables (associated_tile)')
            await conn.execute('TRUNCATE possum.associated_tile;')
            print('Resetting sequences')
            await conn.execute('ALTER sequence possum.associated_tile_id_seq RESTART WITH 1;')
            print('Tables cleared, sequences reset')

            # ingest all tiles (skip if exists)
            await insert_tiles(conn, args.tiles)

            # ingest for each table
            await insert_tilemap(conn, args.emu, prefix='EMU')
            await insert_tilemap(conn, args.wallaby, prefix='WALLABY')
            print('Complete')

    await db_pool.close()
    return


if __name__ == '__main__':
    argv = sys.argv[1:]
    asyncio.run(main(argv))
