from core.story import *
from typing import *


class RCSettings:
    """
    """

    name: str
    disabled = False


class BaseRC:
    """
    """

    _next: 'BaseRC'
    _settings: Mapping

    class Settings(RCSettings):
        name = 'base'

    def sget(self, k: str):
        assert type(k) == str
        d = getattr(self.Settings, k)
        return self._settings.get(f'RC.{self.Settings.name}.{k}', d)

    async def call_next(
        self,
        scope: Mapping
    ) -> Awaitable:
        """
        """
        if self._next is None:
            raise RuntimeError
        return await self._next().handle(scope)

    async def handle(
        self,
        scope: Mapping
    ):
        """
        """
        raise NotImplementedError


class RChain(BaseRC):
    """
    Represents basic CoR (Chain of Responsibility) pattern
    """

    story: Story

    def __init__(
        self
    ):
        self.story = get_current_story()

    class Settings(RCSettings):
        name = 'RChain'

    async def handle(
        self,
        scope: Mapping
    ):
        """
        """


RChainsDT = Iterable[RChain]


def build_responsibility_chain(
    RCs: RChainsDT,
    settings: Mapping = {}
) -> RChain:
    """
    Builds chain of responsibility
    """
    first, i = None, None
    for chain in RCs:
        if first is None and i is None:
            first, i = chain, chain
            continue

        i._next = chain
        i._settings = settings
        i = chain

    return first

