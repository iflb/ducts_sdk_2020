from ducts.spi import EventHandler

from datetime import datetime

import asyncio

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('Send back a dict message')
        return handler_spec

    async def handle(self, event):
        name = event.data['name']
        message = event.data['message']
        yield {'speaker': 'ducts', 'message': 'Hello {}!'.format(name)}
        await asyncio.sleep(0.5)
        yield {'speaker': 'ducts', 'message': "I'm DUCTS server!"}
        await asyncio.sleep(2)
        yield {'speaker': 'you', 'message': message}
        await asyncio.sleep(2)
        yield {'speaker': 'ducts', 'message': "Thank you!"}
        yield {'speaker': 'ducts', 'message': "Bye!"}

