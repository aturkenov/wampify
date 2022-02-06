from wampify import Wampify
from wampify._wamp_client import WAMPClient
from wampify.signal_manager import wamps_signals
import asyncio


ANOTHER_ROUTER_URL = 'ws://127.0.0.1:8080/private'
client = WAMPClient(router_url=ANOTHER_ROUTER_URL, realm='example')

@wamps_signals.on
async def joined(session, details):
    await client.join()
    async def f(i):
        return i ** 2 == await client.call('com.example.pow', i)
    print('wamp client session joined')
    print(await asyncio.gather(
        *[f(i) for i in range(3)],
        return_exceptions=True
    ))

@wamps_signals.on
async def leaved(session, details):
    await client.leave()


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)

@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')


if __name__ == '__main__':
    wampify.run()

