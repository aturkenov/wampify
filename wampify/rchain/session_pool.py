from .base import RChain, RChainSettings
from core.request import *
from service.session_pool import SessionPool
from typing import *


class SessionPoolRC(RChain):
    """
    """

    class DefaultSettings(RChainSettings):
        name = 'session_pool'
        factories = []

    async def handle(
        self,
        request: BaseRequest
    ):
        """
        """
        request.story.session_pool = SessionPool(self.settings.factories)
        return await self.call_next(request)

