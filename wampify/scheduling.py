import asyncio
import time
import multiprocessing
import schedule
import functools
from typing import Callable, Iterable, Mapping


class WampifyScheduler(schedule.Scheduler):

    def every(
        self,
        interval: int = 1
    ) -> 'WampifySchedulerJob':
        return WampifySchedulerJob(interval, self)


class WampifySchedulerJob(schedule.Job):

    @property
    def procedure(
        self
    ) -> Callable:
        return self.job_func.func

    def replace_procedure(
        self,
        procedure: Callable
    ) -> None:
        self.job_func = functools.partial(
            procedure,
            *self.job_func.args,
            **self.job_func.keywords
        )


def mount(
    wampify
) -> None:
    wampify.schedule = WampifyScheduler()
    interval = 1

    from wampify.signals import wamps_signals
    from wampify.entrypoints import Entrypoint

    def _():
        loop = asyncio.new_event_loop()

        def __(
            __ENTRYPOINT__,
            *A: Iterable,
            **K: Mapping
        ):
            loop.run_until_complete(__ENTRYPOINT__(*A, **K))

        for j in wampify.schedule.get_jobs():
            entrypoint = Entrypoint(j.procedure, wampify.settings, None)
            ___ = functools.partial(__, entrypoint)
            j.replace_procedure(___)

        while True:
            wampify.schedule.run_pending()
            time.sleep(interval)

    process = multiprocessing.Process(target=_)

    @wamps_signals.on
    def joined(
        session,
        details
    ):
        process.start()

    @wamps_signals.on
    def leaved(
        session,
        details
    ):
        process.join()

