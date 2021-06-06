from ducts.spi import EventHandler

from datetime import datetime
from io import BytesIO

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('echo back test')
        return handler_spec

    async def handle(self, event):
        print('*****************************BLOB_TEST*******************************************')
        return b'0123456789'*1024*1024
    
