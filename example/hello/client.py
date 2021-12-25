from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        # Backend hello procedure
        # name argument type is string, also has default value 
        # def hello(name: str = 'anonymous'):
        #     return f'Hello, {name}!'

        # Try to send our name
        answer = await self.call(
            'com.example.hello',
            name='wampify'
        )
        print(answer)
        # >>> Hello, wampify!
        
        # # Try to call without name
        # answer = await self.call('com.example.hello')
        # print(answer)
        # # >>> Hello, anonymous!
        
        # # Try to send something other, e.g. name = 1
        # answer = await self.call(
        #     'com.example.hello',
        #     name=1
        # )
        # print(answer)
        # # >>> Hello, 1!
        # # It returns 'Hello, 1!', because str(1) == '1'
        


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)
