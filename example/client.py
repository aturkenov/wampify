import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions, SubscribeOptions, EventDetails
from pprint import PrettyPrinter
from uuid import uuid4



pp = PrettyPrinter(indent=4)


class ClientSession(ApplicationSession):

    def onConnect(self):
        authid = str(uuid4())
        self.join(
            'test',
            authid='public',
            authmethods=["ticket"],
            authrole='public'
        )
    
    def onChallenge(self, challenge):
        return 'secret'

    async def onJoin(self, details):
        answer = await self.call(
            'com.example.rtest',
            0,
            1,
            c = 2,
            # d = 3
        )
        pp.pprint(answer)
        print()
        print()

        # answer = await self.publish(
        #     'com.example.storage.upsert',
        #     data={
        #         'language': 'ru'
        #     },
        #     options=PublishOptions(
        #         acknowledge=True,
        #         exclude_me=True,
        #     )
        # )
        # pp.pprint(answer)
        # print()
        # print()

        # answer = await self.publish(
        #     'com.example.stest',
        #     options=PublishOptions(
        #         acknowledge=True,
        #         exclude_me=True,
        #     )
        # )
        # pp.pprint(answer)
        # print()
        # print()

        # C = []
        # for i in range(10):
        #     c = self.call(
        #         'com.example.rtest',
        #         {}, {'v': i}
        #     )
        #     C.append(c)
        #     c = self.publish(
        #         'com.example.stest',
        #         {'key': 'value'}, {}
        #     )
        #     C.append(c)
        # answer = await asyncio.gather(*C)
        # pp.pprint(answer)
        # print()
        # print()


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public',
        realm='test'
    )
    runner.run(ClientSession)
