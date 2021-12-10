from typing import *


class Request:
    """
    """

    A: Iterable[Any]
    K: Mapping[str, Any]
    details: object
    endpoint: Callable

    def __init__(
        self,
        details,
        endpoint: Callable,
        A: Iterable[Any] = [],
        K: Mapping[str, Any] = {},
    ):
        self.details = details
        self.endpoint = endpoint
        self.A = A
        self.K = K



# story.client = details.caller_authid

# story.client = details.publisher_authid
