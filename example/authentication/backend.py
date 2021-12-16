from wampify.core.wampify import Wampify
from wampify.core.error import AuthenticationFailed


wampify = Wampify(
    settings={
        'debug': True,
        'wamp': {
            'domain': 'com.example',
            'url': 'ws://127.0.0.1:8080/private',
            'session': {
                'realm': 'example',
                'authmethods': ['anonymous']
            }
        }
    }
)


AVAILABLE_USERS = {
    'ivan:secret'
}

DEFAULT_USER_ROLE = 'public'

@wampify.register('authentication')
def login(realm, authid, details):
    """
    WAMP Dynamic Ticket Authentication
    https://crossbar.io/docs/Ticket-Authentication/
    """
    print(f'WAMP Dynamic Ticket Authentication: {authid}')
    
    if details['authmethod'] != 'ticket':
        raise AuthenticationFailed('Unsupported authentication')
    
    if not f'{authid}:{details["ticket"]}' in AVAILABLE_USERS:
        raise AuthenticationFailed('Could not authenticate session - invalid ticket')

    return DEFAULT_USER_ROLE


if __name__ == '__main__':
    wampify.run()