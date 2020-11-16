from ducts.spi import EventHandler

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('Get Value from Redis Server')
        return handler_spec

    async def handle(self, event):
        subkey = 'PUBSUB/STREAM/MESSAGE'
        streamkey = 'VIEW/STREAM/MESSAGES'
        async for kv in event.session.redis.psub_and_xrange_str(subkey, streamkey, last_count = 5):
            yield kv

    async def handle_closed(self, event_session):
        subkey = 'PUBSUB/STREAM/MESSAGE'
        ch = (await event_session.redis.punsubscribe(subkey))
        logger.debug('PUNSUBSCRIBE|CHANNEL=%s', ch)
    

