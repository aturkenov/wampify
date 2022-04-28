from typing import Any
import logging
from datetime import datetime, timedelta
import asyncio


logger = logging.getLogger('wampify')


def mount(
    wampify
) -> None:
    from wampify.story import Story
    from wampify.signals import wamps_signals, entrypoint_signals
    from wampify.requests import CallRequest, PublishRequest
    from wampify.exceptions import InvalidPayload

    def calculate_runtime(
        story: Story
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

    def get_method_name(
        story: Story
    ) -> str:
        if type(story._request_) == CallRequest:
            return 'RPC'
        if type(story._request_) == PublishRequest:
            return 'P&S'
        return 'UND'

    def get_client_name(
        story: Story
    ) -> str:
        caller = getattr(story._request_.details, 'caller_authid', None)
        publisher = getattr(story._request_.details, 'publisher_authid', None)
        return caller or publisher

    def get_request_arguments(
        story: Story
    ) -> str:
        return f'{story._request_.args}, {story._request_.kwargs}'

    def get_uri(
        story: Story
    ) -> str:
        procedure = getattr(story._request_.details, 'procedure', None)
        topic = getattr(story._request_.details, 'topic', None)
        return procedure or topic

    @wamps_signals.on
    def joined(
        wamps,
        details
    ):
        wamps.log._set_log_level('error')
        logger.info('WAMP Session joined')

    @wamps_signals.on
    def leaved(
        wamps,
        details
    ):
        logger.info('WAMP Session leaved')

    @entrypoint_signals.on
    def raised(
        story: Story,
        e: Exception
    ):
        if type(e) == asyncio.CancelledError:
            logger.warning(
                f'C '
                f'{get_method_name(story)} '
                f'{calculate_runtime(story).center(6)} '
                f'{get_client_name(story).center(36)} '
                f'{get_uri(story)}{get_request_arguments(story)}'
            )
        elif type(e) == InvalidPayload:
            logger.warning(
                f'W '
                f'{get_method_name(story)} '
                f'{calculate_runtime(story).center(6)} '
                f'{get_client_name(story).center(36)} '
                f'{get_uri(story)}{get_request_arguments(story)} -> {e.__class__.__name__}'
            )
        elif hasattr(story, '_request_'):
            logger.exception(
                f'E '
                f'{get_method_name(story)} '
                f'{calculate_runtime(story).center(6)} '
                f'{get_client_name(story).center(36)} '
                f'{get_uri(story)}{get_request_arguments(story)}'
            )
        else:
            logger.exception('something went wrong')

    @entrypoint_signals.on
    def closed(
        story: Story
    ):
        if hasattr(story, '_request_'):
            logger.info(
                f'I '
                f'{get_method_name(story)} '
                f'{calculate_runtime(story).center(6)} '
                f'{get_client_name(story).center(36)} '
                f'{get_uri(story)}(...) '
            )

