import sys
sys.path.append('/home/aidar/wampify')
sys.path.append('/home/aidar/wampify/wampify')

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


# @wampify.register('hello')
async def hello(name: str = 'anonymous'):
    return f'Hello, {name}!'


wampify.add_register('hello', hello)


if __name__ == '__main__':
    wampify.run()