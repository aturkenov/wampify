from typing import Callable
import asyncio
from async_timeout import timeout
from wampify.story import *
from wampify.requests import BaseRequest
from wampify.exceptions import TimedOut


async def TimeoutMiddleware(
    next_: Callable,
    request: BaseRequest
):
    story = get_current_story()
    settings = story._endpoint_options_.middlewares.get('timeout', None)
    if settings is None:
        settings = story._settings_.middlewares.get('timeout', {})

    disabled = settings.get('disabled', False)
    if disabled:
        return await next_(request)

    duration = settings.get('duration', 100)
    try:
        async with timeout(duration):
            output = await next_(request)
    except asyncio.TimeoutError:
        raise TimedOut
    else:
        return output

