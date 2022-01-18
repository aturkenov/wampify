from wampify.core.wampify import Wampify
from wampify.core.middleware import BaseMiddleware


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


class CustomMiddleware(BaseMiddleware):

    name = 'custom'

    async def handle(
        self,
        request
    ):
        print(f'client {request.client.i} sent request')
        return await self.call_next(request)


wampify.add_middleware(CustomMiddleware)


@wampify.register
async def hello(name: str = 'anonymous'):
    return f'Hello, {name}!'


if __name__ == '__main__':
    wampify.run()

