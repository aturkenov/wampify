from wampify.requests import BaseRequest
from wampify.exceptions import MiddlewareNotBoundError
from wampify.settings import WampifySettings, EndpointOptions
from typing import Any


class BaseMiddleware:
    """
    """

    _wampify_settings: WampifySettings
    _endpoint_options: EndpointOptions
    _next: 'BaseMiddleware'

    def __init__(
        self,
        wampify_settings: WampifySettings,
        endpoint_options: EndpointOptions
    ) -> None:
        self._wampify_settings = wampify_settings
        self._endpoint_options = endpoint_options

    @classmethod
    def set_next(
        klass,
        m: 'BaseMiddleware'
    ) -> None:
        klass._next = m

    async def call_next(
        self,
        request: BaseRequest
    ) -> Any:
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
    ) -> Any:
        return await self.handle(request)

