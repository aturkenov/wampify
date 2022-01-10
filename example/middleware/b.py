from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        # Try to send our name
        answer = await self.call(
            'com.example.hello',
            name='wampify'
        )
        print(answer)
        # >>> Hello, wampify!


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)
