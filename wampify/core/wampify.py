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
            procedure=procedure,
            endpoint_settings=EndpointSettings(**settings),
            user_settings=self.settings,
            user_middlewares=self._M,
            user_serializers=self._serializers,
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
            procedure=procedure,
            endpoint_settings=EndpointSettings(**settings),
            user_settings=self.settings,
            user_middlewares=self._M,
            user_serializers=self._serializers,
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

    def add_event_listener(
        self,
        event_name: str,
        procedure: Callable,
        settings = {} 
    ) -> Callable:
        """
        System Event Listener
        """
        entrypoint = SystemEntrypoint(
            procedure=procedure,
            user_settings=self.settings
        )
        self.wamp._cart.add_event_listener(event_name, entrypoint, settings)

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
            self.add_register(
                path=path,
                procedure=procedure,
                settings=settings
            )
            return procedure
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_register(
                path=path,
                procedure=path_or_procedure,
                settings=settings
            )
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
            self.add_subscribe(
                path=path,
                procedure=procedure,
                settings=settings
            )
            return procedure
        if callable(path_or_procedure):
            procedure = path_or_procedure
            path = procedure.__name__
            self.add_subscribe(
                path=path,
                procedure=path_or_procedure,
                settings=settings
            )
            return procedure
        return decorate

    def on(
        self,
        event_name_or_procedure: Union[str, Callable] = None,
        settings: Mapping = {}
    ) -> Callable:
        """
        Decorator
        """
        def decorate(
            procedure: Callable
        ):
            event_name = event_name_or_procedure
            if event_name is None:
                event_name = procedure.__name__
            self.add_event_listener(
                event_name=event_name,
                procedure=procedure,
                settings=settings
            )
            return procedure
        if callable(event_name_or_procedure):
            procedure = event_name_or_procedure
            event_name = procedure.__name__
            self.add_event_listener(
                event_name=event_name,
                procedure=procedure,
                settings=settings
            )
            return procedure
        return decorate

    def run(
        self,
        url: str = None,
        start_loop = None
    ) -> None:
        """
        """
        self.wamp.run(url=url, start_loop=start_loop)

