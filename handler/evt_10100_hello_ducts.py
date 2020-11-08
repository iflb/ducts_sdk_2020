from ducts.spi import EventHandler

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('First sample of Ducts Handler')
        return handler_spec

    async def handle(self, event):
        return 'Hello Ducts! its {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    
