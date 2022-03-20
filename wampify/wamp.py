from wampify.signals import wamps_signals
from wampify.settings import WampifySessionSettings
from autobahn.asyncio.wamp import ApplicationSession as AsyncioApplicationSession
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from typing import List, Tuple, Callable, Mapping, Any


class WAMPBucket:
    """
    """

    # register uri: procedure, options
    _R: List[Tuple[str, Callable, Mapping]]
    # subscribe uri: procedure, options
    _S: List[Tuple[str, Callable, Mapping]]

    def __init__(
        self
    ):
        self._R = []
        self._S = []

    def add_register(
        self,
        URI: str,
        procedure: Callable,
        options: Mapping[str, Any]
    ) -> str:
        """
        Adds register procdure
        """
        self._R.append((URI, procedure, options))

    def add_subscribe(
        self,
        URI: str,
        procedure: Callable,
        options: Mapping[str, Any]
    ) -> str:
        """
        Adds susbscribe procedure
        """
        self._S.append((URI, procedure, options))

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

    _bucket: WAMPBucket
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
            resume_token=self._settings.resume_token
        )

    async def onJoin(
        self,
        details
    ):
        """
        """
        for I, F, O in self._bucket.get_registered():
            await self.register(F, I, RegisterOptions(**O))
            if self._settings.show_registered:
                print(f'{I} registered')

        for I, F, O in self._bucket.get_subscribed():
            await self.subscribe(F, I, SubscribeOptions(**O))
            if self._settings.show_registered:
                print(f'{I} subscribed')

        await wamps_signals.fire('joined', self, details)

    async def onLeave(
        self,
        details
    ):
        """
        """
        self.disconnect()

        await wamps_signals.fire('leaved', self, details)

    async def onDisconnect(
        self
    ):
        """
        """

