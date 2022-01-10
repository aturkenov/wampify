from typing import *


class BackgroundTasks:

    _T: List[Tuple[Callable, Iterable, Mapping]]
 
    def __init__(
        self
    ):
        self._T = []

    def add(
        self,
        task: Union[Awaitable, Callable],
        *A: Iterable,
        **K: Mapping
    ) -> None:
        """
        """
        _ = task, A, K
        self._T.append(_)

    def get_list(
        self
    ) -> List[Tuple[Callable, Iterable, Mapping]]:
        return self._T

