from .base import RChain
from core.request import *
from service.client_imc import client_imc
from typing import *


class ClientIMCRC(RChain):

    name = 'client_imc'

    async def handle(
        self,
        request: BaseRequest
    ):
        """
        """
        request.story.client_imc = client_imc[request.story.client.i]
        return await self.call_next(request)

