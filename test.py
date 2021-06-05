#!/usr/bin/env python

from pathlib import Path

import asyncio
import time

from ducts_client import *

from ifconf import configure_main

import logging
logger = logging.getLogger(__name__)

class DuctsFileSystem:
    
    def __init__(self):
        self.duct = Duct()
        self.duct.connection_listener.onopen = self.on_open
        self.duct.connection_listener.onmessage = self.on_message
        self.duct.connection_listener.onerror = self.on_error

    async def open(self, wsd_url = "http://localhost:8080/ducts/wsd"):
        await self.duct.open(wsd_url)

    async def on_open(self, event):
        print('ON_OPEN')
        self.duct.set_event_handler(self.duct.EVENT['BLOBS_CONTENT_ADD'], self.handle_content_add)
        print('HANDLER_ADD')
        
    async def on_message(self, event):
        print("{}-{}-{}".format(event.rid, event.eid, event.data))
        
    async def on_error(self, event):
        print('ONERROR|EVENT={}|SOURCE={}'.format(event, event.source))

    async def add_group(self, group_key):
        metadata = {'group_key': group_key}
        ret = await self.duct.call(self.duct.EVENT['BLOBS_GROUP_ADD'], metadata)
        return ret
        
    async def get_group_metadata(self, group_key):
        ret = await self.duct.call(self.duct.EVENT['BLOBS_GROUP_METADATA'], group_key)
        return ret

    async def group_exists(self, group_key):
        return await self.duct.call(self.duct.EVENT['BLOBS_GROUP_EXISTS'], group_key)

    async def delete_group(self, group_key):
        return await self.duct.call(self.duct.EVENT['BLOBS_GROUP_DELETE'], group_key)

    async def add_content(self, group_key: str, content: bytes, metadata: dict = {}):
        param = metadata.copy()
        param['group_key'] = group_key
        param['content'] = content
        return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_ADD'], param)

    async def add_content_from_file(self, group_key: str, content_path: Path, metadata: dict = {}):
        param = metadata.copy()
        param['group_key'] = group_key
        
        stat = content_path.lstat()
        if 'content_key' not in param:
            param['content_key'] = content_path.name
        param['last_modified'] = stat.st_mtime
        if stat.st_size <= 1024**2 - 1024:
            param['content'] = content_path.read_bytes()
            return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_ADD'], param)
        
        buffer_key = await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_OPEN'], None)
        with open(content_path, 'rb', buffering=1024*512) as f:
            while True:
                buf = f.read(1024*512)
                if buf:
                    await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_APPEND'], [buffer_key, buf])
                else:
                    break
        param['buffer_key'] = buffer_key
        ret = await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_ADD_BY_BUFFER'], param)
        return ret

    async def update_content(self, group_key = '', content_key = '', content = b'', **otherparams):
        param = otherparams.copy()
        param['group_key'] = group_key
        param['content_key'] = content_key
        param['content'] = content
        return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_UPDATE'], param)
        
    async def get_content_metadata(self, group_key, content_key):
        param = {}
        param['group_key'] = group_key
        param['content_key'] = content_key
        return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_METADATA'], param)

    async def content_exists(self, group_key, content_key):
        param = {}
        param['group_key'] = group_key
        param['content_key'] = content_key
        return await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_EXISTS'], param)

    async def update_content_by_buffer_from_file(self, group_key, content_key, content_path):
        buffer_key = await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_OPEN'], None)
        with open(content_path, 'rb', buffering=1024*512) as f:
            while True:
                buf = f.read(1024*512)
                if buf:
                    await self.duct.call(self.duct.EVENT['BLOBS_BUFFER_APPEND'], [buffer_key, buf])
                else:
                    break
        param = {}
        param['group_key'] = group_key
        param['content_key'] = content_key
        param['buffer_key'] = buffer_key
        ret = await self.duct.call(self.duct.EVENT['BLOBS_CONTENT_UPDATE_BY_BUFFER'], param)
        return ret

    async def delete_all(self):
        return await self.duct.call(self.duct.EVENT['BLOBS_DELETE_ALL'], "I'm crazy!")

    async def handle_content_add(self, rid, eid, data):
        print('resource added : {}'.format(data))

        
    async def main(self):
        await self.open()
        await self.delete_all()
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


