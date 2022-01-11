from .signal_manager import SignalManager
from settings import WampifySessionSettings
from autobahn.asyncio.wamp import ApplicationSession as AsyncioApplicationSession
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from typing import *


class WAMPShoppingCart:
    """
    """

    _urip: Union[str, None]
    # register uri: procedure, options
    _R: List[Tuple[str, Callable, Mapping]]
    # subscribe uri: procedure, options
    _S: List[Tuple[str, Callable, Mapping]]

    def __init__(
        self,
        uri_prefix: str = None
    ):
        self.urip = uri_prefix
        self._R = []
        self._S = []

    def _create_uri(
        self,
        path: str
    ) -> str:
        if self._urip is None:
            return path
        return f"{self._urip}.{path}"

    def add_register(
        self,
        path: str,
        procedure: Callable,
        O: Mapping[str, Any]
    ):
        """
        Adds register procdure
        """
        assert type(path) == str, 'path must be string'
        assert callable(procedure), 'procedure must be Callable'
        I = self._create_uri(path)
        self._R.append((I, procedure, O))

    def add_subscribe(
        self,
        path: str,
        procedure: Callable,
        O: Mapping[str, Any]
    ):
        """
        Adds susbscribe procedure
        """
        assert type(path) == str, 'path must be string'
        assert callable(procedure), 'procedure must be Callable'
        I = self._create_uri(path)
        self._S.append((I, procedure, O))

    def get_registered(
        self
    ) -> List[Tuple[str, Callable, Mapping[str, Any]]]:
        """
        Returns all registered procedures with uri and register options
        """
        return self._R

    def get_subscribed(
        self
    ) -> List[Tuple[str, Callable, Mapping[str, Any]]]:
        """
        Returns all subscribed procedures with uri and subscribe options
        """
        return self._S


class AsyncioWampifySession(AsyncioApplicationSession):
    """
    """

    _cart: WAMPShoppingCart
    _signal_manager: SignalManager
    _settings: WampifySessionSettings

    async def onConnect(
        self
    ):
        """
        """
        self.join(
            realm=self._settings.realm,
            authmethods=self._settings.authmethods,
            authid=self._settings.authid,
            authrole=self._settings.authrole,
            authextra=self._settings.authextra,
            resumable=self._settings.resumable,
            resume_session=self._settings.resume_session,
            resume_token=self._settings.resume_token,
        )

    async def onJoin(
        self,
        details
    ):
        """
        """
        for I, F, O in self._cart.get_registered():
            await self.register(F, I, RegisterOptions(**O))
            if self._settings.show_registered:
                print(f'{I} registered')

        for I, F, O in self._cart.get_subscribed():
            await self.subscribe(F, I, SubscribeOptions(**O))
            if self._settings.show_registered:
                print(f'{I} subscribed')

        await self._signal_manager.fire('wamp_session_joined')

    async def onLeave(
        self,
        details
    ):
        """
        """
        self.disconnect()

        await self._signal_manager.fire('wamp_session_leaved')

    async def onDisconnect(
        self
    ):
        """
        """

