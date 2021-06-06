from ducts.spi import EventHandler

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('echo back test')
        return handler_spec

    async def handle(self, event):
        loop_count = int(event.data)
        ret = 0
        for i in range(loop_count):
            ret += i
            logger.info('*********************************{}'.format(ret))
            yield ret
        logger.info('*********************************DONE')
    
