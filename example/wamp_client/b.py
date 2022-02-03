from wampify import Wampify
from wampify.wamp_client import WAMPClient
from wampify.signal_manager import wamps_signals


ANOTHER_ROUTER_URL = 'ws://127.0.0.1:8080/private'
client = WAMPClient(router_url=ANOTHER_ROUTER_URL)

@wamps_signals.on
async def joined(session, details):
    await client.join(realm='example')

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
    answer = await client.call('com.example.pow', 10)
    print(f'Another session answered: {answer}')


if __name__ == '__main__':
    wampify.run()

