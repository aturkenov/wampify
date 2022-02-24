import asyncio
from concurrent.futures import ProcessPoolExecutor
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


def _initialize_background_process(
    wampify
):
    """
    """
    global __wampify__
    __wampify__ = wampify


def _call_async(
    tasks: List[Tuple[Callable, Iterable, Mapping]]
):
    from wampify.entrypoints import Entrypoint

    loop = asyncio.new_event_loop()
    for p, a, k in tasks:
        entrypoint = Entrypoint(p, __wampify__.settings, None)
        loop.run_until_complete(entrypoint(*a, **k))

async def _run(
    pool,
    tasks: List[Tuple[Callable, Iterable, Mapping]]
):
    loop = asyncio.get_running_loop()
    loop.run_in_executor(pool, _call_async, tasks)


def mount(
    wampify
) -> None:
    from wampify.signals import wamps_signals, entrypoint_signals

    max_workers = 2

    pool = ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_initialize_background_process,
        initargs=(wampify, )
    )

    @entrypoint_signals.on
    def opened(
        story
    ):
        story._background_tasks_ = BackgroundTasks()

    @entrypoint_signals.on
    async def closed(
        story
    ) -> None:
        """
        If queue not empty, execute background tasks, 
        in another process with new event loop
        """
        btasks = story._background_tasks_.get_list()

        if len(btasks) == 0:
            return

        await _run(pool, btasks)

    @wamps_signals.on
    async def leaved(
        session,
        details
    ):
        pool.shutdown()

