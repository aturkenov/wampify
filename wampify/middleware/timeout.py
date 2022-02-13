import asyncio
from .base import BaseMiddleware
from wampify.exceptions import TimeoutExpired
from async_timeout import timeout


class TimeoutMiddleware(BaseMiddleware):

    async def handle(
        self,
        request
    ):
        # Timeout for 1 second
        try:
            async with timeout(1):
                output = await self.call_next(request)
        except asyncio.TimeoutError:
            raise TimeoutExpired()
        else:
            return output

