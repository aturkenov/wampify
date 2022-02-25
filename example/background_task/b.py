import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        await asyncio.gather(*[self.call('com.example.asap') for _ in range(100)])


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)

