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
        uri_segment: str,
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
            uri_segment, on_call, {'details_arg': '_CALL_DETAILS_'}
        )
        return on_call

    def add_subscribe(
        self,
        uri_segment: str,
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
            uri_segment, on_publish, {'details_arg': '_PUBLISH_DETAILS_'}
        )
        return on_publish

    def register(
        self,
        uri_segment: str = None,
        settings: Mapping = {}
    ) -> Callable:
        """
        """
        async def decorate(
            procedure: Callable
        ):
            nonlocal uri_segment
            if uri_segment is None:
                uri_segment = procedure.__name__
            return self.add_register(
                uri_segment=uri_segment,
                procedure=procedure,
                settings=settings
            )
        return decorate

    def subscribe(
        self,
        uri_segment: str = None,
        settings: Mapping = {}
    ) -> Callable:
        """
        """
        def decorate(
            procedure: Callable
        ):
            nonlocal uri_segment
            if uri_segment is None:
                uri_segment = procedure.__name__
            return self.add_subscribe(
                uri_segment=uri_segment,
                procedure=procedure,
                settings=settings
            )
        return decorate
  
    def run(
        self,
        url: str = None,
        start_loop = None
    ) -> None:
        """
        """
        self.wamp.run(url=url, start_loop=start_loop)

