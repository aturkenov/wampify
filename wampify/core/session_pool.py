import asyncio
from .session_factory import ISessionFactory
from .error import *
from typing import *


class SessionPool:
    """
    ### Returns new instance of session factory, if is not released yet

    SessionPool accepts map of factories
    >>> factories = {
    >>>     'alchemy': AlchemySessionFactory
    >>> }
    >>> session_pool = SessionPool(factories)
    >>> alchemy_session = session_pool.release('alchemy')

    If something went wrong,
    REQUIRED TO RAISE already released (initialized) instances,
    otherwise REQUIRED TO CLOSE them
    >>> try:
    >>>     # something happend here
    >>> except:
    >>>     session_pool.raise_released()
    >>> else:
    >>>     session_pool.close_released()
    """

    _factories: Mapping[str, ISessionFactory] = {}
    _released: Mapping[str, ISessionFactory] = {}

    def __init__(
        self,
        factories = {}
    ):
        self._released = {}
        self._factories = factories

    def _get_factory(
        self,
        name: str
    ) -> ISessionFactory:
        """
        Returns not produced session factory from `self._factories`,
        otherwise if factory does not exists
        raises `FactoryDoesNotExists` exception 
        """
        factory = self._factories.get(name, ...)
        if factory is ...:
            raise FactoryDoesNotExist
        return factory

    def _get_released(
        self,
        name: str = ...
    ) -> Union[ISessionFactory, List[ISessionFactory]]:
        """
        Returns already released (initialized) session factory
        """
        if name is ...:
            return self._released.values()
        instance = self._released.get(name)
        return instance

    def _is_released(
        self,
        name: str
    ) -> bool:
        """
        Returns True if session factory already released else False
        """
        try:
            self._get_released(name)
        except:
            return False
        return True

    def _get_returning(
        self,
        name: str
    ) -> Any:
        """
        Returns already released session factory instance
        """
        instance = self._get_released(name)
        return instance._returning

    async def _produce(
        self,
        name: str
    ):
        """
        Produces new instance of session factory
        and puts it in `self._released`
        """
        factory = self._get_factory(name)
        instance = factory()
        self._released[name] = instance
        instance._returning = await instance.on_release()

    async def release(
        self,
        name: str
    ) -> Any:
        """
        Returns new instance of session factory,
        if is not released yet
        """
        if not self._is_released(name):
            await self._produce(name)
        return self._get_returning(name)

    async def raise_released(
        self,
        name: str = ...
    ):
        """
        If something went wrong,
        raises already released (initialized) instances
        """
        I = self._get_released(name)
        if not isinstance(I, Iterable):
            I = [I]
        C = [i.on_raise() for i in I]
        await asyncio.gather(*C)

    async def close_released(
        self,
        name: str = ...
    ):
        """
        Close already released (initialized) instances
        """
        I = self._get_released(name)
        if not isinstance(I, Iterable):
            I = [I]
        C = [i.on_close() for i in I]
        await asyncio.gather(*C)

