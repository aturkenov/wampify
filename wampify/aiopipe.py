from asyncio import (
    StreamReader, StreamWriter, StreamReaderProtocol,
    BaseTransport, get_running_loop, sleep
)
from typing import Tuple, Any
import os


def aiopipe() -> Tuple['AioPipeReader', 'AioPipeWriter']:
    rx, tx = os.pipe()
    return AioPipeReader(rx), AioPipeWriter(tx)


def aioduplex() -> Tuple['AioDuplex', 'AioDuplex']:
    rxa, txa = aiopipe()
    rxb, txb = aiopipe()
    return AioDuplex(rxa, txb), AioDuplex(rxb, txa)


class AioPipeStream:

    def __init__(
        self,
        fd
    ):
        self._fd = fd

    async def open(
        self
    ):
        self._transport, self._stream = await self._open()
        return self._stream

    async def _open(
        self
    ) -> Tuple[BaseTransport, Any]:
        raise NotImplementedError()

    def detach(
        self
    ) -> None:
        os.set_inheritable(self._fd, True)

    async def close(
        self
    ) -> None:
        try:
            self._transport.close()
        except OSError: ...
            # The transport/protocol sometimes closes the fd before this is reached.
        finally:
            # try:
            #     os.close(self._fd)
            # except OSError: ...
            #     # Something went wrong

            # Allow event loop callbacks to run and handle closed transport.
            await sleep(0)


class AioPipeReader(AioPipeStream):

    async def _open(
        self
    ) -> Tuple[BaseTransport, StreamReader]:
        rx = StreamReader()
        loop = get_running_loop()
        transport, _ = await loop.connect_read_pipe(
            lambda: StreamReaderProtocol(rx),
            os.fdopen(self._fd)
        )

        return transport, rx


class AioPipeWriter(AioPipeStream):

    async def _open(
        self
    ) -> Tuple[BaseTransport, StreamWriter]:
        rx = StreamReader()
        loop = get_running_loop()
        transport, proto = await loop.connect_write_pipe(
            lambda: StreamReaderProtocol(rx),
            os.fdopen(self._fd, 'w')
        )
        tx = StreamWriter(transport, proto, rx, loop)

        return transport, tx


class AioDuplex:

    def __init__(
        self,
        reader: AioPipeReader,
        writer: AioPipeWriter
    ):
        self._reader = reader
        self._writer = writer

    def detach(
        self
    ) -> None:
        self._reader.detach()
        self._writer.detach()

    async def open(
        self
    ) -> Tuple[AioPipeReader, AioPipeWriter]:
        rx = await self._reader.open()
        tx = await self._writer.open()
        return rx, tx

    async def close(
        self
    ) -> None:
        await self._reader.close()
        await self._writer.close()

