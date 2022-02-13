from wampify.requests import *
from wampify.exceptions import *
from typing import *
from typing_extensions import *


class BaseMiddleware:
    """
    """

    class Settings:
        """
        """

    _next: 'BaseMiddleware'

    @classmethod
    def set_next(
        klass,
        m: 'BaseMiddleware'
    ) -> None:
        klass._next = m

    async def call_next(
        self,
        request: BaseRequest
    ) -> Coroutine:
        """
        Calls next chain
        """
        if self._next is None:
            raise MiddlewareNotBoundError
        return await self._next(request)

    async def handle(
        self,
        request: BaseRequest
    ) -> Any: ...

    async def __call__(
        self,
        request: BaseRequest
    ) -> Coroutine:
        return await self.handle(request)

