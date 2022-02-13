import asyncio
from wampify import Wampify
from wampify.middleware import BaseMiddleware
from wampify.middleware.timeout import TimeoutMiddleware


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


class TestMiddleware(BaseMiddleware):

    async def handle(
        self,
        request
    ):
        print(f'client {request.client.i} sent request')
        return await self.call_next(request)

wampify.add_middleware(TestMiddleware)
wampify.add_middleware(TimeoutMiddleware)


@wampify.register('long', options={ 'validate_endpoint': False })
async def long():
    await asyncio.sleep(2)


if __name__ == '__main__':
    wampify.run()

