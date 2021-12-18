from .story import *
from .endpoint import *
from .session_pool import *
from .background_task import *
from middleware import *
from settings import *
from autobahn.wamp.exception import *
from typing import *


class BaseEntrypoint:
    """
    """
    settings: WampifySettings
    story: Story
    middleware: BaseMiddleware

    def __init__(
        self,
        procedure: Union[Awaitable, Callable],
        endpoint_settings: EndpointSettings,
        user_settings: WampifySettings,
        user_middlewares: List[BaseMiddleware],
        user_serializers: List[Callable],
    ):
        self.settings = user_settings
        endpoint = Endpoint(
            procedure=procedure,
            validate_payload=endpoint_settings.validate_payload,
            serializers=user_serializers
        )
        endpoint_middleware = EndpointMiddleware
        endpoint_middleware.endpoint = endpoint
        self.middleware = build_rchain([*user_middlewares, endpoint_middleware])

    def handle_error(
        self,
        e: Exception
    ) -> Error:
        """
        """
        if self.settings.debug:
            return e
        try:
            e.__init__()
            name = f'{self.settings.wamp.domain}.error.{e.name}'
            payload = e.to_primitive()
        except:
            e = SomethingWentWrong()
            name = f'{self.settings.wamp.domain}.error.{e.name}'
            payload = e.to_primitive()
        return ApplicationError(error=name, payload=payload)

    async def release_required(
        self
    ) -> None:
        """
        """
        self.story.session_pool = SessionPool(self.settings.session_pool.factories)
        self.story.background_tasks = BackgroundTasks()

    async def raise_released(
        self
    ) -> None:
        """
        """
        await self.story.session_pool.raise_released()

    async def close_released(
        self
    ) -> None:
        """
        """
        await self.story.session_pool.close_released()

    async def enter(
        self,
        A,
        K,
        D
    ) -> Any: ...

    async def __call__(
        self,
        A,
        K,
        D
    ) -> Any:
        return await self.enter(A, K, D)


class CallEntrypoint(BaseEntrypoint):
    """
    """

    async def enter(
        self,
        A,
        K,
        D
    ) -> Any:
        """
        """
        self.story = create_story()
        request = CallRequest(A, K, D)
        self.story.client = request.client
        await self.release_required()
        try:
            output = await self.middleware.handle(request)
            await self.close_released()
            return output
        except BaseException as e:
            await self.raise_released()
            raise self.handle_error(e)


class PublishEntrypoint(BaseEntrypoint):
    """
    """

    async def enter(
        self,
        A,
        K,
        D
    ) -> Any:
        """
        """
        self.story = create_story()
        request = PublishRequest(A, K, D)
        self.story.client = request.client
        await self.release_required()
        try:
            output = await self.middleware.handle(request)
            await self.close_released()
            return output
        except BaseException as e:
            await self.raise_released()
            raise self.handle_error(e)

