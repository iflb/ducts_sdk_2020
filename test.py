#!/usr/bin/env python

from pathlib import Path

import asyncio
import time

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

    async def add_and_update_video(self, group_key):
        await self.add_resource(group_key, Path('./video.mp4'))
        await self.update_resource_by_buffer(group_key, 'video.mp4', Path('./video2.mp4'))
        
    async def add_test_resources(self, group_key):
        await self.add_resource(group_key, Path('./requirements.txt'))
        await self.add_resource(group_key, Path('./README.md'))
        await self.add_resource(group_key, Path('./iflab.png'))
        
    async def update_test_resources(self, group_key):
        await self.update_resource(group_key, 'requirements.txt', 'hogehoge')
        await self.update_resource(group_key, 'requirements.txt', 'hogehogegegege')
        
    async def add_group(self, group_key):
        metadata = {'group_name': group_key, 'group_key':group_key}
        ret = await self.duct.call(self.duct.EVENT['BLOBS_GROUP_ADD'], [metadata])
        return ret
        
    async def add_resource(self, group_key, content_path):
        stat = content_path.lstat()
        metadata = {'content_key': '{}'.format(content_path.name), 'last_modified': stat.st_mtime}
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
        
    async def update_resource(self, group_key, content_key, body_str):
        return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_UPDATE'], [group_key, content_key, body_str])

    async def update_resource_by_buffer(self, group_key, content_key, content_path):
        buffer_key = await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_OPEN'], None)
        with open(content_path, 'rb', buffering=1024*512) as f:
            while True:
                buf = f.read(1024*512)
                if buf:
                    await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_APPEND'], [buffer_key, buf])
                else:
                    break
        ret = await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_UPDATE_BY_BUFFER'], [group_key, content_key, buffer_key])
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
        await self.duct.open("http://localhost:8080/ducts/wsd")

    async def main(self):
        await self.open()
        group_key_text = 'test'
        group_key = await self.add_group(group_key_text)
        await self.add_test_resources(group_key)
        await self.update_test_resources(group_key_text)
        await self.add_and_update_video(group_key)

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


