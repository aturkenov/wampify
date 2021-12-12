from .base import RChain, RChainSettings
from core.request import *
from core.error import KBaseError, SomethingWentWrong
from autobahn.wamp.exception import ApplicationError
from typing import *


class ErrorRC(RChain):
    """
    It's first RChain.
    """

    name = 'error'

    class DefaultSettings(RChainSettings):
        domain = 'wamp.error'
        debug = False

    def _create_uri(
        self,
        name
    ):
        return f'{self.settings.domain}.{name}'

    async def handle(
        self,
        request: BaseRequest
    ):
        """
        """
        try:
            return await self.call_next(request)
        except KBaseError as e:
            if self.settings.debug:
                raise e

            try:
                e.__init__()
                _ = {
                    'error': self._create_uri(e.name),
                    'payload': e.to_primitive()
                }
            except:
                e = SomethingWentWrong()
                _ = {
                    'error': self._create_uri(e.name),
                    'payload': e.to_primitive()
                }

        raise ApplicationError(**_)

