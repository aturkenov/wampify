from shared.ensure_deferred import ensure_deferred
from settings import WAMPBackendSettings, WAMPBSessionSettings
from autobahn.wamp import ISession
from autobahn.asyncio.wamp import (
        ApplicationSession as AsyncioApplicationSession,
        ApplicationRunner as AsyncioApplicationRunner
    )
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from typing import *


class WAMPBShoppingCart:
    """
    """

    _domain: Union[str, None]
    # uri: register procedure with register option
    _R: List[Tuple[str, Callable, Mapping[str, Any]]]
    # uri: subscribe procedure with subscribe option
    _S: List[Tuple[str, Callable, Mapping[str, Any]]] 

    def __init__(
        self,
        domain: str = None
    ):
        self._domain = domain
        self._R = []
        self._S = []

    def _create_uri(
        self,
        path: str
    ) -> str:
        if self._domain is None:
            return path
        return f"{self._domain}.{path}"

    def add_register(
        self,
        path: str,
        procedure: Callable,
        O: Mapping[str, Any]
    ):
        """
        Adds register procdure to shopping cart
        """
        assert type(path) == str, '`path` must be string'
        assert callable(procedure), 'procedure must be callable'
        I = self._create_uri(path)
        self._R.append((I, procedure, O))

    def add_subscribe(
        self,
        path: str,
        procedure: Callable,
        O: Mapping[str, Any]
    ):
        """
        Adds susbscribe procedure to shopping cart
        """
        assert type(path) == str, '`path` must be string'
        assert callable(procedure), 'procedure must be callable'
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


class AsyncioWAMPBSession(AsyncioApplicationSession):
    """
    """

    _settings: WAMPBSessionSettings
    _cart: WAMPBShoppingCart

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
        print('Session was joined')

        for I, F, O in self._cart.get_registered():
            await self.register(F, I, RegisterOptions(**O))

        for I, F, O in self._cart.get_subscribed():
            await self.subscribe(F, I, SubscribeOptions(**O))

    async def onLeave(
        self,
        details
    ):
        """
        """
        self.disconnect()

    async def onDisconnect(
        self
    ):
        """
        """


class WAMPBackend:
    """
    """

    settings: WAMPBackendSettings
    session: Union[ISession, None]
    session_factory: ISession
    _cart: WAMPBShoppingCart

    def __init__(
        self,
        settings: WAMPBackendSettings
    ):
        self.session = None
        self.settings = settings
        self.session_factory = settings.session.factory
        self.session_factory._settings = settings.session
        self._cart = WAMPBShoppingCart(settings.domain)
        self.session_factory._cart = self._cart

    def _create_session(
        self,
        *A,
        **K
    ) -> AsyncioWAMPBSession:
        """
        """
        assert self.session is None
        self.session = self.session_factory()
        return self.session

    def run(
        self,
        url: str = None,
        start_loop = None
    ):
        """
        """
        if url is None:
            url = self.settings.url
        assert type(url) == str, 'URL is required'
        runner = AsyncioApplicationRunner(url)
        if start_loop is None:
            start_loop = self.settings.start_loop
        return runner.run(self._create_session, start_loop=start_loop)

