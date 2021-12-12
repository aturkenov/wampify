from core.request import *
from core.error import *
from pydantic import BaseModel
from typing import *


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
        new_settings: Mapping[str, Any]
    ) -> None:
        self._update_settings(new_settings)

    def _update_settings(
        self,
        new_settings: Mapping 
    ):
        """
        Updates settings
        """
        assert type(new_settings) == dict
        rchain_settings = new_settings.get(self.name, {})
        self.settings = self.DefaultSettings(**rchain_settings)

    async def call_next(
        self,
        request: BaseRequest
    ) -> Awaitable:
        """
        Calls next chain and passes settings
        """
        if self._next is None:
            raise RChainNotBoundError
        return await self._next.handle(request)

    async def handle(
        self,
        request: BaseRequest
    ):
        """
        """
        raise NotImplementedError


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
    ):
        """
        """
        return await self.call_next(request)

