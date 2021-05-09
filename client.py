#!/usr/bin/env python

import asyncio

from ducts_api import *

import logging
logger = logging.getLogger(__name__)

class MyPlayground:
    def __init__(self):
        self.duct = Duct()

    async def handle_model_event(self, rid, eid, data):
        print('message from [{}]:{}'.format(data['name'], data['message']))

    async def on_open(self, event):
        print('ON_OPEN')
        self.duct.set_event_handler(self.duct.EVENT['MODEL_MESSAGES'], self.handle_model_event)
        await self.duct.send(self.duct.next_rid(), self.duct.EVENT['MODEL_MESSAGES'], None)
        
    async def main(self):
        self.duct.connection_listener.onopen = self.on_open
        await self.duct.open("http://localhost:8089/ducts/wsd")
        
if __name__=="__main__":
    pg = MyPlayground()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(pg.main())
    try:
        loop.run_forever()
    except Exception as e:
        logger.exception('Error on loop: %s', e)
    except BaseException as e:
        logger.info(e)

