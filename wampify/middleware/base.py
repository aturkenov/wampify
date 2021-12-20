from pydantic import BaseModel
from core.request import *
from core.error import *
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

    def __call__(
        self,
        new_settings: Mapping[str, Any] = None
    ) -> Self:
        """
        Returns himself
        """
        if new_settings != None:
            self._update_settings(new_settings)
        return self

    def _update_settings(
        self,
        new_settings: Mapping 
    ) -> None:
        """
        Updates settings
        """
        rchain_settings = new_settings.get(self.name, {})
        self.settings = self.DefaultSettings(**rchain_settings)

    async def call_next(
        self,
        request: BaseRequest
    ) -> Awaitable:
        """
        Calls next chain
        """
        if self._next is None:
            raise RChainNotBoundError
        return await self._next.handle(request)

    async def handle(
        self,
        request: BaseRequest
    ) -> Any: ...

