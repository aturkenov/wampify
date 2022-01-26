import logging
from datetime import datetime
from .signal_manager import wamps_signals, entrypoint_signals


logger = logging.getLogger('wampify')


def mount(
    wampify
) -> None:
    from .request import CallRequest, PublishRequest

    def on_wamps_joined(
        wamps,
        details
    ):
        logger.info('WAMP Session joined')

    def on_wamps_leaved(
        wamps,
        details
    ):
        logger.info('WAMP Session leaved')

    def on_entrypoint_opened(
        story
    ): ...

    def on_entrypoint_raised(
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

    def on_entrypoint_closed(
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

    wamps_signals.add('joined', on_wamps_joined)
    wamps_signals.add('leaved', on_wamps_leaved)
    entrypoint_signals.add('opened', on_entrypoint_opened)
    entrypoint_signals.add('raised', on_entrypoint_raised)
    entrypoint_signals.add('closed', on_entrypoint_closed)

