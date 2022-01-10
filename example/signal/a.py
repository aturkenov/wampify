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


@wampify.on
async def wamp_session_joined():
    print('Session was joined!') 


@wampify.on
def wamp_session_leaved():
    print('Session was leaved!') 


if __name__ == '__main__':
    wampify.run()

