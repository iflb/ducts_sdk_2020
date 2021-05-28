#!/usr/bin/env python

from pathlib import Path

import asyncio

from ducts_client import *

from ifconf import configure_main

import logging
logger = logging.getLogger(__name__)

class MyPlayground:
    
    def __init__(self):
        self.duct = Duct()
        self.duct.connection_listener.onopen = self.on_open
        self.duct.connection_listener.onmessage = self.on_message
        self.duct.connection_listener.onerror = self.on_error

    async def add_video(self, group_key):
        return await self.add_resource(group_key, Path('/home/teppei/video.mp4'))
        
    async def add_test_resources(self, group_key):
        await self.add_resource(group_key, Path('./requirements.txt'))
        await self.add_resource(group_key, Path('./README.md'))
        await self.add_resource(group_key, Path('./iflab.png'))

    async def add_group(self, group_name):
        metadata = {'group_name': group_name}
        ret = await self.duct.call(self.duct.EVENT['BLOBS_GROUP_ADD'], [metadata])
        return ret
        
    async def add_resource(self, group_key, content_path):
        stat = content_path.lstat()
        metadata = {'content_name':content_path.name, 'last_modified': stat.st_mtime}
        if stat.st_size <= 1024**2 - 1024:
            return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_ADD'], [group_key, content_path.read_bytes(), metadata])
        buffer_key = await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_OPEN'], None)
        with open(content_path, 'rb', buffering=1024*512) as f:
            while True:
                buf = f.read(1024*512)
                if buf:
                    await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_APPEND'], [buffer_key, buf])
                else:
                    break
        ret = await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_ADD_BY_BUFFER'], [group_key, buffer_key, metadata])
        return ret
        
    async def handle_add_resources(self, rid, eid, data):
        print('resource added : {}'.format(data))

    async def on_open(self, event):
        print('ON_OPEN')
        self.duct.set_event_handler(self.duct.EVENT['BLOBS_CONTENT_ADD'], self.handle_add_resources)
        print('HANDLER_ADD')
        #await self.add_resource('test', Path('/home/teppei/video.mp4'))
        
    async def on_message(self, event):
        print("{}-{}-{}".format(event.rid, event.eid, event.data))
        
    async def on_error(self, event):
        print(event)
        
    async def open(self):
        await self.duct.open("http://localhost:8089/ducts/wsd")

    async def main(self):
        await self.open()
        group_key = await self.add_group('hogehoge')
        await self.add_test_resources(group_key)
        await self.add_video(group_key)

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


