from wampify.client import Client
from autobahn.wamp import CallDetails, EventDetails
from datetime import datetime
from typing import Any, Iterable, Mapping


class BaseRequest:
    """
    Represents a base request

    - `A` - requested arguments
    - `K` - requested keyword arguments
    - `D` - request details
    - `client` - requested client (wamp session)
    """

    A: Iterable[Any]
    K: Mapping[str, Any]
    D: Any
    URI: str
    sent_time: datetime
    client: Client

    def __init__(
        self,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
        D = None,
    ):
        self.A = A
        self.K = K
        self.D = D
        self.sent_time = datetime.utcnow()


class CallRequest(BaseRequest):
    """
    Represents a call request
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
            self.URI = D.procedure


class PublishRequest(BaseRequest):
    """
    Represents a publish request
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
            self.URI = D.topic

