import os
import asyncio
import time


FD_CONSUMER = './consumer.pid'
if os.path.exists(FD_CONSUMER):
  os.remove(FD_CONSUMER)


async def procedure(i):
    # await asyncio.sleep(1)
    time.sleep(1)
    return i


async def consumer(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    raw_msg = await reader.read()
    msg = raw_msg.decode()
    returning = await procedure(int(msg))
    output = str(returning).encode()
    writer.write(output)
    writer.write_eof()
    await writer.drain()


async def main():
    server = await asyncio.start_unix_server(consumer, FD_CONSUMER)
    await server.serve_forever()


asyncio.run(main())