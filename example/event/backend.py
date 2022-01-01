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


@wampify.on('joined')
async def joined():
    print('Session was joined!') 


# wampify.add_event_listener('joined', joined)


@wampify.on('leaved')
def leaved():
    print('Session was leaved!') 


# wampify.add_event_listener('leaved', leaved)

if __name__ == '__main__':
    wampify.run()