from core.request import *
from core.error import *
from pydantic import BaseModel
from typing import *
from typing_extensions import *


class RChainSettings(BaseModel):
    """
    """

    disabled = False


class BaseRChain:
    """
    """

    name: str
    settings: RChainSettings
    class DefaultSettings(RChainSettings):
        """
        """

    _next: 'BaseRChain'

    def __init__(
        self,
        new_settings: Mapping[str, Any] = ...
    ) -> None:
        if new_settings != ...:
            self._update_settings(new_settings)

    def __call__(
        self,
        new_settings: Mapping[str, Any] = ...
    ) -> Self:
        """
        Returns himself
        """
        if new_settings != ...:
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
    ): ...


RChainsDT = List['RChain']


class RChain(BaseRChain):
    """
    Represents basic CoR (Chain of Responsibility) pattern
    """

    name = 'RChain'

    class DefaultSettings(RChainSettings):
        """
        """

    async def handle(
        self,
        request: BaseRequest
    ) -> Any:
        """
        """
        return await self.call_next(request)

