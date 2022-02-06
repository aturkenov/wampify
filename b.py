import asyncio
from random import randint as random


async def main():
    R, W = await asyncio.open_unix_connection('wampc')
    n = str(random(0, 100)).encode()
    for i in range(1000):
        W.write(n + b'hello\n')
        print(await R.readline())


loop = asyncio.new_event_loop()
loop.create_task(main())
loop.run_forever()