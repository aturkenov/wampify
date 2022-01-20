from .story import *
from .request import (
    BaseRequest, CallRequest, PublishRequest
)
from .endpoint import (
    Endpoint, SharedEndpoint, RegisterEndpoint, SubscribeEndpoint
)
from .middleware import BaseMiddleware
from .signal_manager import SignalManager
from .error_list import SomethingWentWrong
from .settings import WampifySettings, EndpointOptions
from autobahn.wamp import ISession as WAMPIS
from autobahn.wamp.exception import ApplicationError
from typing import List, Any, Callable, Mapping


class Entrypoint:
    """
    Entrypoint creates story, execute required resources and endpoint.
    If something went wrong, raise released resources and handles exception
    else returns output and close released resources

    - `procedure`
    - `user_settings`
    """

    _endpoint: Endpoint 
    _settings: WampifySettings
    _wamps: WAMPIS
    _signal_manager: SignalManager

    def __init__(
        self,
        procedure: Callable,
        user_settings: WampifySettings,
        wamps: WAMPIS,
        signal_manager: SignalManager
    ) -> None:
        self._endpoint = Endpoint(procedure)
        self._settings = user_settings
        self._wamps = wamps
        self._signal_manager = signal_manager

    async def execute(
        self,
        A = [],
        K = {},
        D = None
    ) -> Any:
        story = create_story()
        story._wamps_ = self._wamps
        story._settings_ = self._settings
        try:
            await self._signal_manager.fire('_entrypoint_.opened', story)
            output = await self._endpoint(*A, **K)
        except BaseException as e:
            await self._signal_manager.fire('_entrypoint_.raised', story, e)
        else:
            await self._signal_manager.fire('_entrypoint_.closed', story)
            return output

    async def __call__(
        self,
        *A,
        **K
    ) -> Any:
        return await self.execute(*A, **K)


class SharedEntrypoint(Entrypoint):

    _middleware: BaseMiddleware

    def __init__(
        self,
        procedure: Callable,
        endpoint_options: EndpointOptions,
        user_settings: WampifySettings,
        user_middlewares: List[BaseMiddleware],
        user_serializers: List[Callable],
        wamps: WAMPIS,
        signal_manager: SignalManager
    ):
        self._settings = user_settings
        self._endpoint = self._create_endpoint(
            procedure, endpoint_options, user_serializers
        )
        self._build_responsibility_chain(
            user_middlewares, self._endpoint
        )
        self._wamps = wamps
        self._signal_manager = signal_manager

    def _build_responsibility_chain(
        self,
        middlewares: List[BaseMiddleware],
        endpoint: SharedEndpoint,
        settings: Mapping = None
    ) -> BaseMiddleware:
        """
        Build chain of responsibility from passed middlewares
        Also converts endpoint to executable middleware
        and append it to chain
        """
        assert isinstance(middlewares, list), 'Must be list of middlewares'

        self._middleware, it = None, None
        for m in middlewares:
            m = m(settings)

            if self._middleware is None and it is None:
                self._middleware, it = m, m
                continue

            it.set_next(m)
            it = m

        class EndpointAsMiddleware(BaseMiddleware):

            async def handle(
                self,
                request: BaseRequest
            ) -> Any:
                return await endpoint(*request.A, **request.K)

        endpoint_as_middleware = EndpointAsMiddleware()

        if it is None:
            self._middleware = endpoint_as_middleware
        else:
            it.set_next(endpoint_as_middleware)

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_options: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> SharedEndpoint: ...

    async def execute(
        self,
        A = [],
        K = {},
        D = None
    ) -> Any:
        story = create_story()
        story._wamps_ = self._wamps
        story._settings_ = self._settings
        request = self._create_request(A, K, D)
        story._client_ = request.client
        try:
            await self._signal_manager.fire('_entrypoint_.opened', story)
            output = await self._middleware(request)
        except BaseException as e:
            await self._signal_manager.fire('_entrypoint_.raised', story, e)

            if self._settings.debug:
                raise e
            try:
                e.__init__()
                name = f'{self._settings.uri_prefix}.error.{e.name}'
                payload = e.to_primitive()
            except:
                e = SomethingWentWrong()
                name = f'{self._settings.uri_prefix}.error.{e.name}'
                payload = e.to_primitive()
            raise ApplicationError(error=name, payload=payload)
        else:
            await self._signal_manager.fire('_entrypoint_.closed', story)
            return output

    def _create_request(
        self,
        A,
        K,
        D
    ) -> BaseRequest: ...


class CallEntrypoint(SharedEntrypoint):

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_options: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> RegisterEndpoint:
        return RegisterEndpoint(
            procedure, endpoint_options.validate_payload, user_serilizers
        )

    def _create_request(
        self,
        A,
        K,
        D
    ) -> CallRequest:
        """
        """
        return CallRequest(A, K, D)


class PublishEntrypoint(SharedEntrypoint):

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_options: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> SubscribeEndpoint:
        return SubscribeEndpoint(
            procedure, endpoint_options.validate_payload, user_serilizers
        )

    def _create_request(
        self,
        A,
        K,
        D
    ) -> PublishRequest:
        """
        """
        return PublishRequest(A, K, D)

