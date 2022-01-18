from wampify.core.wampify import Wampify


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamp_session={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)


@wampify.on('_wamps_.joined')
async def wamp_session_joined():
    print('Session was joined') 


@wampify.on('_wamps_.leaved')
def wamp_session_leaved():
    print('Session was leaved') 


if __name__ == '__main__':
    wampify.run()

