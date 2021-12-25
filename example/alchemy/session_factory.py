from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from wampify.core.session_factory import BaseSessionFactory


engine = create_async_engine(
    'postgresql+asyncpg://scott:tiger@localhost/test',
     pool_size=20,
     max_overflow=-1
)


Session = sessionmaker(
    engine, AsyncSession
)


class AlchemySF(BaseSessionFactory):

    _session: AsyncSession

    async def on_release(
        self
    ):
        self._session = Session()
        return self._session

    async def on_raise(
        self
    ):
        await self._session.rollback()
        await self._session.close()

    async def on_close(
        self
    ):
        await self._session.commit()
        await self._session.close()

