from autobahn.wamp import CallDetails, EventDetails
from datetime import datetime
from typing import Any, Iterable, Mapping


class BaseRequest:
    """
    Represents a base request

    - `args` - requested arguments
    - `kwargs` - requested keyword arguments
    - `details` - request details
    - `sent_time` - request sent time
    """

    args: Iterable[Any]
    kwargs: Mapping[str, Any]
    details: Any
    sent_time: datetime

    def __init__(
        self,
        args: Iterable[Any] = [],
        kwargs: Mapping[str, Any] = {},
        details = None,
    ):
        self.args = args
        self.kwargs = kwargs
        self.details = details
        self.sent_time = datetime.utcnow()


class CallRequest(BaseRequest):
    """
    Represents a call request
    """

    details: CallDetails

    def __init__(
        self,
        args: Iterable[Any] = [],
        kwargs: Mapping[str, Any] = {},
        details: CallDetails = None
    ):
        super().__init__(args, kwargs, details)


class PublishRequest(BaseRequest):
    """
    Represents a publish request
    """

    details: EventDetails

    def __init__(
        self,
        args: Iterable[Any] = [],
        kwargs: Mapping[str, Any] = {},
        details: EventDetails = None
    ):
        super().__init__(args, kwargs, details)

