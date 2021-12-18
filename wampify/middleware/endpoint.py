from .base import BaseMiddleware
from core.request import *
from core.endpoint import *
from typing import *


class EndpointMiddleware(BaseMiddleware):
    """
    It's last Middleware. Just executes endpoint.
    """

    name = 'endpoint'
    endpoint: Endpoint

    async def handle(
        self,
        request: BaseRequest
    ):
        return await self.endpoint(*request.A, **request.K)

