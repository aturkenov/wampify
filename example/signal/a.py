from wampify import Wampify
from wampify.signal_manager import wamps_signals
from autobahn.wamp import ISession


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


@wamps_signals.on
async def joined(wamps: ISession, details):
    wamps.publish('com.example.hello_world')


@wamps_signals.on
def leaved(wamps: ISession, details):
    wamps.publish('com.example.ill_be_back')


if __name__ == '__main__':
    wampify.run()

