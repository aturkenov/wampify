import asyncio
from inspect import iscoroutinefunction as is_async
from typing import Dict, List, Callable, Union


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
        self._S.setdefault(signal_name, [])
        self._S[signal_name].append(procedure)

    def on(
        self,
        signal_name: Union[str, Callable] = None
    ) -> Callable:
        """
        Uses procedure name if signal_name is not passed

        Returns passed procedure

        >>> @signals.on
        >>> async def ():
        """
        def decorate(
            procedure: Callable
        ):
            _signal_name = procedure.__name__ if signal_name is None else signal_name
            self.add(_signal_name, procedure)
            return procedure

        if callable(signal_name):
            _signal_name, procedure = signal_name.__name__, signal_name
            self.add(_signal_name, procedure)
            return procedure
        return decorate

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


signals = SignalManager()
wamps_signals = SignalManager()
entrypoint_signals = SignalManager()

