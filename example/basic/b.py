from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        # com.example.hello procedure
        # def hello(name: string = 'Anonymous'):
        #     print(f'{name} you are welcome!') 

        self.publish('com.example.hello', name='Ivan')


        # com.example.pow procedure
        # def pow(x: float = 1):
        #     return x ** 2 

        answer = await self.call('com.example.pow', 2)
        print('com.example.pow(2) ->', answer)
        # >>> com.example.pow(2) -> 4.0

        answer = await self.call('com.example.pow', 1)
        print('com.example.pow(1) ->', answer)
        # >>> com.example.pow(1) -> 1.0

        answer = await self.call('com.example.pow', 1000000)
        print('com.example.pow(1000000) ->', answer)
        # >>> com.example.pow(1000000) -> 1000000000000.0

        answer = await self.call('com.example.pow', -1)
        print('com.example.pow(-1) ->', answer)
        # >>> com.example.pow(-1) -> 1.0

        answer = await self.call('com.example.pow', 1.23)
        print('com.example.pow(1.23) ->', answer)
        # >>> com.example.pow(1.23) -> 1.5129

        answer = await self.call('com.example.pow', 1.23456)
        print('com.example.pow(1.23456) ->', answer)
        # >>> com.example.pow(1.23456) -> 1.5241383936000001

        answer = await self.call('com.example.pow', '1')
        print('com.example.pow("1") ->', answer)
        # >>> com.example.pow("1") -> 1.0

        answer = await self.call('com.example.pow', '-1')
        print('com.example.pow("-1") ->', answer)
        # >>> com.example.pow("-1") -> 1.0

        answer = await self.call('com.example.pow', '1.23456')
        print('com.example.pow("1.23456") ->', answer)
        # >>> com.example.pow("1.23456") -> 1.5241383936000001

        try:
            await self.call('com.example.pow', 'a')
        except Exception as e:
            print('com.example.pow("a") ->', e)
            # PayloadValidationError!


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)
