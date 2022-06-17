from sys import path
path.append('/home/aidar/')
from wampify.wampify import Wampify


def wamps_on_challenge(challange):
    return 'secret'


wampify = Wampify(
    debug=False,
    preuri='com.example',
    router={ 'url': 'ws://127.0.0.1:8080/private' },
    wamps={
        'realm': 'example',
        'authid': 'a',
        'authrole': 'private',
        'authmethods': ['ticket'],
        'on_challenge': wamps_on_challenge,
        'show_registered': True,
        'show_subscribed': True
    }
)


@wampify.register
async def pow(x: float = 1):
    return x ** 2


@wampify.subscribe
async def hello(name = 'Anonymous'):
    print(f'{name} you are welcome!')


if __name__ == '__main__':
    wampify.run()

