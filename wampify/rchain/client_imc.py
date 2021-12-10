from .base import RChain, RCSettings
from service.client_imc import client_imc
from typing import Mapping


class ClientIMCRC(RChain):

    class Settings(RCSettings):
        name = 'client_imc'

    async def handle(
        self,
        scope: Mapping
    ):
        self.story.client_imc = client_imc[self.story.client]
        return await self.call_next(scope)

