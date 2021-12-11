from .wamp import *
from .request import *
from .endpoint import *
from rchain import *
from shared.serializer import *
from settings import *
from typing import *


class Wampify:
    """
    """

    settings: KitchenSettings
    wamp: WAMPBackend

    def __init__(
        self,
        settings: KitchenSettings
    ):
        self.settings = get_validated_settings(settings)
        self.wamp = WAMPBackend(self.settings.wamp)

    def add_register(
        self,
        path: str,
        F: Union[Awaitable, Callable],
        settings: EndpointSettings = {}
    ) -> Awaitable:
        endpoint_settings = EndpointSettings(**settings)
        rchain = build_rchain(
            self.settings.rchains, endpoint_settings.rchain
        )

        endpoint = Endpoint(
            F, endpoint_settings.validate_payload, self.settings.serializers
        )

        async def on_call(
            *A,
            _CALL_DETAILS,
            **K,
        ):
            r = CallRequest(
                endpoint, _CALL_DETAILS, A, K
            )
            return await rchain.handle(r)

        self.wamp._cart.register(
            path, on_call, {
                'details_arg': '_CALL_DETAILS'
            }
        )
        return on_call

    def register(
        self,
        path: str,
        validate = True,
        settings: Mapping = {}
    ) -> Awaitable:
        """
        """
        def decorate(
            F: Callable
        ):
            return self.add_register(
                path=path,
                F=F,
                validate=validate,
                settings=settings
            )
        return decorate

    def add_subscribe(
        self,
        path: str,
        F: Union[Awaitable, Callable],
        settings: EndpointSettings = {}
    ) -> Awaitable:
        endpoint_settings = EndpointSettings(**settings)
        rchain = build_rchain(
            self.settings.rchains, endpoint_settings.rchain
        )

        endpoint = Endpoint(
            F, endpoint_settings.validate_payload, self.settings.serializers
        )

        async def on_publish(
            *A,
            _PUBLISH_DETAILS,
            **K,
        ):
            r = PublishRequest(
                endpoint, _PUBLISH_DETAILS, A, K
            )
            return await rchain.handle(r)

        self.wamp._cart.subscribe(
            path, on_publish, {
                'details_arg': '_PUBLISH_DETAILS'
            }
        )
        return on_publish

    def subscribe(
        self,
        path: str,
        validate = True,
        settings: Mapping = {}
    ) -> Awaitable:
        """
        """
        def decorate(
            F: Callable
        ):
            return self.add_subscribe(
                path=path,
                F=F,
                validate=validate,
                settings=settings
            )
        return decorate

    def run(
        self,
        url: str = ...,
        start_loop = ...
    ):
        """
        """
        self.wamp.run(url=url, start_loop=start_loop)

