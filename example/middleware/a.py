import asyncio
from wampify import Wampify
from wampify.middlewares import BaseMiddleware
from wampify.middlewares.timeout import TimeoutMiddleware


wampify = Wampify(
    debug=False,
    preuri='com.example',
    router={ 'url': 'ws://127.0.0.1:8080/private' },
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    },
    middlewares={
        'timeout': {
            'duration': 60 # 1 minute timout
        }
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


@wampify.register(
    options={'middlewares': {'timeout': {'duration': 1}}}
)
async def long():
    await asyncio.sleep(2)


if __name__ == '__main__':
    wampify.run()

