import sys
sys.path.append('../..')
sys.path.append('../../wampify')

from wampify.core.wampify import Wampify


wampify = Wampify(
    settings={
        'debug': True,
        'wamp': {
            'domain': 'com.example',
            'url': 'ws://127.0.0.1:8080/private',
            'session': { 'realm': 'example' }
        }
    }
)


@wampify.register('hello')
def hello(name: str = 'anonymous'):
    return f'Hello, {name}!'


if __name__ == '__main__':
    wampify.run()