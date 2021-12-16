import asyncio
from typing import *


class BaseSessionFactory:
    """
    """

    async def on_release(self):
        """
        """

    async def on_raise(self, e):
        """
        """

    async def on_close(self):
        """
        """


SessionName = NewType('SessionName', str)


class FactoryDoesNotExist(BaseException):
    """
    """


class SessionPool:
    """
    """

    _factories: Mapping[SessionName, BaseSessionFactory] = {}
    _released: Mapping[SessionName, BaseSessionFactory] = {}

    def __init__(
        self,
        factories = {}
    ):
        """
        """
        self._released = {}
        self._factories = factories

    def _get_factory(
        self,
        name: SessionName
    ) -> BaseSessionFactory:
        """
        """
        factory = self._factories.get(name, ...)
        if factory is ...:
            raise FactoryDoesNotExist
        return factory

    def _get_released(
        self,
        name: SessionName = ...
    ) -> Union[BaseSessionFactory, List[BaseSessionFactory]]:
        """
        """
        if name is ...:
            return self._released.values()
        instance = self._released.get(name)
        return instance

    def _is_released(
        self,
        name: SessionName
    ):
        """
        """
        try:
            self._get_released(name)
        except:
            return False
        return True

    def _get_returning(
        self,
        name: SessionName
    ) -> Any:
        """
        """
        instance = self._get_released(name)
        return instance.__returning

    async def _produce(
        self,
        name: SessionName
    ):
        """
        """
        factory = self._get_factory(name)
        instance = factory()
        self._released[name] = instance
        instance.__returning = await instance.on_release()

    async def release(
        self,
        name: SessionName
    ):
        """
        """
        if not self._is_released(name):
            await self._produce(name)
        return self._get_returning(name)

    async def raise_released(
        self,
        e,
        name: SessionName = ...
    ):
        """
        """
        I = self._get_released(name)
        if not isinstance(I, Iterable):
            I = [I]
        C = [i.on_raise(e) for i in I]
        await asyncio.gather(*C)

    async def close_released(
        self,
        name: SessionName = ...
    ):
        """
        """
        I = self._get_released(name)
        if not isinstance(I, Iterable):
            I = [I]
        C = [i.on_close() for i in I]
        await asyncio.gather(*C)

