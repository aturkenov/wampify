from .base import RChain, RCSettings
from typing import *


class EndpointRC(RChain):
    """
    """

    class Settings(RCSettings):
        name = 'endpoint'

    async def handle(
        self,
        scope: Mapping
    ):
        """
        """
        A, K = scope['request'].A, scope['request'].K
        return await scope['request'].endpoint(*A, **K)

