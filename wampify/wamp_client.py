# from .settings import WAMPClientSettings

import asyncio
import orjson as json
from multiprocessing import Process
from aiopipe import aioduplex, AioDuplex
from typing import Literal, Iterable, Mapping


class WAMPBridgeOutside:

    _pipe: AioDuplex

    def __init__(
        self,
        pipe: AioDuplex
    ):
        self._pipe = pipe

    async def listen(
        self
    ):
        while True:
            request = await self._rx.readline()
            self._tx.write(b"okey\n")
            if request == b'leave\n':
                self._tx.write(b"okey\n")
                break

        await self._pipe.close()

    def send_ping(
        self
    ):
        self._tx.write(b"ping\n")

    async def start(
        self
    ):
        assert self._pipe
        self._rx, self._tx = await self._pipe.open()
        self.send_ping()
        await self.listen()


def spawn_child_process(
    pipe: AioDuplex
):
    import asyncio
    loop = asyncio.new_event_loop()

    async def execute_wamp_session():
        from autobahn.asyncio.wamp import (
            ApplicationSession as AsyncioApplicationSession,
            ApplicationRunner as AsyncioApplicationRunner
        )
        class WAMPClientSession(AsyncioApplicationSession):
            def onJoin(
                self,
                details
            ):
                print('joined')
        runner = AsyncioApplicationRunner(
            'ws://0.0.0.0:8080/private',
            'example'
        )
        _ = runner.run(WAMPClientSession, start_loop=False)
        asyncio.create_task(_)

    loop.run_until_complete(execute_wamp_session())
    bridge = WAMPBridgeOutside(pipe)
    loop.run_until_complete(bridge.start())
    loop.run_forever()


class WAMPBridge:

    _pipe: AioDuplex
    _process: Process

    def __init__(
        self,
        *A,
        **K
    ):
        """
        """

    def _generate_command(
        self,
        type_: Literal['J', 'L', 'C', 'P'],
        URI: str,
        A: Iterable,
        K: Mapping
    ):
        return json.dumps(
            (type_, URI, A, K),
            option=(json.OPT_NON_STR_KEYS | json.OPT_APPEND_NEWLINE)
        )

    def _spawn_child_process(
        self,
        pipe: AioDuplex
    ):
        """
        """
        self._process = Process(
            target=spawn_child_process,
            args=(pipe, )
        )
        self._process.start()

    async def _check_pipe(
        self
    ):
        response = await self._rx.readline()
        if response != b'ping\n':
            raise

    async def join(
        self
    ):
        """
        """
        a, b = aioduplex()
        self._pipe = a
        self._rx, self._tx = await a.open()
        self._spawn_child_process(b)
        await self._check_pipe()

    async def leave(
        self
    ):
        """
        """
        self._tx.write(b'leave\n')
        await self._rx.readline()
        await self._pipe.close()
        self._process.join()

    async def call(
        self,
        URI,
        *A,
        **K
    ):
        """
        """

    async def publish(
        self,
        URI,
        *A,
        **K
    ):
        """
        """
        cmd = self._generate_command('P', URI, A, K)
        self._tx.write(cmd)
        return await self._rx.readline()


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


client = WAMPClient()
loop = asyncio.get_event_loop()
loop.run_until_complete(client.join())
print(loop.run_until_complete(client.publish('com.example.hello', 1, 2, 3, {0:'\n'}, hello='world')))
loop.run_until_complete(client.leave())

