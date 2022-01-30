import logging
from datetime import datetime
from .signal_manager import wamps_signals, entrypoint_signals


logger = logging.getLogger('wampify')


def mount(
    wampify
) -> None:
    from .request import CallRequest, PublishRequest

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
    def opened(
        story
    ): ...

    @entrypoint_signals.on
    def raised(
        story,
        e
    ):
        def calculate_runtime() -> str:
            return str(datetime.utcnow() - story._request_.sent_time)

        def get_method() -> str:
            if type(story._request_) == CallRequest:
                return 'RPC'
            if type(story._request_) == PublishRequest:
                return 'PUBLISH'
            return 'UNDEFINED'

        def get_client():
            return str(story._request_.client.i)

        def get_request_arguments():
            return str(story._request_.A) + str(story._request_.K)

        logger.exception(
            f'{calculate_runtime()}ms ERROR {get_method()}! {get_client()} '
            f'{story._request_.URI}({get_request_arguments()})'
        )

    @entrypoint_signals.on
    def closed(
        story
    ):
        def calculate_runtime() -> str:
            return str(datetime.utcnow() - story._request_.sent_time)

        def get_method() -> str:
            if type(story._request_) == CallRequest:
                return 'RPC'
            if type(story._request_) == PublishRequest:
                return 'PUBLISH'
            return 'undefined'

        def get_client():
            return str(story._request_.client.i)

        logger.info(
            f'{calculate_runtime()}ms {get_method()}! {get_client()} '
            f'{story._request_.URI}'
        )

