from ducts.spi import EventHandler

from datetime import datetime
import wave
from io import BytesIO

import logging
logger = logging.getLogger(__name__)

class Handler(EventHandler):

    def __init__(self):
        super().__init__()

    def setup(self, handler_spec, manager):
        handler_spec.set_description('Echo back a message as pcm format in dict')
        return handler_spec

    async def handle(self, event):
        wav = wave.open(BytesIO(event.data))
        return {'framerate':wav.getframerate(), 'data': wav.readframes(-1)}
