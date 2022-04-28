from typing import Any, List, Union, Callable, Mapping
from functools import partial
from asyncio.exceptions import CancelledError
from wampify.story import *
from wampify.requests import BaseRequest, CallRequest, PublishRequest
from wampify.endpoints import (
    Endpoint, SharedEndpoint, RegisterEndpoint, SubscribeEndpoint
)
from wampify.signals import entrypoint_signals
from wampify.exceptions import SomethingWentWrong
from wampify.settings import WampifySettings
from autobahn.wamp import ISession as WAMPIS
from autobahn.wamp.exception import ApplicationError
from wampify.shared.camel_to_snake import camel_to_snake


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
    _exceptions_to_skip = (
        CancelledError,
    )

    def __init__(
        self,
        procedure: Callable,
        endpoint_options: Mapping,
        user_settings: WampifySettings,
        wamps: WAMPIS
    ) -> None:
        self.endpoint = Endpoint(procedure, endpoint_options)
        self.endpoint_options = self.endpoint.options
        self._settings = user_settings
        self._wamps = wamps

    async def execute(
        self,
        args = [],
        kwargs = {},
        details = None
    ) -> Any:
        story = create_story()
        story._wamps_ = self._wamps
        story._settings_ = self._settings
        story._endpoint_options_ = self.endpoint.options
        try:
            await entrypoint_signals.fire('opened', story)
            output = await self.endpoint(*args, **kwargs)
            await entrypoint_signals.fire('closed', story)
        except BaseException as e:
            await entrypoint_signals.fire('raised', story, e)
            if type(e) not in self._exceptions_to_skip:
                raise e
        else:
            return output

    async def __call__(
        self,
        *args,
        **kwargs
    ) -> Any:
        return await self.execute(*args, **kwargs)


class SharedEntrypoint(Entrypoint):

    endpoint: Union[SharedEndpoint, Callable]
    endpoint_options: EndpointOptions

    def __init__(
        self,
        procedure: Callable,
        endpoint_options: Mapping,
        user_settings: WampifySettings,
        user_middlewares: List[Callable],
        wamps: WAMPIS
    ):
        self._settings = user_settings
        self.endpoint = self._create_endpoint(procedure, endpoint_options)
        self.endpoint_options = self.endpoint.options
        self._build_responsibility_chain(user_middlewares)
        self._wamps = wamps

    def _build_responsibility_chain(
        self,
        middlewares: List[Callable]
    ) -> None:
        """
        Build chain of responsibility from passed middlewares, also appends endpoint
        Method must be executed after endpoint initialization!
        """
        assert isinstance(middlewares, list), 'Must be list of middlewares'
        i = len(middlewares) - 1
        while i > -1:
            mw = middlewares[i]
            self.endpoint = partial(mw, self.endpoint)
            i -= 1

    def _to_application_level_exception(
        self,
        exception: BaseException
    ) -> ApplicationError:
        """
        Generates `autobahn.wamp.exceptions.ApplicationError`
        from user exception

        Example:
        >>> class Denied(BaseException):
        >>>     cause = 'Service Denied!'

        Returns:
        >>> ApplicationError(
        >>>     'com.example.error.denied', 'Service Denied!'
        >>> )
        """
        _ename = getattr(exception, '__name__', None)
        if _ename is None:
            _eclass = getattr(exception, '__class__', SomethingWentWrong)
            _ename = _eclass.__name__
        ename = camel_to_snake(_ename)
        error_code = f'{self._settings.preuri}.error.{ename}'

        if len(exception.args) > 0:
            ecause = exception.args
            return ApplicationError(error_code, *ecause)
        else:
            ecause = getattr(exception, 'cause', SomethingWentWrong.cause)
            return ApplicationError(error_code, ecause)

    def _create_endpoint(
        self,
        procedure: Callable,
        options: Mapping
    ) -> SharedEndpoint: ...

    async def execute(
        self,
        args = [],
        kwargs = {},
        details = None
    ) -> Any:
        story = create_story()
        story._wamps_ = self._wamps
        story._settings_ = self._settings
        story._request_ = self._create_request(args=args, kwargs=kwargs, details=details)
        story._endpoint_options_ = self.endpoint_options
        try:
            await entrypoint_signals.fire('opened', story)
            output = await self.endpoint(request=story._request_)
            await entrypoint_signals.fire('closed', story)
        except BaseException as e:
            await entrypoint_signals.fire('raised', story, e)
            if type(e) not in self._exceptions_to_skip:
                raise self._to_application_level_exception(e)
        else:
            return output

    def _create_request(
        self,
        args = [],
        kwargs = {},
        details = None
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
        args,
        kwargs,
        details
    ) -> CallRequest:
        return CallRequest(args, kwargs, details)


class PublishEntrypoint(SharedEntrypoint):

    def _create_endpoint(
        self,
        procedure: Callable,
        options: Mapping
    ) -> SubscribeEndpoint:
        return SubscribeEndpoint(procedure, options)

    def _create_request(
        self,
        args,
        kwargs,
        details
    ) -> PublishRequest:
        return PublishRequest(args, kwargs, details)

