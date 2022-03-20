from wampify.exceptions import PayloadValidationError
from wampify.settings import (
    EndpointOptions
)
from inspect import iscoroutinefunction as is_async
from pydantic import validate_arguments, ValidationError
from typing import Callable, Iterable, Mapping, Any


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
        self._procedure = procedure
        self._is_async = is_async(procedure)
        self.options = EndpointOptions(**options)

    async def execute(
        self,
        *A,
        **K
    ) -> Any:
        """
        Executes procedure
        """
        if self._is_async:
            return await self._procedure(*A, **K)
        else:
            return self._procedure(*A, **K)

    async def __call__(
        self,
        *A,
        **K
    ) -> Any:
        return await self.execute(*A, **K)


class SharedEndpoint(Endpoint):
    """
    """

    def __init__(
        self,
        procedure: Callable,
        options: EndpointOptions
    ):
        super().__init__(procedure, options)
        if self.options.validate_payload:
            self._procedure = validate_arguments(self._procedure)
 
    def _get_pydantic_validation_error_content(self, e: ValidationError):
        return e.errors()

    async def execute(
        self,
        *A: Iterable,
        **K: Mapping
    ) -> Any:
        """
        Validates input data, otherwise raises `PayloadValidationError` 
        """
        try:
            if self._is_async:
                output = await self._procedure(*A, **K)
            else:
                output = self._procedure(*A, **K)
        except ValidationError as e:
            raise PayloadValidationError(
                cause=self._get_pydantic_validation_error_content(e)
            )
        else:
            return output


class RegisterEndpoint(SharedEndpoint): ...


class SubscribeEndpoint(SharedEndpoint): ...

