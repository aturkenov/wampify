import asyncio
import time
import multiprocessing
import schedule
import functools
import logging
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


def _initialize_scheduling_process(
    wampify
):
    """
    Execute scheduled jobs
    """
    from wampify.entrypoints import Entrypoint

    loop = asyncio.new_event_loop()

    def call_async(
        __procedure__,
        *A: Iterable,
        **K: Mapping
    ):
        loop.run_until_complete(__procedure__(*A, **K))

    for j in wampify.schedule.get_jobs():
        entrypoint = Entrypoint(j.procedure, wampify.settings, None)
        _ = functools.partial(call_async, entrypoint)
        j.replace_procedure(_)

    interval = 1
    while True:
        wampify.schedule.run_pending()
        time.sleep(interval)


def mount(
    wampify
) -> None:
    """
    """
    from wampify.signals import wamps_signals

    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.DEBUG)

    wampify.schedule = WampifyScheduler()

    process = multiprocessing.Process(
        target=_initialize_scheduling_process,
        kwargs={'wampify': wampify}
    )

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

