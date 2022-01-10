from .wamp import *
from .entrypoint import *
from .middleware import *
from settings import *
from typing import *


class Wampify:

    _middlewares: List[BaseMiddleware]
    _serializers: List[Callable]
    settings: WampifySettings
    wamp: WAMPBackend

    def __init__(
        self,
        settings: Dict
    ) -> None:
        self._middlewares = []
        self._serializers = []
        self.settings = get_validated_settings(settings)
        self.wamp = WAMPBackend(self.settings.wamp)

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
        settings: Mapping = {}
    ) -> Callable:
        """
        Adds register procedure

        - `settings`: {
            'validate_payload': boolean
        }

        Returns passed procedure

        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        >>> wampify.add_register('pow', pow)
        """
        entrypoint = CallEntrypoint(
            procedure, EndpointSettings(**settings),
            self.settings, self._middlewares, self._serializers,
        )

        async def on_call(
            *A,
            _CALL_DETAILS_,
            **K,
        ):
            return await entrypoint(A, K, _CALL_DETAILS_)

        self.wamp._cart.add_register(
            path, on_call, {'details_arg': '_CALL_DETAILS_'}
        )
        return procedure

    def add_subscribe(
        self,
        path: str,
        procedure: Callable,
        settings: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure

        - `settings`: {
            'validate_payload': boolean
        }

        Returns passed procedure

        >>> async def on_hello(name: str = 'Anonymous'):
        >>>     print(f'{name} said hello')
        >>> wampify.add_subscribe('hello', on_hello)
        """
        entrypoint = PublishEntrypoint(
            procedure, EndpointSettings(**settings),
            self.settings, self._middlewares, self._serializers,
        )

        async def on_publish(
            *A,
            _PUBLISH_DETAILS_,
            **K,
        ):
            return await entrypoint(A, K, _PUBLISH_DETAILS_)

        self.wamp._cart.add_subscribe(
            path, on_publish, {'details_arg': '_PUBLISH_DETAILS_'}
        )
        return procedure

    def add_signal(
        self,
        name: str,
        procedure: Callable,
        settings = {} 
    ) -> Callable:
        """
        Adds signal ('wamp_session_joined', 'wamp_session_leaved', etc...)

        - `settings`: {}

        Returns passed procedure

        >>> async def on_wamp_session_leaved():
        >>>     print("I'll be back!")
        >>>
        >>> wampify.add_signal(
        >>>     'wamp_session_leaved', on_wamp_session_leaved
        >>> )
        """
        entrypoint = Entrypoint(procedure, self.settings)
        self.wamp._cart.add_signal(name, entrypoint, settings)
        return procedure

    def register(
        self,
        path_or_procedure: Union[str, Callable] = None,
        *,
        settings: Mapping = {}
    ) -> Callable:
        """
        Adds register procedure as decorator

        If URI segment is not passed, then procedure name

        - `settings`: {
            'validate_payload': boolean
        }

        Returns passed procedure

        >>> @wampify.register
        >>> async def pow(x: float = 1):
        >>>     return x ** 2
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path_or_procedure is None:
                path = procedure.__name__
            return self.add_register(path, path_or_procedure, settings)
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_register(path, path_or_procedure, settings)
            return procedure
        return decorate

    def subscribe(
        self,
        path_or_procedure: Union[str, Callable] = None,
        *,
        settings: Mapping = {}
    ) -> Callable:
        """
        Adds subscribe procedure as decorator

        If URI segment is not passed, then procedure name

        - `settings`: {
            'validate_payload': boolean
        }

        Returns passed procedure

        >>> @wampify.subscribe
        >>> async def hello(name: str = 'Anonymous'):
        >>>     print(f'{name} you are welcome!')
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path_or_procedure is None:
                path = procedure.__name__
            return self.add_subscribe(path, path_or_procedure, settings)
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_subscribe(path, path_or_procedure, settings)
            return procedure
        return decorate

    def on(
        self,
        signal_name_or_procedure: Union[str, Callable] = None,
        settings: Mapping = {}
    ) -> Callable:
        """
        Adds signal ('wamp_session_joined', 'wamp_session_leaved',
        etc...) as decorator

        If signal_name is not passed, then procedure name

        - `settings`: {}

        Returns passed procedure

        >>> @wampify.on
        >>> async def wamp_session_leaved():
        >>>     print("I'll be back!")
        """
        def decorate(
            procedure: Callable
        ):
            signal_name = signal_name_or_procedure
            if signal_name is None:
                signal_name = procedure.__name__
            return self.add_signal(signal_name, procedure, settings)
        if callable(signal_name_or_procedure):
            procedure = signal_name_or_procedure
            signal_name = procedure.__name__
            self.add_signal(signal_name, procedure, settings)
            return procedure
        return decorate

    def run(
        self,
        router_url: str = None,
        start_loop = None
    ) -> None:
        """
        Runs wamp session and if `start_loop` is passed, executes event loop

        - `router_url` - wamp router url
        - `start_loop` - executes event loop

        Returns: None
        """
        self.wamp.run(router_url, start_loop)

