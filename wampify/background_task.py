from .signal_manager import entrypoint_signals
from typing import List, Tuple, Callable, Iterable, Mapping


class BackgroundTasks:

    _T: List[Tuple[Callable, Iterable, Mapping]]
 
    def __init__(
        self
    ):
        self._T = []

    def add(
        self,
        task: Callable,
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


def mount(
    wampify
) -> None:
    import asyncio
    from multiprocessing import Process
    from .entrypoint import Entrypoint

    @entrypoint_signals.on
    def opened(
        story
    ):
        story._background_tasks_ = BackgroundTasks()

    @entrypoint_signals.on
    def closed(
        story
    ) -> None:
        """
        If queue not empty, execute background tasks, 
        in another process and new asyncio event loop
        """
        btasks = story._background_tasks_.get_list()

        def in_another_process():
            loop = asyncio.new_event_loop()
            for p, a, kw in btasks:
                entrypoint = Entrypoint(p, story._settings_, None)
                loop.run_until_complete(entrypoint(*a, **kw))

        if len(btasks) == 0:
            return

        p = Process(target=in_another_process)
        p.start()

