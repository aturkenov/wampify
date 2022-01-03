from settings import WAMPBackendSettings, WampifySessionSettings
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
    # register uri: procedure, options
    _R: List[Tuple[str, Callable, Mapping]]
    # subscribe uri: procedure, options
    _S: List[Tuple[str, Callable, Mapping]]
    # signal name: (procedures, options)[]
    _E: Dict[str, List[Tuple[Callable, Mapping]]]

    def __init__(
        self,
        domain: str = None
    ):
        self._domain = domain
        self._R = []
        self._S = []
        self._E = {}

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

    def add_signal(
        self,
        name: str,
        procedure: Callable,
        settings: Mapping = {}
    ):
        """
        Adds signal 
        """
        assert type(name) == str, 'signal name must be string'
        assert callable(procedure), 'procedure must be Callable'
        self._E.setdefault(name, [])
        _ = procedure, settings
        self._E[name].append(_)

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

    def get_signals(
        self,
        name: str
    ) -> List[Tuple[Callable, Mapping]]:
        return self._E.get(name, [])

    async def fire(
        self,
        name: str
    ) -> None:
        S = self.get_signals(name)
        for procedure, options in S:
            await procedure()


class AsyncioWampifySession(AsyncioApplicationSession):
    """
    """

    _settings: WampifySessionSettings
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
            if self._settings.show_registered:
                print(f'{I} was registered')

        for I, F, O in self._cart.get_subscribed():
            await self.subscribe(F, I, SubscribeOptions(**O))
            if self._settings.show_registered:
                print(f'{I} was subscribed')

        await self._cart.fire('session_joined')

    async def onLeave(
        self,
        details
    ):
        """
        """
        self.disconnect()
 
        await self._cart.fire('session_leaved')

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
    ) -> ISession:
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

