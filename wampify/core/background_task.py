from typing import *


class BackgroundTasks:
    """
    """

    _T: List
 
    def __init__(
        self
    ):
        self._T = []

    def add(
        self,
        task: Union[Awaitable, Callable],
        *A,
        **K
    ) -> None:
        """
        """
        _ = task, A, K
        self._T.append(_)

