from .client import *
from autobahn.wamp import CallDetails, EventDetails
from typing import *


class BaseRequest:
    """
    """

    A: Iterable[Any]
    K: Mapping[str, Any]
    D: Any
    client: Client

    def __init__(
        self,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
        D = None
    ):
        self.A = A
        self.K = K
        self.D = D


class CallRequest(BaseRequest):
    """
    """

    D: CallDetails 

    def __init__(
        self,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
        D: CallDetails = None
    ):
        super().__init__(A, K, D)
        if D:
            self.client = Client(
                i=D.caller_authid,
                role=D.caller_authrole,
                session_i=D.caller
            )


class PublishRequest(BaseRequest):
    """
    """

    D: EventDetails

    def __init__(
        self,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
        D: EventDetails = None
    ):
        super().__init__(A, K, D)
        if D:
            self.client = Client(
                i=D.publisher_authid,
                role=D.publisher_authrole,
                session_i=D.publisher
            )

