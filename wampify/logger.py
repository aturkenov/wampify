import logging
from datetime import datetime, timedelta
from wampify.signals import wamps_signals, entrypoint_signals
from typing import Any


logger = logging.getLogger('wampify')


def mount(
    wampify
) -> None:
    from wampify.story import Story
    from wampify.requests import CallRequest, PublishRequest

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
            return 'PUBLISH'
        return 'UNDEFINED'

    def get_client_name(
        story: Story
    ) -> Any:
        return story._request_.client.i

    def get_request_arguments(
        story: Story
    ) -> str:
        return f'{story._request_.A}, {story._request_.K}'

    @wamps_signals.on
    def joined(
        wamps,
        details
    ):
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
        e
    ):
        if hasattr(story, '_request_'):
            logger.exception(
                f'{calculate_runtime(story)} '
                f'{get_client_name(story)} '
                f'{get_method_name(story)} '
                f'{story._request_.URI} {get_request_arguments(story)}'
            )
        else:
            logger.exception('something went wrong')

    @entrypoint_signals.on
    def closed(
        story: Story
    ):
        if hasattr(story, '_request_'):
            logger.info(
                f'{calculate_runtime(story)} '
                f'{get_client_name(story)} ;) '
                f'{get_method_name(story)} '
                f'{story._request_.URI}(...) '
            )

