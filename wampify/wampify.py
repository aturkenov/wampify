from .wamp import WAMPShoppingCart
from .middleware import BaseMiddleware
from .entrypoint import (
    CallEntrypoint, PublishEntrypoint
)
from .settings import (
    WampifySettings, get_validated_settings, EndpointOptions
)
from . import background_task
from . import logger
from autobahn.wamp import ISession as WAMPIS
from autobahn.asyncio.wamp import ApplicationRunner as AsyncioApplicationRunner
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
    _serializers: List[Callable]
    _cart: WAMPShoppingCart

    def __init__(
        self,
        **KW
    ) -> None:
        self._wamps = None
        self._middlewares = []
        self._serializers = []
        self.settings = get_validated_settings(**KW)
        self.wamps_factory = self.settings.wamps.factory
        self.wamps_factory._settings = self.settings.wamps
        self._cart = WAMPShoppingCart(self.settings.uri_prefix)
        self.wamps_factory._cart = self._cart
        background_task.mount(self)
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

    def add_serializer(
        self,
        s: Callable
    ) -> None:
        """
        Adds custom serializer
        """
        assert callable(s), 'Serializer must be callable'
        # TODO add some serialization tests here
        self._serializers.append(s)

    def add_register(
        self,
        path: str,
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
        entrypoint = CallEntrypoint(
            procedure, EndpointOptions(**options), self.settings,
            self._middlewares, self._serializers, self._wamps
        )

        async def on_call(
            *A,
            _CALL_DETAILS_,
            **K,
        ):
            return await entrypoint(A, K, _CALL_DETAILS_)

        URI = self._cart.add_register(
            path, on_call, {'details_arg': '_CALL_DETAILS_'}
        )
        return procedure

    def add_subscribe(
        self,
        path: str,
        procedure: Callable,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> async def on_hello(name: str = 'Anonymous'):
        >>>     print(f'{name} said hello')
        >>>
        >>> wampify.add_subscribe('hello', on_hello)
        """
        entrypoint = PublishEntrypoint(
            procedure, EndpointOptions(**options), self.settings,
            self._middlewares, self._serializers, self._wamps
        )

        async def on_publish(
            *A,
            _PUBLISH_DETAILS_,
            **K,
        ):
            return await entrypoint(A, K, _PUBLISH_DETAILS_)

        URI = self._cart.add_subscribe(
            path, on_publish, {'details_arg': '_PUBLISH_DETAILS_'}
        )
        return procedure

    def register(
        self,
        path_or_procedure: Union[str, Callable] = None,
        *,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds register procedure as decorator

        Uses procedure name if URI segment is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> @wampify.register
        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path is None:
                path = procedure.__name__
            return self.add_register(path, procedure, options)
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_register(path, procedure, options)
            return procedure
        return decorate

    def subscribe(
        self,
        path_or_procedure: Union[str, Callable] = None,
        *,
        options: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure as decorator

        Uses procedure name if URI segment is not passed

        - `options`: `EndpointOptions` (go to wampify/settings.py)

        Returns passed procedure

        >>> @wampify.subscribe
        >>> async def hello(name: str = 'Anonymous'):
        >>>     print(f'{name} you are welcome!')
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path is None:
                path = procedure.__name__
            return self.add_subscribe(path, procedure, options)
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_subscribe(path, procedure, options)
            return procedure
        return decorate

    def run(
        self,
        router_url: str = None,
        start_loop=None
    ):
        """
        Runs WAMP session

        if `start_loop` is passed, executes event loop

        - `router_url` - wamp router url
        - `start_loop` - executes event loop

        Returns: None
        """
        def create_session(
            *A,
            **K
        ) -> WAMPIS:
            assert self._wamps is None
            self._wamps = self.wamps_factory()
            return self._wamps
        if router_url is None:
            router_url = self.settings.router_url
        assert type(router_url) == str, 'URL is required'
        runner = AsyncioApplicationRunner(router_url)
        if start_loop is None:
            start_loop = self.settings.start_loop
        return runner.run(create_session, start_loop=start_loop)

