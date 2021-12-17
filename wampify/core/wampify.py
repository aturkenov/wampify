from .wamp import *
from .request import *
from middleware import *
from .endpoint import *
from .session_pool import *
from .error import *
from autobahn.wamp.exception import ApplicationError
from shared.serializer import *
from settings import *
from typing import *


class Wampify:
    """
    """

    _M: List[BaseMiddleware]
    _serializers: List[Callable]
    settings: KitchenSettings
    wamp: WAMPBackend

    def __init__(
        self,
        settings: KitchenSettings
    ) -> None:
        self._M = []
        self._serializers = []
        self.settings = get_validated_settings(settings)
        self.wamp = WAMPBackend(self.settings.wamp)

    def add_middleware(
        self,
        m: Callable
    ) -> None:
        """
        """
        assert isinstance(m, BaseMiddleware), 'Must be BaseMiddleware'
        self._M.append(m)

    def add_serializer(
        self,
        F: Callable
    ) -> None:
        """
        """
        assert callable(F), 'Serializer must be callable'
        # TODO add some serialization tests here
        self._serializers.append(F)

    def _handle_error(
        self,
        e
    ) -> Union[BaseException, Mapping]:
        """
        """
        if self.settings.debug:
            return e
        try:
            e.__init__()
            name = f'{self.settings.wamp.domain}.{e.name}'
            payload = e.to_primitive()
        except:
            e = SomethingWentWrong()
            name = f'{self.settings.wamp.domain}.{e.name}'
            payload = e.to_primitive()
        return ApplicationError(error=name, payload=payload)

    async def _entrypoint(
        self,
        entrypoint: BaseMiddleware,
        request: BaseRequest
    ) -> Any:
        """
        """
        session_pool = SessionPool(self.settings.session_pool.factories)
        story = create_story()
        story.client = request.client
        story.session_pool = session_pool
        try:
            output = await entrypoint.handle(request)
            await session_pool.close_released()
            return output
        except BaseException as e:
            await session_pool.raise_released()
            raise self._handle_error(e)

    def add_register(
        self,
        path: str,
        F: Union[Awaitable, Callable],
        settings: EndpointSettings = {}
    ) -> Awaitable:
        """
        """
        endpoint_settings = EndpointSettings(**settings)
        endpoint = Endpoint(
            F, endpoint_settings.validate_payload, self._serializers
        )
        entrypoint = build_rchain(self._M)

        async def on_call(
            *A,
            _CALL_DETAILS_,
            **K,
        ):
            call_request = CallRequest(
                endpoint, _CALL_DETAILS_, A, K
            )
            return await self._entrypoint(
                entrypoint, call_request
            )

        self.wamp._cart.register(
            path, on_call, {
                'details_arg': '_CALL_DETAILS_'
            }
        )
        return on_call

    def add_subscribe(
        self,
        path: str,
        F: Union[Awaitable, Callable],
        settings: EndpointSettings = {}
    ) -> Awaitable:
        """
        """
        endpoint_settings = EndpointSettings(**settings)
        endpoint = Endpoint(
            F, endpoint_settings.validate_payload, self._serializers
        )
        entrypoint = build_rchain(self._M)

        async def on_publish(
            *A,
            _PUBLISH_DETAILS_,
            **K,
        ):
            publish_request = PublishRequest(
                endpoint, _PUBLISH_DETAILS_, A, K
            )
            return await self._entrypoint(
                entrypoint, publish_request
            )

        self.wamp._cart.subscribe(
            path, on_publish, {
                'details_arg': '_PUBLISH_DETAILS_'
            }
        )
        return on_publish

    def register(
        self,
        path: str,
        settings: Mapping = {}
    ) -> Awaitable:
        """
        """
        def decorate(
            F: Callable
        ):
            return self.add_register(
                path=path,
                F=F,
                settings=settings
            )
        return decorate

    def subscribe(
        self,
        path: str,
        settings: Mapping = {}
    ) -> Awaitable:
        """
        """
        def decorate(
            F: Callable
        ):
            return self.add_subscribe(
                path=path,
                F=F,
                settings=settings
            )
        return decorate

    def run(
        self,
        url: str = ...,
        start_loop = ...
    ) -> None:
        """
        """
        self.wamp.run(url=url, start_loop=start_loop)

