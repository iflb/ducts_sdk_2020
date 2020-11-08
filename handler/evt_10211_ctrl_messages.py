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
        if not event.data:
            return None
        pubkey = 'PUBSUB/STREAM/MESSAGE'
        streamkey = 'VIEW/STREAM/MESSAGES'
        await event.session.redis.xadd_and_publish(pubkey, streamkey, **event.data)

