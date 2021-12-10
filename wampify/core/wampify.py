from .story import *
from .wamp import *
from rchain import *
from .request import *
from .endpoint import Endpoint
from shared.serializer import serialize_primitive
from settings import KitchenSettings, get_validated_settings
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
        self.settings.RCs = [
            ErrorRC,
            *self.settings.RCs,
            EndpointRC
        ]
        self.settings.serializers.append(serialize_primitive)
        self.wamp = WAMPBackend(self.settings.wamp)

    def add_register(
        self,
        path: str,
        F: Union[Awaitable, Callable],
        validate = True,
        settings: Mapping = {}
    ) -> Awaitable:
        rchain = build_responsibility_chain(self.settings.RCs, settings)
        endpoint = Endpoint(
            path,
            F,
            validate_payload=validate,
            serializers=self.settings.serializers
        )

        async def called(
            *A,
            _D,
            **K,
        ):
            create_story()
            r = Request(_D, endpoint, A, K)
            return await rchain().handle({'request': r})

        self.wamp._cart.register(
            path,
            called,
            {
                'details_arg': '_D'
            }
        )
        return called

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
        validate = True,
        settings: Mapping = {}
    ) -> Awaitable:
        rchain = build_responsibility_chain(self.settings.RCs, settings)
        endpoint = Endpoint(
            path,
            F,
            validate_payload=validate,
            serializers=self.settings.serializers
        )

        async def published(
            *A,
            _D,
            **K,
        ):
            create_story()
            r = Request(_D, endpoint, A, K)
            return await rchain().handle({'request': r})

        self.wamp._cart.subscribe(
            path,
            published,
            {
                'details_arg': '_D'
            }
        )
        return published

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

