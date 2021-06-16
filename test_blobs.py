#!/usr/bin/env python

# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import aiounittest

import warnings
#warnings.simplefilter('ignore')
warnings.resetwarnings()
import logging
logging.captureWarnings(True)

import sys
sys.path.append('..')
import time
from pathlib import Path
from collections import namedtuple

import asyncio

from ducts_client import *
from test import DuctsFileSystem, FileMetadata



class TestBlobsModule(aiounittest.AsyncTestCase):

    def asynctest(func):
        async def wrapper(*args, **kwargs):
            await TestBlobsModule.async_setup(args[0])
            try:
                await func(*args, **kwargs)
            finally:
                await TestBlobsModule.async_teardown(args[0])
        return wrapper

    GROUP_KEY = [
        'ducts.unittest.group.0'
        , 'ducts.unittest.group.1'
        ]
    
    CONTENT_KEY = [
        'requirements.txt'
        , 'README.md'
        , 'iflab.png'
        ]
    
    CONTENT_DIR_KEY = [
        'test.dir.0'
        , [
            'test.dir.0.0'
            , 'test.dir.0.1'
            , 'test.dir.0.2'
        ]
    ]
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def exception_handler(self, loop, context):
        pass

    async def async_setup(self):
        asyncio.get_event_loop().set_exception_handler(self.exception_handler)

        self.duct = DuctsFileSystem()
        await self.duct.open()
        for key in self.GROUP_KEY:
            if await self.duct.group_exists(key):
                #print(await self.duct.delete_group(key))
                await self.duct.delete_group(key)
        await self.duct.add_group(self.GROUP_KEY[0])
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path(self.CONTENT_KEY[0]))

    async def async_teardown(self):
        await self.duct.close()

    @asynctest
    async def test_get_group_metadata(self):
        ret = await self.duct.get_group_metadata(self.GROUP_KEY[0])
        #print (ret)
        expected = {'content_type': 'application/octet-stream', 'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'group_key_text': 'ducts.unittest.group.0'}
        for k,v in expected.items():
            self.assertEqual(ret[1][k], v)
        await self.duct.get_group_metadata('bc9810181d68f079c2553334b67bd6da13b5515e')
        with self.assertRaises(KeyError):
            await self.duct.get_group_metadata('hogehogehoge')
            
    @asynctest
    async def test_add_error(self):
        with self.assertRaises(KeyError):
            await self.duct.add_group(self.GROUP_KEY[0])

    @asynctest
    async def test_get_content_metadata(self):
        last_modified = int(Path(self.CONTENT_KEY[0]).lstat().st_mtime)
        ret = await self.duct.get_content_metadata(self.GROUP_KEY[0], self.CONTENT_KEY[0])
        expected = {'content_key': '19359a61ae2446b51b549167b014da2fcf265768', 'content_type': 'text/plain', 'last_modified': '{}'.format(last_modified), 'content_length': '115', 'cid': '6af5218610965df61fc0a62e3ca1a96b7be591af', 'order': '10'}
        for k,v in expected.items():
            self.assertEqual(ret[1][k], v)


    @asynctest
    async def test_contents_exists(self):
        self.assertTrue(await self.duct.content_exists(self.GROUP_KEY[0], self.CONTENT_KEY[0]))
        self.assertTrue(await self.duct.content_exists(self.GROUP_KEY[0], '19359a61ae2446b51b549167b014da2fcf265768'))
        self.assertTrue(await self.duct.content_exists('bc9810181d68f079c2553334b67bd6da13b5515e', self.CONTENT_KEY[0]))
        self.assertTrue(await self.duct.content_exists('bc9810181d68f079c2553334b67bd6da13b5515e', '19359a61ae2446b51b549167b014da2fcf265768'))
        self.assertFalse(await self.duct.content_exists(self.GROUP_KEY[0], 'NA'))
        self.assertFalse(await self.duct.content_exists('NA', self.CONTENT_KEY[0]))
        
    @asynctest
    async def test_add_and_update_video(self):
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('video.mp4'), abc = 123)
        await self.duct.update_content_by_buffer_from_file(self.GROUP_KEY[0], 'video.mp4', Path('./video2.mp4'))
        
    @asynctest
    async def test_add_contents(self):
        with self.assertRaises(KeyError):
            await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./requirements.txt'))
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./README.md'))
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./iflab.png'))
        
    @asynctest
    async def test_update_contents(self):
        ret = await self.duct.add_content(self.GROUP_KEY[0], b'abcdefg')
        await self.duct.update_content(self.GROUP_KEY[0], ret['content_key'], 'hogehoge')
        await self.duct.update_content(self.GROUP_KEY[0], ret['content_key'], 'hogehogegegege')
        
    @asynctest
    async def test_add_dir_wo_root(self):
        ret = await self.duct.add_content_dir(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0])
        self.assertEqual(ret, {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a'})
                         
        ret = await self.duct.get_content_metadata(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0])
        expected = {'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a', 'content_key_name': 'test.dir.0', 'content_type': 'application/json', 'is_dir':'1'}
        for k,v in expected.items():
            self.assertEqual(ret[1][k], v)

    @asynctest
    async def test_add_dir(self):
        root = await self.duct.add_content_dir(self.GROUP_KEY[0], '/')
        sub1 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub11 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub111 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub112 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub2 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub21 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub211 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        sub2111 = await self.duct.add_content_dir(self.GROUP_KEY[0])
        f = await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./README.md'))

        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], root['content_key'], files = [
            FileMetadata({'filename':'usr', 'content_key':sub1['content_key']})
            , FileMetadata({'filename':'var', 'content_key':sub2['content_key']})
        ])
        #print(ret)
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub1['content_key'], files = [
            FileMetadata({'filename':'local', 'content_key':sub11['content_key']})
        ])
        #print(ret)
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub11['content_key'], files = [
            FileMetadata({'filename':'lib', 'content_key':sub111['content_key']})
            , FileMetadata({'filename':'bin', 'content_key':sub112['content_key']})
        ])
        #print(ret)
        
        with self.assertRaises(ValueError):
            ret = await self.duct.add_dir_files(self.GROUP_KEY[0], root['content_key'], files = [
                FileMetadata({'filename':'var', 'content_key':sub2['content_key']})
            ])

        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub2['content_key'], files = [
            FileMetadata({'filename':'log', 'content_key':sub21['content_key']})
        ])
        #print(ret)
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub21['content_key'], files = [
            FileMetadata({'filename':'app', 'content_key':sub211['content_key']})
        ])
        #print(ret)
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub211['content_key'], files = [
            FileMetadata({'filename':'error', 'content_key':sub211['content_key']})
        ])
        #print(ret)
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], sub2111['content_key'], files = [
            FileMetadata({'filename':'some.txt', 'content_key':f['content_key']})
        ])
        #print(ret)


        self.assertTrue(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/'))
        self.assertTrue(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/usr/local'))
        self.assertTrue(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/usr/local/lib'))
        self.assertTrue(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/usr/local/bin'))
        self.assertFalse(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/usr/local/not_found'))
        self.assertFalse(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/var/log/app/error/some.txt'))
        self.assertFalse(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/var/log/error.log'))
        self.assertFalse(await self.duct.dir_file_exists(self.GROUP_KEY[0], '/hogehogexx'))
        with self.assertRaises(KeyError):
            await self.duct.dir_file_exists('not_exists', '/')
                         
    @asynctest
    async def test_add_dir_file(self):
        await self.duct.add_content_dir(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0])
        ret = await self.duct.add_dir_file(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], filename = 'mytestfile.txt', file_content_key = self.CONTENT_KEY[0])
        expected = {'.': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a', 'version': 'latest', 'is_dir': '1'}, 'mytestfile.txt': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '19359a61ae2446b51b549167b014da2fcf265768', 'version': 'latest', 'is_dir': '0'}}
        for k,v in expected.items():
            self.assertEqual(ret[k], v)
        with self.assertRaises(ValueError):
            await self.duct.add_dir_file(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], filename = 'mytestfile.txt', file_content_key = self.CONTENT_KEY[0])
        with self.assertRaises(ValueError):
            await self.duct.add_dir_file(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], filename = 'mytestfile.txt', file_content_key = self.CONTENT_KEY[1])
        
    @asynctest
    async def test_add_and_remove_dir_files(self):
        await self.duct.add_content_dir(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0])
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./README.md'))
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./iflab.png'))
        files = []
        for content in self.CONTENT_KEY:
            files.append(FileMetadata({'filename':content, 'content_key':content}))
        ret = await self.duct.add_dir_files(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], files = files)
        expected = {'requirements.txt': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '19359a61ae2446b51b549167b014da2fcf265768', 'version': 'latest', 'is_dir': '0'}, '.': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a', 'version': 'latest', 'is_dir': '1'}, 'iflab.png': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '9e4966344bec94a01b1bbcce5fe15b837859b957', 'version': 'latest', 'is_dir': '0'}, 'README.md': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '8ec9a00bfd09b3190ac6b22251dbb1aa95a0579d', 'version': 'latest', 'is_dir': '0'}}
        for k,v in expected.items():
            self.assertEqual(ret[k], v)
        self.assertEquals(ret, await self.duct.list_dir_files(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0]))

        ret = await self.duct.rm_dir_files(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], files = [self.CONTENT_KEY[0]])
        expected = {'.': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a', 'version': 'latest', 'is_dir': '1'}, 'iflab.png': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '9e4966344bec94a01b1bbcce5fe15b837859b957', 'version': 'latest', 'is_dir': '0'}, 'README.md': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '8ec9a00bfd09b3190ac6b22251dbb1aa95a0579d', 'version': 'latest', 'is_dir': '0'}}
        for k,v in expected.items():
            self.assertEqual(ret[k], v)
        ret = await self.duct.rm_dir_files(self.GROUP_KEY[0], self.CONTENT_DIR_KEY[0], files = [self.CONTENT_KEY[1], self.CONTENT_KEY[2]])
        expected = {'.': {'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'content_key': '10b3277eab37583d4ddb531bc469fbab2273ca4a', 'version': 'latest', 'is_dir': '1'}}
        for k,v in expected.items():
            self.assertEqual(ret[k], v)

    @asynctest
    async def test_get_content(self):
        ret = await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('video.mp4'))
        queue = await self.duct.get_content(**ret)
        self.assertTrue(isinstance(queue, asyncio.Queue))
        bio = BytesIO()
        while True:
            ret = await queue.get()
            if ret is None:
                break
            bio.write(ret)
        with open('video.mp4','rb') as f:
            self.assertEquals(bio.getvalue(), f.read())
        

    @asynctest
    async def test_ducts_message(self):
        msg = 'hello, world!'
        ret = await self.duct.duct.call(self.duct.duct.EVENT['DUCTS_TEST_MSG'], msg)
        self.assertEqual(msg, ret)
        
    @asynctest
    async def test_ducts_loop(self):
        count = 10
        queue = await self.duct.duct.call(self.duct.duct.EVENT['DUCTS_TEST_LOOP'], count)
        self.assertTrue(isinstance(queue, asyncio.Queue))
        it = iter(range(count))
        total = 0
        while True:
            val = await queue.get()
            if val is None:
                break
            total += next(it)
            self.assertEquals(val, total)
        
    @asynctest
    async def test_ducts_loop_bio(self):
        queue = await self.duct.duct.call(self.duct.duct.EVENT['DUCTS_TEST_LOOP_BIO'], None)
        self.assertTrue(isinstance(queue, asyncio.Queue))
        bio = BytesIO()
        while True:
            ret = await queue.get()
            if ret is None:
                break
            bio.write(ret)
        self.assertEquals(bio.getvalue(), b'0123456789'*1024*1024)
        
    @asynctest
    async def test_ducts_blob(self):
        ret = await self.duct.duct.call(self.duct.duct.EVENT['DUCTS_TEST_BLOB'], None)
        self.assertTrue(isinstance(ret, bytes))
        self.assertEquals(ret, b'0123456789'*1024*1024)
        
if __name__ == '__main__':
    unittest.main()

