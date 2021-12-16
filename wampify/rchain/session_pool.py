from .base import RChain, RChainSettings
from core.request import *
from service.base.session_pool import SessionPool
from typing import *


class SessionPoolRC(RChain):
    """
    """

    name = 'session_pool'

    class DefaultSettings(RChainSettings):
        factories = []

    async def handle(
        self,
        request: BaseRequest
    ):
        """
        """
        request.story.session_pool = SessionPool(self.settings.factories)
        return await self.call_next(request)

