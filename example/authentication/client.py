from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from uuid import uuid4


authid = str(uuid4())


class ClientSession(ApplicationSession):

    def onConnect(self):
        self.join(
            'example',
            authid='ivan',
            authmethods=["ticket"],
            authrole='public'
        )

    def onChallenge(self, challenge):
        return 'secret'

    async def onJoin(self, details):
        print('Session was joined')


if __name__ == '__main__':
    runner = ApplicationRunner(url='ws://127.0.0.1:8080/public')
    runner.run(ClientSession)
