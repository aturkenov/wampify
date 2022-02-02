# from .settings import WAMPClientSettings
from autobahn.wamp import ISession, ApplicationError
from autobahn.asyncio.wamp import (
    ApplicationSession as AsyncioApplicationSession,
    ApplicationRunner as AsyncioApplicationRunner
)
import asyncio
import orjson as json
from uuid import UUID
from multiprocessing import Process
from aiopipe import aioduplex, AioDuplex
from typing import Literal, Iterable, Mapping, Tuple, Any


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
        sequence = command['sequence']
        method = command['method']
        URI = command['URI']
        A = command['A']
        K = command['K']
        return sequence, method, URI, A, K

    def _generate_answer(
        self,
        sequence: UUID,
        returning: Any
    ) -> bytes:
        return json.dumps(
            {'sequence': sequence, 'status': 1, 'returning': returning},
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    def _generate_error(
        self,
        sequence: UUID,
        e: ApplicationError
    ) -> bytes:
        returning = {
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
            {'sequence': sequence, 'status': 0, 'returning': returning},
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    async def _listen_pipe(
        self
    ):
        async def f(payload):
            try:
                sequence, method, URI, A, K = self._parse(payload)
            except:
                self._tx.write(b'something_went_wrong\n')
            else:
                try:
                    if method == 'C':
                        returning = await self._wamps.call(URI, *A, **K)
                    elif method == 'P':
                        returning = self._wamps.publish(URI, *A, **K)
                    elif method == 'L':
                        returning = self._wamps.leave(URI, *A, **K)
                        return False
                    else:
                        raise 
                except ApplicationError as e:
                    output = self._generate_error(sequence, e)
                else:
                    output = self._generate_answer(sequence, returning)
                self._tx.write(output)
            return True

        while True:
            payload = await self._rx.readline()
            asyncio.create_task(f(payload))

        await self._pipe.close()

    def _send_joined(
        self
    ):
        self._tx.write(b"joined\n")

    async def start(
        self
    ):
        assert self._pipe
        self._rx, self._tx = await self._pipe.open()
        await self._listen_pipe()


class WAMPClientSession(AsyncioApplicationSession):

    _bridge: WAMPBridgeOutside

    async def onJoin(
        self,
        details
    ):
        self._bridge._wamps = self
        self._bridge._send_joined()


def run_wamp_client(
    pipe: AioDuplex
):
    loop = asyncio.new_event_loop()
    bridge = WAMPBridgeOutside(pipe)

    async def run_wamp():
        WAMPClientSession._bridge = bridge
        runner = AsyncioApplicationRunner(
            'ws://0.0.0.0:8080/private',
            'example'
        )
        _ = runner.run(WAMPClientSession, start_loop=False)
        await asyncio.create_task(_)
        await bridge.start()

    loop.run_until_complete(run_wamp())
    loop.run_forever()


from datetime import datetime


class WAMPBridge:
    """
    """

    _i: int
    _pipe: AioDuplex
    _process: Process
    _wampc_joined: bool

    def __init__(
        self,
        *A,
        **K
    ):
        self._sequence = 0
        self._wampc_joined = False
        self._map = {}
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()

    def _increase_message_sequence(
        self
    ) -> None:
        self._sequence += 1

    def _get_message_sequence(
        self
    ):
        return UUID(int=self._sequence)

    def _generate(
        self,
        sequence: UUID,
        method: Literal['J', 'L', 'C', 'P'],
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
        payload: bytes
    ):
        decoded = json.loads(payload)
        sequence = UUID(decoded.get('sequence', None))
        status = int(decoded.get('status', 0))
        returning = decoded.get('returning', None)
        return sequence, status, returning

    async def _dispatch(
        self,
        method: Literal['J', 'L', 'C', 'P'],
        URI: str = None,
        A: Iterable = tuple(),
        K: Mapping = {}
    ) -> Any:
        if not self._wampc_joined:
            raise

        async with self._write_lock:
            asequence = self._get_message_sequence()
            self._increase_message_sequence()

            command = self._generate(asequence, method, URI, A, K)
            self._tx.write(command)

        async def f():
            async with self._read_lock:
                while True:
                    output = await self._rx.readline()
                    bsequence, status, returning = self._parse(output)
                    if asequence == bsequence:
                        return bsequence, status, returning
                    task: asyncio.Task = self._map.pop(bsequence, None)
                    if task is None:
                        continue
                    task._returning_ = bsequence, status, returning
                    task.cancel()

        task = asyncio.create_task(f())
        self._map[asequence] = task
        try:
            bsequence, status, returning = await task
        except asyncio.CancelledError:
            bsequence, status, returning = task._returning_

        if status == 0:
            if returning is None:
                returning = {}

            A = returning.get('args', [])
            K = returning.get('kwargs', {})
            raise ApplicationError(
                returning.get('error', 'wamp.error'),
                *A,
                enc_algo=returning.get('enc_algo', None),
                callee=returning.get('callee', None),
                callee_authid=returning.get('callee_authid', None),
                callee_authrole=returning.get('callee_authrole', None),
                forward_for=returning.get('forward_for', None),
                **K
            )

        return returning

    async def _check_pipe(
        self
    ):
        response = await self._rx.readline()
        if response != b'joined\n':
            raise
        self._wampc_joined = True

    def _spawn_child_process(
        self,
        pipe: AioDuplex
    ):
        """
        """
        self._process = Process(target=run_wamp_client, args=(pipe, ))
        self._process.start()

    async def join(
        self
    ):
        """
        """
        self._pipe, b = aioduplex()
        self._rx, self._tx = await self._pipe.open()
        b.detach()
        self._spawn_child_process(b)
        await self._check_pipe()

    async def leave(
        self
    ):
        """
        """
        response = await self._dispatch('L')
        await self._pipe.close()
        self._process.join()
        return response

    async def call(
        self,
        URI,
        *A,
        **K
    ):
        """
        """
        a = datetime.now()
        response = await self._dispatch('C', URI, A, K)
        print(datetime.now() - a, 'C')
        return response

    async def publish(
        self,
        URI,
        *A,
        **K
    ):
        """
        """
        a = datetime.now()
        response = await self._dispatch('P', URI, A, K)
        print(datetime.now() - a, 'P')
        return response


class WAMPClient:
    """
    """

    _bridge: WAMPBridge
    # _settings: WAMPClientSettings

    def __init__(
        self,
        *A,
        **K
    ):
        self._bridge = WAMPBridge()
        # self._settings = WAMPClientSettings(*A, **K)

    def onChallange(
        self
    ):
        """
        """

    async def join(
        self
    ):
        """
        """
        return await self._bridge.join()

    async def leave(
        self
    ):
        """
        """
        return await self._bridge.leave()

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


async def main():
    client = WAMPClient()
    await client.join()
    # await asyncio.sleep(1)
    # import threading
    # print(threading.active_count())
    print(await asyncio.gather(
        client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world'),
        # client.call('com.example.pow', 1, 2, 3, {0:'\n'}, hello='world')
        return_exceptions=True
    ))
    await client.leave()
    print('thats all')


asyncio.run(main())

