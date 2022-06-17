from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from async_timeout import timeout


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        # This procedure never executed
        async with timeout(1):
            answer = await self.call('com.example.long')


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)
