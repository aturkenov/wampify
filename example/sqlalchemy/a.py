from wampify.core.wampify import Wampify
from wampify.core.story import *


wampify = Wampify(
    debug=False,
    uri_prefix='com.example',
    router_url='ws://127.0.0.1:8080/private',
    wamp_session={
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


@wampify.on('_entrypoint_.opened', options={'is_endpoint': False})
async def _(story):
    story.alchemy = AlchemySession()
    print('SQLAlchemy Async Session initialized')

@wampify.on('_entrypoint_.raised', options={'is_endpoint': False})
async def _(story, e):
    await story.alchemy.rollback()
    await story.alchemy.close()
    print('SQLAlchemy Async Session rollback')

@wampify.on('_entrypoint_.closed', options={'is_endpoint': False})
async def _(story):
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

