import asyncio
from wampify.wamp_client import WAMPClient


async def main():
    client = WAMPClient(
        'http://127.0.0.1:8080/call',
        'http://127.0.0.1:8080/publish',
        'client',
        'secret'
    )

    print(await client.call('com.example.pow', 10))
    print(await client.publish('com.example.hello', 'Ivan'))


if __name__ == '__main__':
    asyncio.run(main())

