from .base import RChain, RCSettings
from core.error import KBaseError, SomethingWentWrong
from autobahn.wamp.exception import ApplicationError
from typing import Mapping


class ErrorRC(RChain):
    """
    """

    class Settings(RCSettings):
        name = 'error'
        domain = 'error'
        debug = False

    def _create_uri(
        self,
        name
    ):
        domain = self.sget('domain')
        return f'{domain}.{name}'

    async def handle(
        self,
        scope: Mapping
    ):
        """
        """
        try:
            return await self.call_next(scope)
        except KBaseError as e:
            if self.sget('debug'):
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

