from .base import *
from core.endpoint import SharedEndpoint
from typing import *


def build_rchain(
    M: List[Union[BaseMiddleware, SharedEndpoint]],
    settings: Mapping = None
) -> BaseMiddleware:
    """
    Builds chain of responsibility
    """
    assert isinstance(M, list), 'Must be list of middlewares'
    assert len(M) > 0, 'Must be more than zero middlewares'

    endpoint = M.pop()

    first, i = None, None
    for m in M:
        m = m.__init__(settings)

        if first is None and i is None:
            first, i = m, m
            continue

        i.set_next(m)
        i = m

    if i is None:
        return endpoint

    i.set_next(endpoint)
    return first

