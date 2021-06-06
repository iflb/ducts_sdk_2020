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
        bio = BytesIO()
        for i in range(1024):
            bio.write(b'0123456789'*1024)
        bio.seek(0)
        for buf in iter(lambda: bio.read(2000), b''):
            yield buf
    
