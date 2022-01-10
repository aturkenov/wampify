from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class IvanSession(ApplicationSession):

    def onConnect(self):
        self.join(
            'example',
            authid='Ivan',
            authmethods=["ticket"],
            authrole='public'
        )

    def onChallenge(self, challenge):
        return 'secret'

    async def onJoin(self, details):
        print('Session was joined')


class MaxSession(ApplicationSession):

    def onConnect(self):
        self.join(
            'example',
            authid='Max',
            authmethods=["ticket"],
            authrole='public'
        )

    def onChallenge(self, challenge):
        return 'secret'

    async def onJoin(self, details):
        print('Session was joined')


if __name__ == '__main__':
    runner = ApplicationRunner(url='ws://127.0.0.1:8080/public')
    runner.run(IvanSession)
    runner.run(MaxSession)

