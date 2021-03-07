from random import uniform, choice
from collections import deque

import asyncio
import aiofiles

from ifconf import configure_module, config_callback, configure_main
from ducts.redis import RedisClient

import logging
logger = logging.getLogger(__name__)

@config_callback()
def config(loader):
    loader.add_attr('pub_key', 'PUBSUB/STREAM/MESSAGE', help='key for message stream')
    loader.add_attr('stream_key', 'VIEW/STREAM/MESSAGES', help='key for message stream')
    loader.add_attr_int('stream_timeout', 3000, help='timeout[millisec] for message stream')
    loader.add_attr('bot_name', 'BOT', help='name of bot')
    loader.add_attr_list('bot_response', ['ごめんなさい、よくわかりません。', 'そうなんですね', 'すごいですね！', 'もう一回言ってください'], help='response list of bot')
    

class Bot(object):

    def __init__(self, loop):
        self.conf = configure_module(config)
        self.loop = loop

    async def run(self, loop):
        self.redis = RedisClient(loop)
        await self.redis.connect()
        last_id = '$'
        client_names = deque(maxlen=10)
        while True:
            ret = await self.redis.execute_str('XREAD', 'COUNT', 1, 'BLOCK', self.conf.stream_timeout, 'STREAMS', self.conf.stream_key, last_id)
            if ret is None:
                logger.info('BOT XREAD TIMEOUT CONTINUE...')
                continue
            key = ret[0][0]
            if key != self.conf.stream_key:
                logger.warn('UNEXPECTED STREAM_KEY=[%s]', key)
                continue
            for value in ret[0][1]:
                last_id = value[0]
                logger.info('ENTRY:%s', value[1])
                entry_dict = {v[0] : v[1] for v in zip(*[iter(value[1])]*2)}
                name = entry_dict['name']
                message = entry_dict['message']
                response = ''
                if name == self.conf.bot_name:
                    continue
                elif name not in client_names:
                    client_names.append(name)
                    response = '{}さんこんにちは！'.format(name)
                else:
                    response = choice(self.conf.bot_response+[message])
                await asyncio.sleep(uniform(0.5, 3.0))
                await self.redis.xadd_and_publish(self.conf.pub_key, self.conf.stream_key, 'name', self.conf.bot_name, 'message', response)
                    

def run():
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    bot = Bot(loop)
    try:
        loop.run_until_complete(bot.run(loop))
    except Exception as e:
        logger.exception('Error on loop: %s', e)
    except BaseException as e:
        logger.info(e)
    finally:
        loop.close()
        logger.info('Completed. See you!')

    
