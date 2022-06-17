from typing import Callable, Iterable, Mapping, List, Any
from wampify.settings import EndpointOptions
from wampify.exceptions import InvalidPayload
from inspect import iscoroutinefunction as is_async
from pydantic import validate_arguments, ValidationError


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
        args: Iterable = [],
        kwargs: Mapping = {}
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
        args: Iterable = [],
        kwargs: Mapping = {}
    ) -> Any:
        """
        Validates input data, otherwise raises `InvalidPayload` 
        """
        try:
            return await super().execute(args=args, kwargs=kwargs)
        except ValidationError as e:
            if hasattr(self._procedure, 'model') and e.model is self._procedure.model:
                raise InvalidPayload(*e.errors())
            raise e


class RegisterEndpoint(SharedEndpoint): ...


class SubscribeEndpoint(SharedEndpoint): ...

