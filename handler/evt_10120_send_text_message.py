from ducts.spi import EventHandler

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('Echo back a message')
        return handler_spec

    async def handle(self, event):
        name = event.data
        return 'Hello, {}!'.format(name)
    
