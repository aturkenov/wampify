from wampify.core.wampify import Wampify


wampify = Wampify(
    settings={
        'debug': False,
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


@wampify.register
async def pow(x: float = 1):
    return x ** 2


@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')


if __name__ == '__main__':
    wampify.run()

