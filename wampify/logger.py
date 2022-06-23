import asyncio
from datetime import datetime, timedelta
from sys import stdout
from typing import TYPE_CHECKING
from loguru import logger


if TYPE_CHECKING:
    from autobahn.wamp import ISession as WAMPIS, SessionDetails
    from wampify.story import Story
    from wampify.wampify import Wampify


class SessionStats:
    wamps_joined_time: datetime
    rpc_count = 0
    rpc_error_count = 0
    pns_count = 0
    pns_error_count= 0
    max_runtime: timedelta
    min_runtime: timedelta
    avg_runtime: timedelta


def loguru_format(state):
    if state['level'].name == 'SUCCESS':
        return '<b><g>{level.name[0]}</g></b> '\
            '{time:HH:mm:ss} '\
            '{extra[method]} '\
            '{extra[client]:^36} '\
            '{extra[procedure]}(...) '\
            '{extra[runtime]} '\
            '{message}\n'\
            '{exception}'
    if state['level'].name == 'WARNING':
        return '<b><y>{level.name[0]}</y></b> '\
            '{time:HH:mm:ss} '\
            '{extra[method]} '\
            '{extra[client]:^36} '\
            '{extra[procedure]}({extra[procedure_args]}) '\
            '{extra[runtime]} '\
            '{message}\n'\
            '{exception}'
    return '<b><r>{level.name[0]}</r></b> '\
        '{time:HH:mm:ss} '\
        '{extra[method]} '\
        '{extra[client]:^36} '\
        '{extra[procedure]}({extra[procedure_args]}) '\
        '{extra[runtime]} '\
        '{message}\n'\
        '{exception}'


loguru_configuration = {
    "handlers": [
        { "sink": stdout, "format": loguru_format }
    ]
}


def mount(
    wampify: 'Wampify'
) -> None:
    ON_WAMP_SESSION_JOIN_TEXT = \
        '<g><b>WAMP Session Joined!</b></g>\n'\
        '<b>Current Time</b>:              {current_time}\n'\
        '<b>Transport</b>:                 {transport}\n'\
        '<b>Router URL</b>:                {router_url}\n'\
        '<b>Realm</b>:                     {realm}\n'\
        '<b>Role</b>:                      {role}\n'\
        '<b>Session Number</b>:            {session}\n'\
        '<b>authid</b>:                    {authid}\n'

    ON_WAMP_SESSION_LEAVE_TEXT = \
        '<r><b>WAMP Session Leaved!</b></r>\n'\
        '<b>Session Lifetime</b>          {session_lifetime}\n'

    from wampify.signals import wamps_signals, entrypoint_signals
    from wampify.requests import CallRequest, PublishRequest
    from wampify.exceptions import InvalidPayload

    stats = SessionStats()
    logger.configure(**loguru_configuration)

    def calculate_runtime(
        story: 'Story'
    ) -> str:
        d = datetime.utcnow() - story._request_.sent_time
        if d >= timedelta(hours=1):
            return f'{d.seconds // 3600}H'
        if d >= timedelta(minutes=1):
            return f'{d.seconds // 60}M'
        if d >= timedelta(seconds=1):
            return f'{d.seconds}S'
        if d >= timedelta(milliseconds=1):
            return f'{d.microseconds // 1000}m'
        if d >= timedelta(microseconds=1):
            return f'{d.microseconds}ms'
        return f'{d}?'

    def get_request_method_name(
        story: 'Story'
    ) -> str:
        if type(story._request_) == CallRequest:
            return 'RPC'
        if type(story._request_) == PublishRequest:
            return 'P&S'
        return 'IDK'

    def get_client_name(
        story: 'Story'
    ) -> str:
        caller = getattr(story._request_.details, 'caller_authid', None)
        publisher = getattr(story._request_.details, 'publisher_authid', None)
        return caller or publisher

    def get_procedure_name(
        story: 'Story'
    ) -> str:
        procedure = getattr(story._request_.details, 'procedure', None)
        topic = getattr(story._request_.details, 'topic', None)
        return procedure or topic

    def get_procedure_arguments(
        story: 'Story'
    ) -> str:
        return f'{story._request_.args}, {story._request_.kwargs}'

    @wamps_signals.on
    def joined(
        wamps: 'WAMPIS',
        details: 'SessionDetails'
    ):
        stats.wamps_joined_time = datetime.now()
        logger.opt(raw=True, colors=True)\
            .debug(
                ON_WAMP_SESSION_JOIN_TEXT,
                current_time=stats.wamps_joined_time,
                router_url=wampify.settings.router.url,
                realm=details.realm,
                role=details.authrole,
                session=details.session,
                authid=details.authid,
                transport=details.transport,
            )

    @wamps_signals.on
    def leaved(
        wamps: 'WAMPIS',
        details: 'SessionDetails'
    ):
        current_time = datetime.now()
        logger.opt(raw=True, colors=True)\
            .debug(
                ON_WAMP_SESSION_LEAVE_TEXT,
                session_lifetime=current_time - stats.wamps_joined_time
            )

    @entrypoint_signals.on
    def raised(
        story: 'Story',
        e: Exception
    ):
        if not hasattr(story, '_request_'):
            logger.exception('something went wrong')
            return

        if type(e) == asyncio.CancelledError:
            logger.bind(
                    method=get_request_method_name(story),
                    runtime=calculate_runtime(story),
                    client=get_client_name(story),
                    procedure=get_procedure_name(story),
                    procedure_args=get_procedure_arguments(story)
                ).warning('Task was canceled!')
        elif type(e) == InvalidPayload:
            logger.bind(
                    method=get_request_method_name(story),
                    runtime=calculate_runtime(story),
                    client=get_client_name(story),
                    procedure=get_procedure_name(story),
                    procedure_args=get_procedure_arguments(story)
                ).warning('Invalid Payload!')
        else:
            logger.bind(
                    method=get_request_method_name(story),
                    runtime=calculate_runtime(story),
                    client=get_client_name(story),
                    procedure=get_procedure_name(story),
                    procedure_args=get_procedure_arguments(story)
                ).exception('')

    @entrypoint_signals.on
    def closed(
        story: 'Story'
    ):
        if hasattr(story, '_request_'):
            logger.bind(
                method=get_request_method_name(story),
                runtime=calculate_runtime(story),
                client=get_client_name(story),
                procedure=get_procedure_name(story),
                procedure_args=get_procedure_arguments(story)
            ).success('')

