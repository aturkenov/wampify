from .endpoint import EndpointMiddleware
from .base import *
from typing import *


def build_rchain(
    M: List[BaseMiddleware],
    settings: Mapping = {}
) -> BaseMiddleware:
    """
    Builds chain of responsibility
    """
    def build(
        M, settings
    ):
        first, i = None, None
        for m in M:
            m = m(settings)

            if first is None and i is None:
                first, i = m, m
                continue

            i._next = m
            i = m

        return first

    return build([*M, EndpointMiddleware], settings)

