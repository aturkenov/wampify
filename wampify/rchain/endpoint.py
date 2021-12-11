from .base import RChain, RChainSettings
from core.request import *
from typing import *


class EndpointRC(RChain):
    """
    It's last Rchain. Just executes enpoint
    """

    name = 'endpoint'

    async def handle(
        self,
        request: BaseRequest
    ):
        return await request.endpoint(*request.A, **request.K)

