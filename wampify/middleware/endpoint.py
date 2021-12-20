from .base import BaseMiddleware, MiddlewareSettings
from core.request import *
from core.endpoint import *
from typing import *


class EndpointMiddleware(BaseMiddleware):
    """
    It's last Middleware. Just executes endpoint.
    """

    name = 'endpoint'
    endpoint: Endpoint

    def set_endpoint(
        self,
        endpoint: Endpoint
    ) -> None:
        self.endpoint = endpoint

    async def handle(
        self,
        request: BaseRequest
    ):
        return await self.endpoint(*request.A, **request.K)

