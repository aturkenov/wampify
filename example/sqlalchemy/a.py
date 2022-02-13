from wampify import Wampify
from wampify.story import *
from wampify.signals import entrypoint_signals


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)


from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


engine = create_async_engine('postgresql+asyncpg://scott:tiger@localhost/test', echo=True)

AlchemySession = sessionmaker(engine, AsyncSession)


@entrypoint_signals.on
async def opened(story):
    story.alchemy = AlchemySession()
    print('SQLAlchemy Async Session initialized')

@entrypoint_signals.on
async def raised(story, e):
    await story.alchemy.rollback()
    await story.alchemy.close()
    print('SQLAlchemy Async Session rollback')

@entrypoint_signals.on
async def closed(story):
    await story.alchemy.commit()
    await story.alchemy.close()
    print('SQLAlchemy Async Session closed')


@wampify.subscribe
async def hello(name: str = 'Anonymous'):
    print(f'{name} you are welcome!')
    story = get_current_story()
    print(story.alchemy)


if __name__ == '__main__':
    wampify.run()

