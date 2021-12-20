from .error import *
from inspect import iscoroutinefunction as is_awaitable
from pydantic import ValidationError
from pydantic.decorator import ValidatedFunction
from shared.serializer import *
from typing import *


class _BaseEndpoint:
    """
    """

    _procedure: Union[Coroutine, Callable]

    def __init__(
        self,
        procedure: Union[Coroutine, Callable]
    ):
        assert callable(procedure), 'procedure must be `Callable`'
        self._procedure = procedure

    async def execute(
        self,
        *A,
        **K
    ) -> Any:
        if is_awaitable(self._procedure):
            return await self._procedure(*A, **K)
        else:
            return self._procedure(*A, **K)

    async def __call__(
        self,
        *A,
        **K
    ) -> Any:
        return await self.execute(*A, **K)


class SystemEndpoint(_BaseEndpoint):
    """
    """


class BaseEndpoint(_BaseEndpoint):
    """
    """

    _validate_payload: bool
    _pmodel: ValidatedFunction
    _serializers: Iterable[Callable]

    def __init__(
        self,
        procedure: Union[Awaitable, Callable],
        validate_payload = True,
        serializers: Iterable[Callable] = DEFAULT_SERIALIZERS
    ):
        assert callable(procedure), 'procedure must be `Callable`'
        self._procedure = procedure
        self._pmodel = ValidatedFunction(procedure, None)
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
        values = self._pmodel.build_values(A, K)

        if not self._validate_payload:
            return values

        try:
            self._pmodel.model(**values)
        except ValidationError as e:
            raise PayloadValidationError(
                cause=self._get_pydantic_validation_error_content(e)
            )

        return values

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
        """
        Executes procedure
        """
        payload = self._validate(*A, **K)

        if is_awaitable(self._procedure):
            output = await self._procedure(**payload)
        else:
            output = self._procedure(**payload)

        return self._serialize(output)


class RegisterEndpoint(BaseEndpoint):
    """
    """


class SubscribeEndpoint(BaseEndpoint):
    """
    """


