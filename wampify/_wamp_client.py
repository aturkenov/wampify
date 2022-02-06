from .aiopipe import aioduplex, AioDuplex
from .error_list import (
    WAMPClientHasNotJoinedYet
)
from autobahn.wamp import ISession, ApplicationError
from autobahn.asyncio.wamp import (
    ApplicationSession as AsyncioApplicationSession,
    ApplicationRunner as AsyncioApplicationRunner
)
import asyncio
import orjson as json
from uuid import UUID
from multiprocessing import Process
import signal
from typing import (
    Literal, Iterable, Mapping, Tuple, Any, Union
)


WAMP_METHOD_JOIN = 'J'
WAMP_METHOD_LEAVE = 'L'
WAMP_METHOD_CALL = 'C'
WAMP_METHOD_PUBLISH = 'P'
AVAILABLE_WAMP_METHODS = Literal['L', 'C', 'P']


# TODO Rename
class WAMPBridgeOutside:

    _pipe: AioDuplex
    _wamps: ISession

    def __init__(
        self,
        pipe: AioDuplex
    ):
        self._pipe = pipe

    def _parse(
        self,
        payload: bytes
    ) -> Tuple[UUID, str, str, Iterable, Mapping]:
        """
        """
        command = json.loads(payload)
        sequence = UUID(command['sequence'])
        method = command['method']
        URI = command['URI']
        A = command['A']
        K = command['K']
        return sequence, method, URI, A, K

    def _generate_answer(
        self,
        sequence: UUID,
        payload: Any
    ) -> bytes:
        """
        """
        return json.dumps(
            {'sequence': sequence, 'status': 1, 'payload': payload},
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    def _generate_error(
        self,
        sequence: UUID,
        e: ApplicationError
    ) -> bytes:
        """
        """
        payload = {
            'error': e.error,
            'enc_algo': e.enc_algo,
            'callee': e.callee,
            'callee_authid': e.callee_authid,
            'callee_authrole': e.callee_authrole,
            'forward_for': e.forward_for,
            'args': e.args,
            'kwargs': e.kwargs
        }
        return json.dumps(
            {'sequence': sequence, 'status': 0, 'payload': payload},
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    async def _dispatch(
        self,
        sequence: UUID,
        method: AVAILABLE_WAMP_METHODS,
        URI: str,
        A: Iterable,
        K: Mapping
    ) -> Any:
        """
        """
        try:
            returning = None
            if method == WAMP_METHOD_CALL:
                returning = await self._wamps.call(URI, *A, **K)
            elif method == WAMP_METHOD_PUBLISH:
                returning = self._wamps.publish(URI, *A, **K)
            elif method == WAMP_METHOD_LEAVE:
                self.stop()
        except ApplicationError as e:
            return self._generate_error(sequence, e)
        else:
            return self._generate_answer(sequence, returning)

    async def _listen_pipe(
        self
    ):
        """
        """
        async def onCommand(
            command: bytes
        ):
            try:
                sequence, method, URI, A, K = self._parse(command)
            except:
                # TODO required at least to parse message sequence
                self._tx.write(
                    b'{"sequence":"00000000-0000-0000-0000-000000000000","status":-1,"paylaod":"could_not_parse_command"}\n'
                )
            else:
                output = await self._dispatch(sequence, method, URI, A, K)
                self._tx.write(output)

        while True:
            command = await self._rx.readline()
            asyncio.create_task(onCommand(command))

    def _send_joined(
        self
    ) -> None:
        """
        """
        self._tx.write(b"joined\n")

    async def start(
        self
    ) -> None:
        """
        """
        assert self._pipe
        self._rx, self._tx = await self._pipe.open()
        await self._listen_pipe()

    async def stop(
        self
    ):
        """
        """
        assert self._pipe
        await self._pipe.close()
        await self._wamps.leave()
        exit()


class WAMPClientSession(AsyncioApplicationSession):

    _bridge: WAMPBridgeOutside

    async def onJoin(
        self,
        details
    ):
        self._bridge._wamps = self
        self._bridge._send_joined()


def run_wamp_client(
    pipe: AioDuplex,
    router_url: str,
    realm: str,
    wampc_session: WAMPClientSession
):
    bridge = WAMPBridgeOutside(pipe)

    async def async_run_wamp():
        runner = AsyncioApplicationRunner(router_url, realm)
        wampc_session._bridge = bridge
        _ = runner.run(wampc_session, start_loop=False)
        await asyncio.create_task(_)

    def on_leave_signal(*A, **K):
        loop = asyncio.get_running_loop()
        loop.create_task(bridge.stop())

    signal.signal(signal.SIGINT, on_leave_signal)
    signal.signal(signal.SIGTERM, on_leave_signal)

    loop = asyncio.new_event_loop()
    loop.create_task(async_run_wamp())
    loop.create_task(bridge.start())
    loop.run_forever()


# TODO Rename
class WAMPBridge:
    """
    """

    _pipe: AioDuplex
    _sequence: int
    _todo: Mapping[UUID, asyncio.Task]
    _write_lock: asyncio.Lock
    _read_lock: asyncio.Lock
    _process: Process
    _wampc_joined: bool
    _router_url: str
    _realm: str
    _wampc_session: WAMPClientSession

    def __init__(
        self,
        router_url: str,
        realm: str,
        wampc_session: WAMPClientSession
    ):
        self._router_url = router_url
        self._realm = realm
        self._wampc_session = wampc_session
        self._sequence = 0
        self._wampc_joined = False
        self._todo: Mapping[UUID, asyncio.Task] = {}
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()

    def _increase_message_sequence(
        self
    ) -> None:
        self._sequence += 1

    def _get_message_sequence(
        self
    ) -> UUID:
        return UUID(int=self._sequence)

    def _generate(
        self,
        sequence: UUID,
        method: AVAILABLE_WAMP_METHODS,
        URI: str = None,
        A: Iterable = tuple(),
        K: Mapping = {}
    ) -> bytes:
        return json.dumps(
            { 'sequence': sequence, 'method': method, 'URI': URI, 'A': A, 'K': K },
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    def _parse(
        self,
        encoded: bytes
    ) -> Tuple[UUID, int, Any]:
        decoded = json.loads(encoded)
        sequence = UUID(decoded.get('sequence', None))
        status = int(decoded.get('status', 0))
        payload = decoded.get('payload', None)
        return sequence, status, payload

    async def _receive_dispatched_(
        self,
        asequence: UUID
    ):
        # This function will work until the task receives required data
        # asyncio.streams.StreamReader doesn't support concurrent reading
        self._todo[asequence] = asyncio.current_task()
        # FIXME check to while True
        while True:
            # Locks from concurrent execution
            async with self._read_lock:
                # Waiting for data to be received
                answer = await self._rx.readline()
                bsequence, status, payload = self._parse(answer)
                if asequence == bsequence:
                    # It executes, when data belongs to task
                    return bsequence, status, payload
                # Otherwise, tries to find payload owner's task
                another_task = self._todo.pop(bsequence, None)
                if another_task:
                    # Binds parsed output to task
                    another_task._RETURNING_ = bsequence, status, payload
                    # And closes it
                    another_task.cancel()

            # Enables other concurrent tasks
            await asyncio.sleep(0)

    async def _receive_dispatched(
        self,
        asequence: UUID
    ) -> Tuple[UUID, int, Any]:
        """
        It's beginning of self._receive_dispatched_.
        It wraps the coroutine in a task and waits for that task to complete,
        but another concurrent task can cancel the task
        and return the required payload in the _RETURNING_ attribute.
        """
        task = asyncio.create_task(self._receive_dispatched_(asequence))
        try:
            return await task
        except asyncio.CancelledError:
            return task._RETURNING_

    async def _dispatch(
        self,
        method: AVAILABLE_WAMP_METHODS,
        URI: str = None,
        A: Iterable = tuple(),
        K: Mapping = {}
    ) -> Any:
        """
        """
        if not self._wampc_joined:
            raise WAMPClientHasNotJoinedYet()

        async with self._write_lock:
            asequence = self._get_message_sequence()
            self._increase_message_sequence()

            command = self._generate(asequence, method, URI, A, K)
            self._tx.write(command)

        bsequence, status, payload = await self._receive_dispatched(asequence)

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

    async def _listen_wampc_heartbeat(
        self
    ):
        if not self._wampc_joined:
            response = await self._rx.readline()
            if response != b'joined\n':
                # TODO
                raise
            self._wampc_joined = True

    def _spawn_child_process(
        self,
        pipe: AioDuplex
    ):
        """
        Spawns child process
        """
        self._process = Process(
            target=run_wamp_client,
            args=(pipe, self._router_url, self._realm, self._wampc_session)
        )
        self._process.start()

    async def join(
        self,
        authid: str = None,
        authrole: str = None,
        authmethods: Iterable[str] = None,
        authextra: Any = None,
        resumable: str = None,
        resume_session: str = None,
        resume_token: str = None
    ):
        """
        Creates async duplex pipes
        To exchange messages between two processes
        """
        def on_leave_signal(*A, **K):
            loop = asyncio.get_running_loop()
            loop.create_task(self.leave())

        signal.signal(signal.SIGINT, on_leave_signal)
        signal.signal(signal.SIGTERM, on_leave_signal)

        self._pipe, b = aioduplex()
        self._rx, self._tx = await self._pipe.open()
        # Detaches b pipe from current process
        b.detach()
        self._spawn_child_process(b)
        await self._listen_wampc_heartbeat()

    async def leave(
        self,
        *A,
        **K
    ):
        """
        
        """
        response = await self._dispatch(WAMP_METHOD_LEAVE, None, A, K)
        await self._pipe.close()
        self._process.join()
        return response

    async def call(
        self,
        URI,
        *A,
        **K
    ):
        return await self._dispatch(WAMP_METHOD_CALL, URI, A, K)

    async def publish(
        self,
        URI,
        *A,
        **K
    ):
        return await self._dispatch(WAMP_METHOD_PUBLISH, URI, A, K)


class WAMPClient:
    """
    """

    _bridge: WAMPBridge
    _urip: Union[str, None]

    def __init__(
        self,
        router_url: str,
        realm: str,
        uri_prefix: str = None,
        factory: WAMPClientSession = WAMPClientSession,
    ):
        self._bridge = WAMPBridge(router_url, realm, factory)
        self._urip = uri_prefix

    async def join(
        self,
        authid: str = None,
        authrole: str = None,
        authmethods: Iterable[str] = None,
        authextra: Any = None,
        resumable: str = None,
        resume_session: str = None,
        resume_token: str = None,
    ):
        """
        """
        return await self._bridge.join(
            authmethods=authid,
            authid=authrole,
            authrole=authmethods,
            authextra=authextra,
            resumable=resumable,
            resume_session=resume_session,
            resume_token=resume_token
        )

    async def leave(
        self,
        reason=None,
        message=None
    ):
        """
        """
        return await self._bridge.leave(reason, message)

    async def call(
        self,
        URI,
        *A,
        **K
    ):
        """
        """
        return await self._bridge.call(URI, *A, **K)

    async def publish(
        self,
        URI,
        *A,
        **K
    ):
        """
        """
        return await self._bridge.publish(URI, *A, **K)

