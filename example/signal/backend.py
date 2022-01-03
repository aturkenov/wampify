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
            'session': {
                'realm': 'example',
                'show_registered': True,
                'show_subscribed': True
            }
        }
    }
)


@wampify.on_signal('session_joined')
async def joined():
    print('Session was joined!') 


# wampify.add_signal('session_joined', joined)


@wampify.on_signal('session_leaved')
def leaved():
    print('Session was leaved!') 


# wampify.add_signal('session_leaved', leaved)


if __name__ == '__main__':
    wampify.run()