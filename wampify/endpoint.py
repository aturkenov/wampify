from .error_list import PayloadValidationError
from .shared.serializer import (
    is_primitive, serialize_primitive, DEFAULT_SERIALIZERS
)
from inspect import iscoroutinefunction as is_async
from pydantic import ValidationError
from pydantic.decorator import ValidatedFunction
from typing import Callable, Iterable, Mapping, Any


class Endpoint:
    """
    Endpoint last point to execute procedure
    """

    _procedure: Callable
    _is_async: bool

    def __init__(
        self,
        procedure: Callable
    ):
        assert callable(procedure), 'procedure must be Callable'
        self._procedure = procedure
        self._is_async = is_async(procedure)

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

    _validate_payload: bool
    _validated_function: ValidatedFunction
    _serializers: Iterable[Callable]

    def __init__(
        self,
        procedure: Callable,
        validate_payload = True,
        serializers: Iterable[Callable] = DEFAULT_SERIALIZERS
    ):
        super().__init__(procedure)
        self._validated_function = ValidatedFunction(procedure, None)
        self._validate_payload = validate_payload
        self._serializers = serializers
 
    def _get_pydantic_validation_error_content(self, e: ValidationError):
        return e.errors()

    def _validate(
        self,
        *A,
        **K
    ) -> Mapping[str, Any]:
        """
        Validates input data, otherwise raises `PayloadValidationError`
        """
        values = self._validated_function.build_values(A, K)

        if not self._validate_payload:
            return values

        try:
            payload = self._validated_function.model(**values)
        except ValidationError as e:
            raise PayloadValidationError(
                cause=self._get_pydantic_validation_error_content(e)
            )
        else:
            required_arguments = values.keys()
            return payload.dict(include=required_arguments)

    def _serialize(
        self,
        data: Any
    ) -> Any:
        """
        Tryies to serialize function output. First checks output is primitive,
        second with passed serializers, else with default serializer,
        otherwise raises `SerializationError` 
        """
        if is_primitive(data):
            return data

        for s in self._serializers:
            try:
                return s(data)
            except: ...

        try:
            return serialize_primitive(data)
        except: ...

    async def execute(
        self,
        *A,
        **K
    ) -> Any:
        payload = self._validate(*A, **K)

        if self._is_async:
            output = await self._procedure(**payload)
        else:
            output = self._procedure(**payload)

        return self._serialize(output)


class RegisterEndpoint(SharedEndpoint): ...


class SubscribeEndpoint(SharedEndpoint): ...

