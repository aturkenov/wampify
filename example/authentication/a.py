from wampify import Wampify
from wampify.exceptions import AuthenticationFailed


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamps={
        'realm': 'example',
        'authmethods': ['anonymous'],
        'show_registered': True,
        'show_subscribed': True
    }
)


AVAILABLE_USERS = {
    'Ivan:secret'
}

DEFAULT_USER_ROLE = 'public'

@wampify.register
def authentication(realm, authid, details):
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

