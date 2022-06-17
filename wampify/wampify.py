from wampify.wamp import WAMPBucket
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
    session: Union[WAMPIS, None]
    middlewares: List[Callable]
    _bucket: WAMPBucket

    def __init__(
        self,
        **KW
    ) -> None:
        self.middlewares = []
        self.settings = get_validated_settings(**KW)
        self._bucket = WAMPBucket()
        logger.mount(self)

    def add_middleware(
        self,
        m: Callable
    ) -> None:
        """
        Adds custom middleware
        """
        assert callable(m), 'Middleware must be Callable'
        self.middlewares.append(m)

    def add_register(
        self,
        uri: str,
        procedure: Callable,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds register procedure

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        >>>
        >>> wampify.add_register('pow', pow)
        """
        entrypoint = CallEntrypoint(self, procedure, options)

        async def on_call(
            *args,
            _CALL_DETAILS_: CallDetails,
            **kwargs,
        ):
            return await entrypoint(args=args, kwargs=kwargs, details=_CALL_DETAILS_)

        _uri = f'{self.settings.preuri}{uri}' if uri.startswith('.') else uri
        _options = { k: options.get(k, None) for k in RegisterOptions.__slots__ }
        _options['details_arg'] = '_CALL_DETAILS_'
        self._bucket.add_register(_uri, on_call, _options)
        return procedure

    def add_subscribe(
        self,
        uri: str,
        procedure: Callable,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> async def on_hello(name = 'Anonymous'):
        >>>     print(f'{name} said hello')
        >>>
        >>> wampify.add_subscribe('hello', on_hello)
        """
        entrypoint = PublishEntrypoint(self, procedure, options)

        async def on_publish(
            *args,
            _PUBLISH_DETAILS_: EventDetails,
            **kwargs,
        ):
            return await entrypoint(args=args, kwargs=kwargs, details=_PUBLISH_DETAILS_)

        _uri = f'{self.settings.preuri}{uri}' if uri.startswith('.') else uri
        _options = { k: options.get(k, None) for k in SubscribeOptions.__slots__ }
        _options['details_arg'] = '_PUBLISH_DETAILS_'
        self._bucket.add_subscribe(_uri, on_publish, _options)
        return procedure

    def register(
        self,
        uri: Union[str, Callable] = None,
        *,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds register procedure as decorator

        Uses procedure name if `uri` is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> @wampify.register
        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        """
        if callable(uri):
            _uri, procedure = f'.{uri.__name__}', uri
            self.add_register(_uri, procedure, options)
            return procedure

        def decorate(
            procedure: Callable
        ):
            _uri = f'.{procedure.__name__}' if uri is None else uri
            self.add_register(_uri, procedure, options)
            return procedure
        return decorate

    def subscribe(
        self,
        uri: Union[str, Callable] = None,
        *,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure as decorator

        Uses procedure name if `uri` is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> @wampify.subscribe
        >>> async def hello(name = 'Anonymous'):
        >>>     print(f'{name} you are welcome!')
        """
        if callable(uri):
            _uri, procedure = f'.{uri.__name__}', uri
            self.add_subscribe(_uri, procedure, options)
            return procedure

        def decorate(
            procedure: Callable
        ):
            _uri = f'.{procedure.__name__}' if uri is None else uri
            self.add_subscribe(_uri, procedure, options)
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
            *args,
            **kwargs
        ) -> WAMPIS:
            self.session = self.settings.wamps.factory(
                *args,
                wampify_session_settings=self.settings.wamps,
                wampify_bucket=self._bucket,
                **kwargs
            )
            return self.session

        assert type(self.settings.router.url) == str, 'URL is required'
        runner = ApplicationRunner(self.settings.router.url)
        if start_loop is None:
            start_loop = self.settings.start_loop
        return runner.run(create_session, start_loop=start_loop)

