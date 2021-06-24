from statistics import mean, median,variance,stdev
from time import time
from pathlib import *
import aioredis

blobs = [str(i).encode('UTF-8') * 1024 for i in range(10)]

def update_blobs(length = 1024):
    blobs.clear()
    for i in range(10):
        blobs.append(str(i).encode('UTF-8') * length)

def write_files():
    for i, blob in enumerate(blobs):
        with open('{}.dat'.format(i), 'wb') as f:
            f.write(blob)

async def connect(url = 'redis://localhost:6379/0?encoding=utf-8'):
    return await aioredis.create_redis_pool(url, minsize=1, maxsize=1)

async def write_redis(redis):
    for i, blob in enumerate(blobs):
        await redis.execute('SET', '{}.dat'.format(i), blob)
    
def timeit_write_files(count = 10):
    result = []
    for i in range(10):
        start = time()
        write_files()
        end = time()
        result.append(end - start)
    return result

async def timeit_write_redis(count = 10):
    result = []
    redis = await connect()
    for i in range(10):
        start = time()
        await write_redis(redis)
        end = time()
        result.append(end - start)
    redis.close()
    return result

def print_stat(data):
    print('mean :[{}]'.format(mean(data)))
    print('stdev:[{}]'.format(stdev(data)))








