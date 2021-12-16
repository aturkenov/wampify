from .error import ErrorRC
from .endpoint import EndpointRC
from .base import *
from typing import *


def build_rchain(
    RCs: RChainsDT,
    settings: Mapping = {}
) -> RChain:
    """
    Builds chain of responsibility
    """
    def build(
        RCs, settings
    ):
        first, i = None, None
        for chain in RCs:
            chain = chain(settings)

            if first is None and i is None:
                first, i = chain, chain
                continue

            i._next = chain
            i = chain

        return first

    return build([ErrorRC, *RCs, EndpointRC], settings)

