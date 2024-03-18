import sys
import asyncio
import optparse
import logging
import configparser

logger = logging.getLogger()
logger.setLevel(logging.INFO)
streamhdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
streamhdlr.setFormatter(formatter)
logger.addHandler(streamhdlr)

from .subscriber import Subscriber


async def main(loop):
    command_args = optparse.OptionParser()
    command_args.add_option('-c', dest="config", default="./possum.ini")
    command_args.add_option('-d', '--dry_run', dest="dry_run", action='store_true', default=False)

    options, arguments = command_args.parse_args()
    dry_run = options.dry_run
    parser = configparser.ConfigParser()
    parser.read(options.config)
    await loop.run_in_executor(None, parser.read, options.config)
    d_sec = parser['Database']
    host = d_sec['host']
    port = d_sec['port']
    user = d_sec['user']
    password = d_sec['password']
    database = d_sec['database']

    d_dsn = {'host': host,
             'port': port,
             'user': user,
             'password': password,
             'database': database}

    r_dsn = parser['RabbitMQ']['dsn']

    main = parser['Pipeline']['main']
    mfs = parser['Pipeline']['mfs']
    mosaic = parser['Pipeline']['mosaic']
    username = parser['Pipeline']['username']

    if dry_run:
        logging.info('Executing in dry run mode (no database updates or message ack)')

    sub = Subscriber()
    await sub.setup(d_dsn, r_dsn, username, main, mfs, mosaic, loop, dry_run)
    await sub.consume()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    logger.info("Waiting on queue")
    loop.run_forever()
