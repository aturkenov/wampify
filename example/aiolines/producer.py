import asyncio
import time


FD_CONSUMER = './consumer.pid'


async def produce(i):
    reader, writer = await asyncio.open_unix_connection(FD_CONSUMER)
    _ = str(i).encode()
    writer.write(_)
    writer.write_eof()
    await writer.drain()
    return await reader.read()


async def main():
    print(await asyncio.gather(*[produce(i) for i in range(470)]))


asyncio.run(main())

