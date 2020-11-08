from ducts.spi import EventHandler

from datetime import datetime
import random

import asyncio

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('Second sample of Ducts Handler in Chapter.1')
        return handler_spec

    async def handle(self, event):
        request_id = event.session.request_id()
        count = random.randrange(5, 10)
        yield 'Hello! this is a response for {}. I will start the loop... for {} times.'.format(request_id, count)        
        for i in range(count):
            await asyncio.sleep(random.randrange(1, 5))
            yield '[{}] in the loop... {}/{}'.format(request_id, i, count)
        yield '{} is Done! Bye!'.format(request_id)
    
