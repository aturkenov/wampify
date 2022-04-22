from wampify.story import *
from wampify.requests import BaseRequest, CallRequest, PublishRequest
from wampify.endpoints import (
    Endpoint, SharedEndpoint, RegisterEndpoint, SubscribeEndpoint
)
from wampify.middlewares import BaseMiddleware
from wampify.signals import entrypoint_signals
from wampify.exceptions import SomethingWentWrong
from wampify.settings import WampifySettings
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

    endpoint: Endpoint 
    _settings: WampifySettings
    _wamps: WAMPIS

    def __init__(
        self,
        procedure: Callable,
        user_settings: WampifySettings,
        wamps: WAMPIS
    ) -> None:
        self.endpoint = Endpoint(procedure)
        self._settings = user_settings
        self._wamps = wamps

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
            await entrypoint_signals.fire('opened', story)
            output = await self.endpoint(*A, **K)
        except BaseException as e:
            await entrypoint_signals.fire('raised', story, e)
        else:
            await entrypoint_signals.fire('closed', story)
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
        endpoint_options: Mapping,
        user_settings: WampifySettings,
        user_middlewares: List[BaseMiddleware],
        wamps: WAMPIS
    ):
        self._settings = user_settings
        self.endpoint = self._create_endpoint(procedure, endpoint_options)
        self._build_responsibility_chain(user_middlewares)
        self._wamps = wamps

    def _build_responsibility_chain(
        self,
        middlewares: List[BaseMiddleware]
    ) -> BaseMiddleware:
        """
        Build chain of responsibility from passed middlewares
        Also converts endpoint to executable middleware
        and append it to chain
        """
        assert isinstance(middlewares, list), 'Must be list of middlewares'
        endpoint = self.endpoint

        self._middleware, it = None, None
        for m in middlewares:
            m = m(self._settings, endpoint.options)

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

        endpoint_as_middleware = EndpointAsMiddleware(self._settings, endpoint.options)

        if it is None:
            self._middleware = endpoint_as_middleware
        else:
            it.set_next(endpoint_as_middleware)

    def _create_endpoint(
        self,
        procedure: Callable,
        options: Mapping
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
        story._request_ = self._create_request(A, K, D)
        try:
            await entrypoint_signals.fire('opened', story)
            output = await self._middleware(story._request_)
        except BaseException as e:
            await entrypoint_signals.fire('raised', story, e)

            try:
                e.__init__()
                name = f'{self._settings.preuri}.error.{e.name}'
                payload = e.to_primitive()
            except:
                e = SomethingWentWrong()
                name = f'{self._settings.preuri}.error.{e.name}'
                payload = e.to_primitive()
            raise ApplicationError(error=name, payload=payload)
        else:
            await entrypoint_signals.fire('closed', story)
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
        options: Mapping
    ) -> RegisterEndpoint:
        return RegisterEndpoint(procedure, options)

    def _create_request(
        self,
        A,
        K,
        D
    ) -> CallRequest:
        return CallRequest(A, K, D)


class PublishEntrypoint(SharedEntrypoint):

    def _create_endpoint(
        self,
        procedure: Callable,
        options: Mapping
    ) -> SubscribeEndpoint:
        return SubscribeEndpoint(procedure, options)

    def _create_request(
        self,
        A,
        K,
        D
    ) -> PublishRequest:
        return PublishRequest(A, K, D)

