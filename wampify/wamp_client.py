import asyncio
from autobahn.wamp import ISession as WAMPIS
from autobahn.wamp.exception import ApplicationError
import orjson as json
from typing import Iterable, Mapping, Any, Tuple


WAMP_METHOD_CALL = 'C'
WAMP_METHOD_PUBLISH = 'P'
WAMP_METHOD_JOIN = 'J'
WAMP_METHOD_LEAVE = 'L'


class Consumer:

    _wamps: WAMPIS

    def __init__(
        self,
        wamps: WAMPIS
    ):
        self._wamps = wamps

    def _decode(
        self,
        encoded: bytes
    ) -> Tuple[int, str, str, Iterable, Mapping]:
        """
        """
        msg = json.loads(encoded)
        i = int(msg['i'])
        method = msg['method']
        URI = msg['URI']
        A = msg['A']
        K = msg['K']
        return i, method, URI, A, K

    def _encode_answer(
        self,
        i: int,
        payload: Any
    ) -> bytes:
        """
        """
        return json.dumps(
            {'i': i, 'status': 1, 'payload': payload},
            option=(json.OPT_NON_STR_KEYS|json.OPT_APPEND_NEWLINE)
        )

    def _encode_error(
        self,
        i: int,
        exception: ApplicationError
    ) -> bytes:
        """
        """
        payload = {
            'error': exception.error,
            'enc_algo': exception.enc_algo,
            'callee': exception.callee,
            'callee_authid': exception.callee_authid,
            'callee_authrole': exception.callee_authrole,
            'forward_for': exception.forward_for,
            'args': exception.args,
            'kwargs': exception.kwargs
        }
        return json.dumps(
            {'i': i, 'status': 0, 'payload': payload},
            option=(json.OPT_NON_STR_KEYS|json.OPT_APPEND_NEWLINE)
        )

    async def on_message(
        self,
        r: asyncio.StreamReader,
        w: asyncio.StreamWriter
    ):
        async def _(
            i: int,
            method: str,
            URI: str,
            A: Iterable,
            K: Mapping
        ) -> Any:
            """
            """
            try:
                payload = None
                if method == WAMP_METHOD_CALL:
                    payload = await self._wamps.call(URI, *A, **K)
                elif method == WAMP_METHOD_PUBLISH:
                    payload = self._wamps.publish(URI, *A, **K)
                elif method == WAMP_METHOD_LEAVE:
                    ...
            except ApplicationError as exception:
                return self._encode_error(i, exception)
            else:
                return self._encode_answer(i, payload)

        encoded = await r.readline()
        try:
            i, method, URI, A, K = self._decode(encoded)
        except:
            ...
        else:
            returning = await _(i, method, URI, A, K)
            w.write(returning)
            await w.drain()

    async def consume(
        self,
        path
    ):
        await asyncio.start_unix_server(self.on_message, path)


class Producer:

    _i: int
    _r: asyncio.StreamReader
    _w: asyncio.StreamWriter
    _read_lock: asyncio.Lock
    _write_lock: asyncio.Lock
    _todo: Mapping[int, asyncio.Task]

    def __init__(
        self,
        path
    ):
        self._path = path
        self._i = 0
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._todo = {}

    async def __aini__(
        self
    ):
        self._r, self._w = await asyncio.open_unix_connection(self._path)
        return self

    def __await__(
        self
    ):
        return self.__aini__().__await__()

    def _increase_message_number(
        self
    ) -> int:
        self._i += 1

    def get_message_number(
        self
    ) -> int:
        return self._i

    def _encode(
        self,
        i: int,
        method: str,
        URI: str,
        A: Iterable = [],
        K: Mapping = {}
    ) -> bytes:
        return json.dumps(
            { "i": i, "URI": URI, "method": method, "A": A, "K": K },
            option=(json.OPT_NON_STR_KEYS|json.OPT_APPEND_NEWLINE)
        )

    def _decode(
        self,
        encoded: bytes
    ) -> bytes:
        msg = json.loads(encoded)
        i = int(msg.get('i'))
        status = int(msg.get('status', 0))
        payload = msg.get('payload', None)
        return i, status, payload

    async def _receive_answer_(
        self,
        ai: int
    ) -> Any:
        # This function will work until the task receives required data
        # asyncio.streams.StreamReader doesn't support concurrent reading
        self._todo[ai] = asyncio.current_task()
        # FIXME check to while True
        while True:
            # Locks from concurrent execution
            async with self._read_lock:
                # Waiting for data to be received
                answer = await self._r.readline()
                bi, status, payload = self._decode(answer)
                if ai == bi:
                    # It executes, when data belongs to task
                    return ai, status, payload
                # Otherwise, tries to find payload owner's task
                another_task = self._todo.pop(bi, None)
                if another_task:
                    # Binds parsed output to task
                    another_task._RETURNING_ = bi, status, payload
                    # And closes it
                    another_task.cancel()

            # Enables other concurrent tasks
            await asyncio.sleep(0)

    async def _receive_answer(
        self,
        i: int
    ) -> Tuple[int, int, Any]:
        """
        It's beginning of self._receive_dispatched_.
        It wraps the coroutine in a task and waits for that task to complete,
        but another concurrent task can cancel the task
        and return the required payload in the _RETURNING_ attribute.
        """
        task = asyncio.create_task(self._receive_answer_(i))
        try:
            return await task
        except asyncio.CancelledError:
            return task._RETURNING_

    async def produce(
        self,
        method: str,
        URI: str,
        A: Iterable = [],
        K: Mapping = {}
    ) -> Any:
        async with self._write_lock:
            ai = self.get_message_number()
            msg = self._encode(ai, method, URI, A, K)
            self._increase_message_number()
            self._w.write(msg)
            await self._w.drain()

        bi, status, payload = await self._receive_answer(ai)

        if status == 0:
            if payload is None:
                payload = {}

            A = payload.get('args', [])
            K = payload.get('kwargs', {})
            raise ApplicationError(
                payload.get('error', 'wamp.error'),
                *A,
                enc_algo=payload.get('enc_algo', None),
                callee=payload.get('callee', None),
                callee_authid=payload.get('callee_authid', None),
                callee_authrole=payload.get('callee_authrole', None),
                forward_for=payload.get('forward_for', None),
                **K
            )

        return payload


class WAMPClient:

    _path: str
    _producer: Producer

    def __init__(
        self,
        path: str
    ):
        self._path = path

    async def __aini__(
        self
    ):
        self._producer = await Producer(self._path)
        return self

    def __await__(
        self
    ):
        return self.__aini__().__await__()

    async def join(
        self
    ):
        return await self._producer.produce(
            WAMP_METHOD_JOIN, None
        )

    async def leave(
        self
    ):
        return await self._producer.produce(
            WAMP_METHOD_LEAVE, None
        )

    async def call(
        self,
        URI: str,
        *A: Iterable,
        **K: Mapping
    ) -> Any:
        return await self._producer.produce(
            WAMP_METHOD_CALL, URI, A=A, K=K
        )

    async def publish(
        self,
        topic: str,
        *A: Iterable,
        **K: Mapping
    ) -> Any:
        return await self._producer.produce(
            WAMP_METHOD_PUBLISH, topic, A=A, K=K
        )

