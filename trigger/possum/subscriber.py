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

    CUBE_SUBMITTED = "SELECT COUNT(*) as count FROM possum.observation WHERE cube_state IN ('SUBMITTED', 'QUEUED', 'RUNNING')"

    UPDATE_CUBE_SENT = "UPDATE possum.observation SET cube_sent=true, cube_state='SUBMITTED' WHERE sbid = any($1)"
    UPDATE_CUBE_STATE = 'UPDATE possum.observation SET cube_state=$1, cube_update=$2 WHERE sbid=$3'

    MFS_SUBMITTED = "SELECT COUNT(*) as count FROM possum.observation WHERE mfs_state IN ('SUBMITTED', 'QUEUED', 'RUNNING')"

    UPDATE_MFS_SENT = "UPDATE possum.observation SET mfs_sent=True, mfs_state='SUBMITTED' WHERE sbid = any($1)"
    UPDATE_MFS_STATE = 'UPDATE possum.observation SET mfs_state=$1, mfs_update=$2 WHERE sbid=$3'


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


    async def setup(self, d_dsn, r_dsn, username, main, mfs, loop):
        self.d_dsn = d_dsn
        # Perform db connection
        self.d_pool = await asyncpg.create_pool(dsn=None, **d_dsn)
        # Perform rabbitmq connection
        self.r_conn = await connect_robust(r_dsn)
        # Pipeline key
        self.main = main
        self.mfs = mfs
        self.username = username

        self.loop = loop

        # Creating channel to exchange
        self.channel = await self.r_conn.channel()
        await self.channel.set_qos(prefetch_count=1)

        # Create exchange to workflows
        self.workflow_exchange = await self.channel.declare_exchange(
            "aussrc.workflow.submit",
            ExchangeType.DIRECT,
            durable=True)

        # Create exchange to casda
        self.casda_exchange = await self.channel.declare_exchange(
            "aussrc.casda",
            ExchangeType.FANOUT,
            durable=True)

        # Declaring casda possum queue
        self.casda_queue = await self.channel.declare_queue(name='aussrc.casda.possum',
                                                            durable=True)

        ###################### State Exchange ##################
        self.state_exchange = await self.channel.declare_exchange(
            "aussrc.workflow.state", 
            ExchangeType.FANOUT, 
            durable=True)


        self.state_queue = await self.channel.declare_queue(name='aussrc.workflow.state.possum', 
                                                            durable=True)

        await self.state_queue.bind(self.state_exchange)
        #########################################################


        self.r_task = asyncio.ensure_future(self._loop_send_to_queue())

        # Binding the queue to the exchange
        await self.casda_queue.bind(self.casda_exchange)


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
                count = int(results[0]['count'])
                if count >= 3:
                    return

                limit = 3 - count
                UNSCHEDULED_MFS = f"""SELECT sbid FROM possum.observation WHERE sbid IS NOT NULL AND 
                                      validated_state='ACCEPTED' AND mfs_sent=false order by sbid LIMIT {limit}"""

                # Get observations that we have not sent
                results = await d_conn.fetch(UNSCHEDULED_MFS)
                if len(results) <= 0:
                    return

                sbid_list = [r['sbid'] for r in results]

                logger.info(f'Sending mfs pipeline(s) to workflow queue: {len(sbid_list)}')

                # Send diffuse out to workflow scheduler
                for sbid in sbid_list:
                    params = {"pipeline_key": self.mfs,
                              "username": self.username,
                              "params": {"SBID": sbid}}

                    message = Message(
                            json.dumps(params).encode(),
                            delivery_mode=DeliveryMode.PERSISTENT)

                    logging.info(f"Submitting mfs pipeline: {self.mfs}, sbid: {sbid}")

                    # Sending the message
                    await self.workflow_exchange.publish(message, 
                                                        routing_key='aussrc.workflow.submit.pull')

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
                count = int(results[0]['count'])
                if count >= 3:
                    return

                limit = 3 - count
                UNSCHEDULED_CUBE = f"""SELECT sbid FROM possum.observation WHERE sbid IS NOT NULL 
                                       AND validated_state='ACCEPTED' AND cube_sent=false order by sbid LIMIT {limit}"""

                # Get observations that we have not sent
                results = await d_conn.fetch(UNSCHEDULED_CUBE)
                if len(results) <= 0:
                    return

                sbid_list = [r['sbid'] for r in results]

                logger.info(f'Sending cube pipeline(s) to workflow queue: {len(sbid_list)}')

                # Send regions out to workflow scheduler
                for sbid in sbid_list:
                    params = {"pipeline_key": self.main,
                              "username": self.username,
                              "params": {"SBID": sbid}}

                    message = Message(
                            json.dumps(params).encode(),
                            delivery_mode=DeliveryMode.PERSISTENT)

                    logging.info(f"Submitting cube pipeline: {self.main}, SBID: {sbid}")

                    # Sending the message
                    await self.workflow_exchange.publish(message, 
                                                        routing_key='aussrc.workflow.submit.pull')

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


    async def _send_to_queue(self):
        await self._cube_send()
        await self._mfs_send()


    async def consume(self):
        self.loop.create_task(self.state_queue.consume(self.on_state_message, no_ack=False))
        self.loop.create_task(self.casda_queue.consume(self.on_casda_message, no_ack=False))


    async def on_state_message(self, message: IncomingMessage):
        try:
            body = json.loads(message.body)

            params = body.get('params', 'null')
            if params == 'null':
                await message.ack()
                return

            if body['repository'] == 'https://github.com/AusSRC/POSSUM_workflow' and body['main_script'] == 'mfs.nf':
                params = json.loads(params)
                sbid = params.get('SBID', None)
                if not sbid:
                    logging.error(f'sbid parameter does not exist for pipeline id: {body["pipeline_id"]}')
                    await message.ack()
                    return

                logging.info(f"Updating pipeline details: {sbid}, state: {body['state']}")

                d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                async with d_conn.transaction():
                    await d_conn.execute(Subscriber.UPDATE_MFS_STATE, 
                                        body['state'], 
                                        parser.parse(body['updated']),
                                        int(sbid))
                    
            elif body['repository'] == 'https://github.com/AusSRC/POSSUM_workflow' and body['main_script'] == 'main.nf':
                params = json.loads(params)
                sbid = params.get('SBID', None)
                if not sbid:
                    logging.error(f'sbid parameter does not exist for pipeline id: {body["pipeline_id"]}')
                    await message.ack()
                    return

                logging.info(f"Updating pipeline details: {sbid}, state: {body['state']}")

                d_conn = await asyncpg.connect(dsn=None, **self.d_dsn)
                async with d_conn.transaction():
                    await d_conn.execute(Subscriber.UPDATE_CUBE_STATE, 
                                        body['state'], 
                                        parser.parse(body['updated']),
                                        int(sbid))

        finally:
            await message.ack()


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

            # Only interested in EMU, WALLABY, POSSUM project code
            if body['project_code'] not in ['AS203']:
                await message.ack()
                return

            for f, _, _ in body['files']:
                name = self.extract_name(f)
                if name is None:
                    continue

                logger.info(f"Match. Field Name: {name}, SBID: {body['sbid']}, Event ID: {body['event_id']}, Event Date: {body['event_date']}, Event Type: {body['event_type']}")

                obs_start = datetime.fromisoformat(body['obs_start'])
                validated_date = datetime.fromisoformat(body['event_date'])
                event_type = body['event_type']

                if event_type == 'VALIDATED' or event_type == 'RELEASED':
                    event_type = 'ACCEPTED'
                elif event_type == 'DEPOSITED':
                    event_type = None
                    validated_date = None

                async with self.d_pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute('UPDATE possum.observation SET sbid=$1, obs_start=$2, validated_date=$3, validated_state=$4 WHERE name=$5',
                                            int(body['sbid']),
                                            obs_start,
                                            validated_date,
                                            event_type,
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