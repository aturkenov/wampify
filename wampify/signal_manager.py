import asyncio
from inspect import iscoroutinefunction as is_async
from typing import Dict, List, Callable


class SignalManager:

    _S: Dict[str, List[Callable]]

    def __init__(
        self
    ) -> None:
        self._S = {}

    def add(
        self,
        signal_name: str,
        procedure: Callable
    ) -> None:
        assert callable(procedure), 'procedure must be Callable'
        self._S.setdefault(signal_name, list())
        self._S[signal_name].append(procedure)

    async def fire(
        self,
        signal_name: str,
        *A,
        **KW
    ) -> None:
        P = self._S.get(signal_name, [])
        C = []
        for procedure in P:
            if is_async(procedure):
                c = procedure(*A, **KW)
                C.append(c)
            else:
                procedure(*A, **KW)
        await asyncio.gather(*C)

