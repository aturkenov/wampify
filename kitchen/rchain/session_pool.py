from .base import RChain, RCSettings
from service.session_pool import SessionPool
from typing import Mapping


class SessionPoolRC(RChain):
    """
    """

    class Settings(RCSettings):
        name = 'session_pool'
        factories = []

    async def handle(
        self,
        scope: Mapping
    ):
        """
        """
        factories = self.sget('factories')
        self.story.session_pool = SessionPool(factories)
        return await self.call_next(scope)

