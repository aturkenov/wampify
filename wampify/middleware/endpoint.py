from .base import BaseMiddleware
from core.request import *
from typing import *


class EndpointMiddleware(BaseMiddleware):
    """
    It's last Middleware. Just executes endpoint.
    """

    name = 'endpoint'

    async def handle(
        self,
        request: BaseRequest
    ):
        return await request.endpoint(*request.A, **request.K)

