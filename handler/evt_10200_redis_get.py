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
        redis_key, response_key = event.data
        value = await event.session.redis.execute_str('GET', redis_key)
        return {'key': response_key, 'value': value}
    
