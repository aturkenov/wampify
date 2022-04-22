from wampify.wamp import WAMPBucket
from wampify.middlewares import BaseMiddleware
from wampify.entrypoints import CallEntrypoint, PublishEntrypoint
from wampify.settings import WampifySettings, get_validated_settings
from wampify import logger
from autobahn.wamp import (
    ISession as WAMPIS,
    RegisterOptions, SubscribeOptions,
    CallDetails, EventDetails
)
from autobahn.asyncio.wamp import ApplicationRunner
from typing import Callable, Union, List, Mapping


class Wampify:
    """

    >>> Wampify(
    >>> 
    >>> )
    """

    settings: WampifySettings
    wamps_factory: WAMPIS
    _wamps: Union[WAMPIS, None]
    _middlewares: List[BaseMiddleware]
    _bucket: WAMPBucket

    def __init__(
        self,
        **KW
    ) -> None:
        self._wamps = None
        self._middlewares = []
        self.settings = get_validated_settings(**KW)
        self.wamps_factory = self.settings.wamps.factory
        self.wamps_factory._settings = self.settings.wamps
        self._bucket = WAMPBucket()
        self.wamps_factory._bucket = self._bucket
        self.wamps_factory.onChallenge = self.settings.wamps.on_challenge
        self._wamps = self.wamps_factory()
        logger.mount(self)

    def add_middleware(
        self,
        m: BaseMiddleware
    ) -> None:
        """
        Adds custom middleware
        """
        _ = isinstance(m, BaseMiddleware) or issubclass(m, BaseMiddleware)
        assert _, 'Must be BaseMiddleware'
        self._middlewares.append(m)

    def add_register(
        self,
        uri: str,
        procedure: Callable,
        options: Mapping = {},
        without_preuri: bool = False
    ) -> Callable:
        """
        Adds register procedure

        - `options`: `EndpointOptions` (go to wampify/settings.py)
        - `without_preuri`: `bool` 

        Returns passed procedure

        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        >>>
        >>> wampify.add_register('pow', pow)
        """
        entrypoint = CallEntrypoint(
            procedure, options, self.settings,
            self._middlewares, self._wamps
        )

        async def on_call(
            *A,
            _CALL_DETAILS_: CallDetails,
            **K,
        ):
            return await entrypoint(A, K, _CALL_DETAILS_)

        _uri = uri if without_preuri else f'{self.settings.preuri}.{uri}'
        _options = { k: options.get(k, None) for k in RegisterOptions.__slots__ }
        _options['details_arg'] = '_CALL_DETAILS_'
        self._bucket.add_register(_uri, on_call, _options)
        return procedure

    def add_subscribe(
        self,
        uri: str,
        procedure: Callable,
        options: Mapping = {},
        without_preuri: bool = False
    ) -> Callable:
        """
        Adds subscribe procedure

        - `options`: `EndpointOptions` (go to wampify/settings.py)
        - `without_preuri`: `bool` 

        Returns passed procedure

        >>> async def on_hello(name = 'Anonymous'):
        >>>     print(f'{name} said hello')
        >>>
        >>> wampify.add_subscribe('hello', on_hello)
        """
        entrypoint = PublishEntrypoint(
            procedure, options, self.settings,
            self._middlewares, self._wamps
        )

        async def on_publish(
            *A,
            _PUBLISH_DETAILS_: EventDetails,
            **K,
        ):
            return await entrypoint(A, K, _PUBLISH_DETAILS_)

        _uri = uri if without_preuri else f'{self.settings.preuri}.{uri}'
        _options = { k: options.get(k, None) for k in SubscribeOptions.__slots__ }
        _options['details_arg'] = '_PUBLISH_DETAILS_'
        self._bucket.add_subscribe(_uri, on_publish, _options)
        return procedure

    def register(
        self,
        uri: Union[str, Callable] = None,
        *,
        options: Mapping = {},
        without_preuri: bool = False
    ) -> Callable:
        """
        Adds register procedure as decorator

        Uses procedure name if `uri` is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)
        - `without_preuri`: `bool`

        Returns passed procedure

        >>> @wampify.register
        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        """
        def decorate(
            procedure: Callable
        ):
            _uri = procedure.__name__ if uri is None else uri
            self.add_register(_uri, procedure, options, without_preuri)
            return procedure

        if callable(uri):
            _uri, procedure = uri.__name__, uri
            self.add_register(_uri, procedure, options, without_preuri)
            return procedure
        return decorate

    def subscribe(
        self,
        uri: Union[str, Callable] = None,
        *,
        options: Mapping = {},
        without_preuri: bool = False
    ) -> Callable:
        """
        Adds subscribe procedure as decorator

        Uses procedure name if `uri` is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)
        - `without_preuri`: `bool` 

        Returns passed procedure

        >>> @wampify.subscribe
        >>> async def hello(name = 'Anonymous'):
        >>>     print(f'{name} you are welcome!')
        """
        def decorate(
            procedure: Callable
        ):
            _uri = procedure.__name__ if uri is None else uri
            self.add_subscribe(_uri, procedure, options, without_preuri)
            return procedure

        if callable(uri):
            _uri, procedure = uri.__name__, uri
            self.add_subscribe(_uri, procedure, options, without_preuri)
            return procedure
        return decorate

    def run(
        self,
        start_loop=None
    ):
        """
        Runs WAMP session

        - `start_loop` - executes event loop

        Returns: None
        """
        def create_session(
            *A,
            **K
        ) -> WAMPIS:
            return self._wamps
        assert type(self.settings.router.url) == str, 'URL is required'
        runner = ApplicationRunner(self.settings.router.url)
        if start_loop is None:
            start_loop = self.settings.start_loop
        return runner.run(create_session, start_loop=start_loop)

