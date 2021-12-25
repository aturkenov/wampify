from .story import *
from .request import *
from .endpoint import *
from .session_pool import *
from .background_task import *
from .middleware import *
from settings import *
from autobahn.wamp.exception import *
from typing import *


class FactoryEntrypoint:
    """
    """

    story: Story
    settings: WampifySettings

    async def _release(
        self
    ) -> None:
        """
        """
        self.story.session_pool = SessionPool(self.settings.session_pool.factories)
        self.story.background_tasks = BackgroundTasks()

    async def _raise_released(
        self
    ) -> None:
        """
        """
        await self.story.session_pool.raise_released()

    async def _close_released(
        self
    ) -> None:
        """
        """
        await self.story.session_pool.close_released()

    async def execute(
        self,
        A,
        K,
        D
    ) -> Any: ...

    def _raise_handled_error(
        self,
        e: BaseError
    ) -> None:
        """
        """
        if self.settings.debug:
            raise e
        try:
            e.__init__()
            name = f'{self.settings.wamp.domain}.error.{e.name}'
            payload = e.to_primitive()
        except:
            e = SomethingWentWrong()
            name = f'{self.settings.wamp.domain}.error.{e.name}'
            payload = e.to_primitive()
        raise ApplicationError(error=name, payload=payload)

    async def __call__(
        self,
        *A,
    ) -> Any:
        return await self.execute(*A)


class SystemEntrypoint(FactoryEntrypoint):
    """
    """

    endpoint: SystemEndpoint

    def __init__(
        self,
        procedure: Callable
    ) -> None:
        self.endpoint = SystemEndpoint(
            procedure=procedure,
        )

    async def execute(
        self
    ) -> Any:
        self.story = create_story()
        await self._release()
        try:
            output = await self.endpoint()
            await self._close_released()
            return output
        except BaseError as e:
            await self._raise_released()
            self._raise_handled_error(e)


class SharedEntrypoint(FactoryEntrypoint):
    """
    """

    middleware: BaseMiddleware

    def __init__(
        self,
        procedure: Callable,
        endpoint_settings: EndpointSettings,
        user_settings: WampifySettings,
        user_middlewares: List[BaseMiddleware],
        user_serializers: List[Callable],
    ):
        self.settings = user_settings
        endpoint = self._create_endpoint(
            procedure=procedure,
            endpoint_settings=endpoint_settings,
            user_serilizers=user_serializers
        )
        self.middleware = build_rchain([*user_middlewares, endpoint])

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_settings: EndpointSettings,
        user_serilizers: List[Callable]
    ) -> SharedEndpoint: ...

    async def execute(
        self,
        A,
        K,
        D
    ) -> Any:
        self.story = create_story()
        request = self._create_request(A, K, D)
        self.story.client = request.client
        await self._release()
        try:
            output = await self.middleware.handle(request)
            await self._close_released()
            return output
        except BaseError as e:
            await self._raise_released()
            self._raise_handled_error(e)

    def _create_request(
        self,
        A,
        K,
        D
    ) -> BaseRequest: ...


class CallEntrypoint(SharedEntrypoint):
    """
    """

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_settings: EndpointSettings,
        user_serilizers: List[Callable]
    ) -> RegisterEndpoint:
        return RegisterEndpoint(
            procedure=procedure,
            validate_payload=endpoint_settings.validate_payload,
            serializers=user_serilizers
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
    """
    """

    def _create_endpoint(
        self,
        procedure: Callable,
        endpoint_settings: EndpointSettings,
        user_serilizers: List[Callable]
    ) -> SubscribeEndpoint:
        return SubscribeEndpoint(
            procedure=procedure,
            validate_payload=endpoint_settings.validate_payload,
            serializers=user_serilizers
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


