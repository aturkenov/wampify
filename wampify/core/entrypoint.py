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

    endpoint: SystemEndpoint
    story: Story
    settings: WampifySettings

    def __init__(
        self,
        procedure: Callable,
        user_settings: WampifySettings
    ) -> None:
        self.settings = user_settings
        self.endpoint = FactoryEndpoint(procedure)

    async def _release(
        self
    ) -> None:
        """
        """
        self.story = create_story()
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
        self
    ) -> Any:
        await self._release()
        try:
            output = await self.endpoint()
            await self._close_released()
            return output
        except BaseError as e:
            await self._raise_released()
            raise e

    async def __call__(
        self,
        *A,
    ) -> Any:
        return await self.execute(*A)


class SystemEntrypoint(FactoryEntrypoint):
    """
    """

    def __init__(
        self,
        procedure: Callable,
        user_settings: WampifySettings
    ) -> None:
        self.settings = user_settings
        self.endpoint = SystemEndpoint(procedure)


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
        self.endpoint = self._create_endpoint(
            procedure=procedure,
            endpoint_settings=endpoint_settings,
            user_serilizers=user_serializers
        )
        async def endpoint_as_middleware(request: BaseRequest):
            return await self.endpoint(*request.A, **request.K)
        self.middleware = self._build_responsibility_chain([
            *user_middlewares, endpoint_as_middleware
        ])

    def _build_responsibility_chain(
        self,
        M: List[Union[BaseMiddleware, SharedEndpoint]],
        settings: Mapping = None
    ) -> BaseMiddleware:
        """
        Builds chain of responsibility
        """
        assert isinstance(M, list), 'Must be list of middlewares'
        assert len(M) > 0, 'Must be more than zero middlewares'

        endpoint = M.pop()

        first, i = None, None
        for m in M:
            m = m.__init__(settings)

            if first is None and i is None:
                first, i = m, m
                continue

            i.set_next(m)
            i = m

        if i is None:
            return endpoint

        i.set_next(endpoint)
        return first

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
        await self._release()
        request = self._create_request(A, K, D)
        self.story.client = request.client
        try:
            output = await self.middleware(request)
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

