#!/usr/bin/env python

# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import aiounittest


import sys
sys.path.append('..')
import time
from pathlib import Path
from collections import namedtuple

import asyncio

from ducts_client import *
from test import DuctsFileSystem

class TestBlobsModule(aiounittest.AsyncTestCase):

    GROUP_KEY = [
        'ducts.unittest.group.0'
        , 'ducts.unittest.group.1'
        ]
    
    CONTENT_KEY = [
        'requirements.txt'
        ]
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    async def setup(self):
        self.duct = DuctsFileSystem()
        await self.duct.open()
        for key in self.GROUP_KEY:
            if await self.duct.group_exists(key):
                print(await self.duct.delete_group(key))
        await self.duct.add_group(self.GROUP_KEY[0])
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path(self.CONTENT_KEY[0]))
        
    async def test_get_group_metadata(self):
        await self.setup()
        ret = await self.duct.get_group_metadata(self.GROUP_KEY[0])
        print (ret)
        expected = {'group_name': '', 'content_type': 'application/octet-stream', 'group_key': 'bc9810181d68f079c2553334b67bd6da13b5515e', 'group_key_text': 'ducts.unittest.group.0'}
        for k,v in expected.items():
            self.assertEqual(ret[1][k], v)
        await self.duct.get_group_metadata('bc9810181d68f079c2553334b67bd6da13b5515e')
        with self.assertRaises(KeyError):
            await self.duct.get_group_metadata('hogehogehoge')
            
    async def test_add_error(self):
        await self.setup()
        with self.assertRaises(KeyError):
            await self.duct.add_group(self.GROUP_KEY[0])

    async def test_get_content_metadata(self):
        await self.setup()
        last_modified = int(Path(self.CONTENT_KEY[0]).lstat().st_mtime)
        ret = await self.duct.get_content_metadata(self.GROUP_KEY[0], self.CONTENT_KEY[0])
        expected = {'content_key': '19359a61ae2446b51b549167b014da2fcf265768', 'content_key_name': 'requirements.txt', 'content_type': 'text/plain', 'last_modified': '{}'.format(last_modified), 'content_length': '98', 'cid': '1947e0ab255b09794ef17871e44e720677d8895e', 'order': '10'}
        for k,v in expected.items():
            self.assertEqual(ret[1][k], v)


    async def test_contents_exists(self):
        await self.setup()
        self.assertTrue(await self.duct.content_exists(self.GROUP_KEY[0], self.CONTENT_KEY[0]))
        self.assertTrue(await self.duct.content_exists(self.GROUP_KEY[0], '19359a61ae2446b51b549167b014da2fcf265768'))
        self.assertTrue(await self.duct.content_exists('bc9810181d68f079c2553334b67bd6da13b5515e', self.CONTENT_KEY[0]))
        self.assertTrue(await self.duct.content_exists('bc9810181d68f079c2553334b67bd6da13b5515e', '19359a61ae2446b51b549167b014da2fcf265768'))
        self.assertFalse(await self.duct.content_exists(self.GROUP_KEY[0], 'NA'))
        self.assertFalse(await self.duct.content_exists('NA', self.CONTENT_KEY[0]))
        
    async def test_add_and_update_video(self):
        await self.setup()
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('video.mp4'), {'abc':123})
        await self.duct.update_content_by_buffer_from_file(self.GROUP_KEY[0], 'video.mp4', Path('./video2.mp4'))
        
    async def test_add_contents(self):
        await self.setup()
        with self.assertRaises(KeyError):
            await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./requirements.txt'))
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./README.md'))
        await self.duct.add_content_from_file(self.GROUP_KEY[0], Path('./iflab.png'))
        
    async def test_update_contents(self):
        await self.setup()
        group_key, content_key = await self.duct.add_content(self.GROUP_KEY[0], b'abcdefg')
        await self.duct.update_content(self.GROUP_KEY[0], content_key, 'hogehoge')
        await self.duct.update_content(self.GROUP_KEY[0], content_key, 'hogehogegegege')
        
            
if __name__ == '__main__':
    unittest.main()

