from wampify.settings import EndpointOptions
from wampify.requests import BaseRequest
from wampify.exceptions import InvalidPayload
from inspect import iscoroutinefunction as is_async
from pydantic import validate_arguments, ValidationError
from typing import Callable, Mapping, List, Any


class Endpoint:
    """
    Endpoint last point to execute procedure
    """

    options: EndpointOptions
    _procedure: Callable
    _is_async: bool

    def __init__(
        self,
        procedure: Callable,
        options: Mapping = {}
    ):
        assert callable(procedure), 'procedure must be Callable'
        self._is_async = is_async(procedure)
        self.setup_procedure(procedure, options)

    def setup_procedure(
        self,
        procedure: Callable,
        options: Mapping = {}
    ) -> None:
        self.options = EndpointOptions(**options)
        self._procedure = procedure

    async def execute(
        self,
        *args,
        **kwargs
    ) -> Any:
        """
        Executes procedure
        """
        if self._is_async:
            return await self._procedure(*args, **kwargs)
        return self._procedure(*args, **kwargs)

    async def __call__(
        self,
        *args,
        **kwargs
    ) -> Any:
        return await self.execute(*args, **kwargs)


class SharedEndpoint(Endpoint):
    """
    """

    def _get_pydantic_validation_error_content(
        self,
        e: ValidationError
    ) -> List:
        return e.errors()

    def setup_procedure(
        self,
        procedure: Callable,
        options: Mapping = {}
    ):
        super().setup_procedure(procedure, options)
        self.options.payload.setdefault('arbitrary_types_allowed', True)
        self.options.payload.setdefault('underscore_attrs_are_private', True)
        validate = self.options.payload.get('validate', True)
        if validate:
            self._procedure = validate_arguments(
                self._procedure, config=self.options.payload
            )

    async def execute(
        self,
        *args,
        request: BaseRequest = None,
        **kwargs,
    ) -> Any:
        """
        Validates input data, otherwise raises `InvalidPayload` 
        """
        if isinstance(request, BaseRequest):
            args, kwargs = request.args, request.kwargs
        try:
            return await super().execute(*args, **kwargs)
        except ValidationError as e:
            cause = self._get_pydantic_validation_error_content(e)
            raise InvalidPayload(*cause)


class RegisterEndpoint(SharedEndpoint): ...


class SubscribeEndpoint(SharedEndpoint): ...

