from .story import *
from .request import *
from .endpoint import *
from .session_pool import *
from .background_task import *
from .middleware import *
from settings import *
import asyncio
from multiprocessing import Process
from autobahn.wamp import ISession as WAMPIS
from autobahn.wamp.exception import ApplicationError


class Entrypoint:
    """
    Entrypoint creates story, execute required resources and endpoint.
    If something went wrong, raise released resources and handles exception
    else returns output and close released resources

    - `procedure`
    - `user_settings`
    """

    _story: Story
    _endpoint: Endpoint 
    _settings: WampifySettings
    _wamps: WAMPIS

    def __init__(
        self,
        procedure: Callable,
        user_settings: WampifySettings,
        wamps: WAMPIS,
    ) -> None:
        self._endpoint = Endpoint(procedure)
        self._settings = user_settings
        self._wamps = wamps

    async def execute(
        self,
        A = [],
        K = {},
        D = None
    ) -> Any:
        self._story = create_story()
        self._story.wamps = self._wamps
        self._story.session_pool = SessionPool(
            self._settings.session_pool.factories
        )
        try:
            output = await self._endpoint(*A, **K)
        except BaseException as E:
            await self._story.session_pool.raise_released()
            raise E
        else:
            await self._story.session_pool.close_released()
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
        endpoint_settings: EndpointOptions,
        wamps: WAMPIS,
        user_settings: WampifySettings,
        user_middlewares: List[BaseMiddleware],
        user_serializers: List[Callable],
    ):
        self._settings = user_settings
        self._wamps = wamps
        self._endpoint = self._create_endpoint(
            procedure, endpoint_settings, user_serializers
        )
        self._build_responsibility_chain(
            user_middlewares, self._endpoint
        )

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
        endpoint_settings: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> SharedEndpoint: ...

    async def _execute_background_tasks(
        self
    ) -> None:
        """
        If queue not empty, execute background tasks, 
        in another process and new asyncio event loop
        """
        background_tasks = self._story.background_tasks.get_list()

        def in_another_process():
            loop = asyncio.new_event_loop()
            for p, a, k in background_tasks:
                entrypoint = Entrypoint(p, self._settings)
                loop.run_until_complete(entrypoint(*a, **k))

        if len(background_tasks) == 0:
            return

        p = Process(target=in_another_process)
        p.start()

    async def execute(
        self,
        A = [],
        K = {},
        D = None
    ) -> Any:
        self._story = create_story()
        self._story.wamps = self._wamps
        self._request = self._create_request(A, K, D)
        self._story.session_pool = SessionPool(
            self._settings.session_pool.factories
        )
        self._story.background_tasks = BackgroundTasks()
        self._story.client = self._request.client
        try:
            output = await self._middleware(self._request)
        except BaseException as e:
            await self._story.session_pool.raise_released()
 
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
            await self._execute_background_tasks()
            await self._story.session_pool.close_released()
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
        endpoint_settings: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> RegisterEndpoint:
        return RegisterEndpoint(
            procedure, endpoint_settings.validate_payload, user_serilizers
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
        endpoint_settings: EndpointOptions,
        user_serilizers: List[Callable]
    ) -> SubscribeEndpoint:
        return SubscribeEndpoint(
            procedure, endpoint_settings.validate_payload, user_serilizers
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

