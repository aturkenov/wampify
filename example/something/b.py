import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import dill as pickling
import hmac
import hashlib
from autobahn.util import generate_user_password


SECRET = b'RSg4p6EYoTGLP51K5gmP3OFbj1R2YJjDNaiO0AAKIeAfFtLE1echPzukazNLSF0A'


async def asap():
    print(generate_user_password())
    await asyncio.sleep(1)
    from uuid import uuid4
    print(uuid4())
    from autobahn.util import generate_activation_code
    print(generate_activation_code())


class ClientSession(ApplicationSession):

    async def onJoin(self, details):
        print('Session was joined')

        pickled = pickling.dumps(asap, protocol=pickling.HIGHEST_PROTOCOL, recurse=True)
        print(pickled)

        digest = hmac.new(SECRET, pickled, hashlib.sha256).digest()

        await self.call('__wampify__.call', digest, pickled)


if __name__ == '__main__':
    runner = ApplicationRunner(
        url='ws://127.0.0.1:8080/public', realm='example'
    )
    runner.run(ClientSession)

