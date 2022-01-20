import logging
import traceback
from datetime import datetime


logger = logging.getLogger('wampify')


def mount(
    wampify
) -> None:
    from .request import CallRequest, PublishRequest

    def on_wamps_joined(
        wamps
    ):
        logger.info('WAMP Session joined')

    def on_wamps_leaved(
        wamps
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

    wampify._signal_manager.add('_wamps_.joined', on_wamps_joined)
    wampify._signal_manager.add('_wamps_.leaved', on_wamps_leaved)
    wampify._signal_manager.add('_entrypoint_.opened', on_entrypoint_opened)
    wampify._signal_manager.add('_entrypoint_.raised', on_entrypoint_raised)
    wampify._signal_manager.add('_entrypoint_.closed', on_entrypoint_closed)

