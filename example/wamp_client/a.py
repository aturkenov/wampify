from wampify import Wampify


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)


@wampify.register
async def pow(x: float = 1):
    return x ** 2


if __name__ == '__main__':
    wampify.run()

