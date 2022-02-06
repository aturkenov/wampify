import asyncio
from wampify.wamp_client import WAMPClient


async def amain():
    client = await WAMPClient('a')
    print(await client.call('com.example.pow', 10))
    print(await client.publish('com.example.hello'))


asyncio.run(amain())