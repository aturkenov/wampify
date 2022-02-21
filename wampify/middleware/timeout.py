import asyncio
from wampify.middleware.base import BaseMiddleware
from wampify.requests import BaseRequest
from wampify.exceptions import TimeoutExpired
from async_timeout import timeout


class TimeoutMiddleware(BaseMiddleware):

    async def handle(
        self,
        request: BaseRequest
    ):
        settings = self._endpoint_options.middlewares.get('timeout', None)
        if settings is None:
            settings = self._wampify_settings.middlewares.get('timeout', {})

        disabled = settings.get('disabled', False)
        if disabled:
            return await self.call_next(request)

        duration = settings.get('duration', 100)
        try:
            async with timeout(duration):
                output = await self.call_next(request)
        except asyncio.TimeoutError:
            raise TimeoutExpired()
        else:
            return output

