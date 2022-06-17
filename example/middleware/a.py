from typing import Callable
import asyncio
from wampify import Wampify
from wampify.story import *
from wampify.middlewares.timeout import TimeoutMiddleware
from contextlib import suppress


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


async def FirstCustomMiddleware(
    next_: Callable,
    request: BaseRequest
):
    print('Im doing something prerequest!')
    return await next_(request)

async def SecondCustomMiddleware(
    next_: Callable,
    request: BaseRequest
):
    output = await next_(request)
    print('Im doing something postrequest!')
    return output

async def ThirdCustomMiddleware(
    next_: Callable,
    request: BaseRequest
):
    story = get_current_story()
    enabled = story._endpoint_options_.middlewares.get('third-custom-middleware-enabled', True)
    if enabled:
        await story._wamps_.call('com.example.user.exist', id=request.client.i)
    else:
        print(f'{request.sent_time} ThirdCustomMiddleware disabled!')
    return await next_(request)

wampify.add_middleware(FirstCustomMiddleware)
wampify.add_middleware(SecondCustomMiddleware)
wampify.add_middleware(ThirdCustomMiddleware)
wampify.add_middleware(TimeoutMiddleware)


@wampify.register(
    options={'middlewares': {
        # 'timeout': {'duration': 1},
        'third-custom-middleware-enabled': True
    }}
)
async def long():
    try:
        await asyncio.sleep(10)
    except:
        print('Catched!')


@wampify.register(
    'user.exist',
    options={'middlewares': {
        'timeout': {'duration': 1},
        'third-custom-middleware-enabled': False
    }}
)
async def exist(
    id
):
    return True


if __name__ == '__main__':
    wampify.run()

