from pydantic import BaseModel
from wampify.request import *
from wampify.error_list import *
from typing import *
from typing_extensions import *


class MiddlewareSettings(BaseModel):
    """
    """

    disabled = False

    class Config:
        arbitrary_types_allowed = True


class BaseMiddleware:
    """
    """

    name: str
    settings: MiddlewareSettings

    class DefaultSettings(MiddlewareSettings):
        """
        """

    _next: 'BaseMiddleware'

    def __init__(
        self,
        new_settings: Mapping[str, Any] = None
    ) -> None:
        if new_settings != None:
            self._update_settings(new_settings)

    def _update_settings(
        self,
        new_settings: Mapping 
    ) -> None:
        """
        Updates settings
        """
        rchain_settings = new_settings.get(self.name, {})
        self.settings = self.DefaultSettings(**rchain_settings)

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

