from .wamp import *
from .entrypoint import *
from .middleware import *
from settings import *
from typing import *


class Wampify:
    """
    """

    _M: List[BaseMiddleware]
    _serializers: List[Callable]
    settings: WampifySettings
    wamp: WAMPBackend

    def __init__(
        self,
        settings: Dict
    ) -> None:
        self._M = []
        self._serializers = []
        self.settings = get_validated_settings(settings)
        self.wamp = WAMPBackend(self.settings.wamp)

    def add_middleware(
        self,
        m: BaseMiddleware
    ) -> None:
        """
        """
        assert isinstance(m, BaseMiddleware), 'Must be BaseMiddleware'
        self._M.append(m)

    def add_serializer(
        self,
        s: Callable
    ) -> None:
        """
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
        """
        entrypoint = CallEntrypoint(
            procedure, EndpointSettings(**settings),
            self.settings, self._M, self._serializers,
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
        return on_call

    def add_subscribe(
        self,
        path: str,
        procedure: Callable,
        settings: Mapping = {}
    ) -> Callable:
        """
        """
        entrypoint = PublishEntrypoint(
            procedure, EndpointSettings(**settings),
            self.settings, self._M, self._serializers,
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
        return on_publish

    def add_signal(
        self,
        name: str,
        procedure: Callable,
        settings = {} 
    ) -> Callable:
        """
        Adds signal
        """
        entrypoint = SystemEntrypoint(procedure, self.settings)
        self.wamp._cart.add_signal(name, entrypoint, settings)
        return entrypoint.execute

    def register(
        self,
        path_or_procedure: str = None,
        *,
        settings: Mapping = {}
    ) -> Callable:
        """
        Decorator
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path_or_procedure is None:
                path = procedure.__name__
            self.add_register(path, path_or_procedure, settings)
            return procedure
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
        Decorator
        """
        def decorate(
            procedure: Callable
        ):
            path = path_or_procedure
            if path_or_procedure is None:
                path = procedure.__name__
            self.add_subscribe(path, path_or_procedure, settings)
            return procedure
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_subscribe(path, path_or_procedure, settings)
            return procedure
        return decorate

    def on_signal(
        self,
        name_or_procedure: Union[str, Callable] = None,
        settings: Mapping = {}
    ) -> Callable:
        """
        Decorator
        """
        def decorate(
            procedure: Callable
        ):
            name = name_or_procedure
            if name is None:
                name = procedure.__name__
            self.add_signal(name, procedure, settings)
            return procedure
        if callable(name_or_procedure):
            procedure = name_or_procedure
            name = procedure.__name__
            self.add_signal(name, procedure, settings)
            return procedure
        return decorate

    def run(
        self,
        url: str = None,
        start_loop = None
    ) -> None:
        """
        """
        self.wamp.run(url, start_loop)

