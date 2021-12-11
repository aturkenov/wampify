from inspect import iscoroutinefunction as is_awaitable
from pydantic import ValidationError
from pydantic.decorator import ValidatedFunction
from shared.serializer import DEFAULT_SERIALIZERS, serialize_primitive
from . import error
from typing import *


class BaseEndpoint:
    """
    """

    _endpoint: Union[Awaitable, Callable]
    _validate_payload: bool
    _pmodel: ValidatedFunction
    _serializers: Iterable[Callable]

    def __init__(
        self,
        endpoint: Union[Awaitable, Callable],
        validate_payload = True,
        serializers: Iterable[Callable] = DEFAULT_SERIALIZERS
    ):
        assert callable(endpoint), 'endpoint must be `Callable`'
        self._endpoint = endpoint
        self._pmodel = ValidatedFunction(endpoint, None)
        assert type(validate_payload) == bool
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
        Validates
        """
        values = self._pmodel.build_values(A, K)

        if not self._validate_payload:
            return values

        try:
            self._pmodel.model(**values)
        except ValidationError as e:
            raise error.PayloadValidationError(
                cause=self._get_pydantic_validation_error_content(e)
            )

        return values

    def _serialize(
        self,
        data: Any
    ) -> Any:
        for s in self._serializers:
            try:
                return s(data)
            except: ...

        try:
            return serialize_primitive(data)
        except: ...

        raise error.SerializationError

    async def execute(
        self,
        *A,
        **K
    ) -> Any:
        """
        Executes
        """
        payload = self._validate(*A, **K)

        if is_awaitable(self._endpoint):
            output = await self._endpoint(**payload)
        else:
            output = self._endpoint(**payload)

        return self._serialize(output)

    async def __call__(
        self,
        *A,
        **K
    ) -> Any:
        return await self.execute(*A, **K)


class Endpoint(BaseEndpoint):
    """
    """

    # TODO annotations

