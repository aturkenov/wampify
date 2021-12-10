from core.story import *
from typing import *


class BaseInMemoryCache:
    """
    In Memory Cache
    """

    _cache: Mapping[Hashable, Any]

    def __init__(
        self
    ):
        self.reset()

    def reset(
        self
    ):
        """
        """
        self._cache = {}

    def get(
        self,
        key: Hashable
    ) -> Any:
        return self._cache.get(key, None)

    def set(
        self,
        key: Hashable,
        data: Any = None
    ) -> Any:
        self._cache[key] = data

    def __getitem__(
        self,
        key: Hashable
    ) -> Any:
        return self.get(key)

    def __setitem__(
        self,
        key: Hashable,
        data: Any = None
    ) -> Any:
        self.set(key, data)


class BaseWService:
    """
    """

    story: Story

    def __init__(
        self
    ):
        self.story = get_current_story()


class WService(BaseWService):
    """
    """

