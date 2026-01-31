# Test file for CS003 - Blocking Call in Async Function

import asyncio
import time
import requests


async def bad_sleep():
    time.sleep(1)  # CS003 - blocking sleep in async
    return "done"


async def bad_request():
    response = requests.get("https://api.example.com")  # CS003 - blocking HTTP
    return response.json()


async def bad_request_post():
    response = requests.post("https://api.example.com", json={})  # CS003
    return response.status_code


async def bad_file_open():
    with open("data.txt") as f:  # CS003 - blocking file I/O
        return f.read()


async def good_async_sleep():
    await asyncio.sleep(1)  # OK - async sleep
    return "done"


def regular_function():
    # These are fine in regular functions
    time.sleep(1)
    requests.get("https://example.com")
    with open("file.txt") as f:
        pass


async def good_uses_aiohttp():
    # This would use async HTTP library (not detected as bad)
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com") as response:
            return await response.json()
