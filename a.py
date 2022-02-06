import asyncio


async def on_message(
    R: asyncio.StreamReader,
    W: asyncio.StreamWriter
):
    print(await R.readline())
    W.write(b'world\n')


async def main():
    await asyncio.start_unix_server(
        on_message,
        path='wampc'
    )


loop = asyncio.new_event_loop()
loop.create_task(main())
loop.run_forever()