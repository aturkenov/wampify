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
    ) -> 'WampifyJob':
        return WampifyJob(interval, self)


class WampifyJob(schedule.Job):

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


def _initialize_scheduler_process(
    wampify,
    update_interval: int = 1
):
    """
    Execute pending jobs every `update_interval` seconds
    """
    from wampify.entrypoints import Entrypoint

    def call_async(
        __procedure__,
        *A: Iterable,
        **K: Mapping
    ):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(__procedure__(*A, **K))

    for j in wampify.schedule.get_jobs():
        entrypoint = Entrypoint(j.procedure, wampify.settings, None)
        _ = functools.partial(call_async, entrypoint)
        j.replace_procedure(_)

    update_interval = 1
    while True:
        wampify.schedule.run_pending()
        time.sleep(update_interval)


def mount(
    wampify,
    update_interval: int = 1,
    logging_level = logging.DEBUG
) -> None:
    """
    Mounts scheduling module in wampify

    Executes scheduled jobs in background process, when WAMP session is joined

    - `logging_level` schedule library logger level
    - `update_interval` update interval for executing pending tasks in seconds
    """
    from wampify.signals import wamps_signals

    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging_level)

    wampify.schedule = WampifyScheduler()

    # TODO required to distribute execution of jobs
    # TODO from different types of polls
    process = multiprocessing.Process(
        target=_initialize_scheduler_process,
        kwargs={
            'wampify': wampify,
            'update_interval': update_interval
        }
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
        process.close()
        process.join()

