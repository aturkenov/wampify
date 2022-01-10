from wampify.service.provider.base import BaseProvider
from sqlalchemy import Table, Column
from sqlalchemy.sql import Select, Insert, Update, Delete
from sqlalchemy.ext.asyncio import AsyncSession
from .table_filters import AlchemyFilters
from typing import Mapping, Iterable, Any


class BaseAlchemyProvider(BaseProvider):
    """
    """

    _session: AsyncSession

    async def __aini__(
        self
    ):
        self._session = await self._story.session_pool.release('alchemy')


class BaseAlchemyModelProvider(BaseAlchemyProvider):
    """
    """

    _table_: Table

    _select_stmt: Select
    _select_count_stmt: Select
    _insert_stmt: Insert
    _insert_returning_stmt: Any
    _update_stmt: Update
    _update_returning_stmt: Any
    _delete_stmt: Delete

    _sorting_columns: Iterable[str] = []


    class Filters(AlchemyFilters):
        """
        """


    async def __aini__(
        self
    ):
        await super().__aini__()
        self._filters = self.Filters()


    def _get_column(
        self,
        name: str
    ) -> Column:
        column = self._table.columns.get(name)
        if isinstance(column, Column):
            return column
        raise # TODO Exception

    async def _do_select(
        self,
        order_by: str = None,
        order_reversed: bool = None,
        limit: int = None,
        offset: int = None,
        **filters: Mapping
    ):
        """
        """
        stmt = self._select_stmt
        if isinstance(order_by, str) and order_by in self._sorting_columns:
            by_column = self._get_column(order_by)
            if isinstance(order_reversed, bool):
                by_column = by_column.desc() if order_reversed else by_column.asc()
            stmt = stmt.order_by(by_column)
        if limit and offset:
            stmt = stmt.limit(limit)
            stmt = stmt.offset(offset)
        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)
        return (await self._session.scalars(stmt)).all()

    async def _do_select_count(
        self,
        **filters
    ) -> int:
        stmt = self._select_count_stmt
        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)
        return await self._session.scalar(stmt)

    async def _do_get(
        self,
        **filters
    ):
        """
        """
        stmt = self._select_stmt
        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)
        return await self._session.scalar(stmt)

    async def _do_insert(
        self,
        **values: Mapping
    ):
        """
        """
        stmt = self._insert_stmt
        stmt = stmt.values(**values)
        if not self._insert_returning_stmt:
            await self._session.execute(stmt)
            return
        stmt = stmt.returning(self._insert_returning_stmt)
        return await self._session.scalar(stmt)

    async def _do_bulksert(
        self,
        *values: Iterable[Mapping]
    ):
        """
        """
        stmt = self._insert_stmt
        stmt = stmt.values(*values)
        if not self._insert_returning_stmt:
            await self._session.execute(stmt)
            return 
        stmt = stmt.returning(self._insert_returning_stmt)
        return (await self._session.scalars(stmt)).all()

    async def _do_update(
        self,
        filters: Mapping,
        **values: Mapping
    ):
        """
        """
        stmt = self._update_stmt
        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.values(**values)
        stmt = stmt.where(where_clause)
        if not self._update_returning_stmt:
            await self._session.execute(stmt)
            return
        stmt = stmt.returning(self._update_returning_stmt)
        return (await self._session.scalars(stmt)).all()

    async def _do_delete(
        self,
        filters: Mapping
    ) -> None:
        """
        """
        stmt = self._delete_stmt
        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)
        await self._session.execute(stmt)

    async def select(
        self,
        order_by: str = None,
        order_reversed: bool = None,
        limit: int = None,
        offset: int = None,
        **filters: Mapping
    ):
        """
        """
        return await self._do_select(
            order_by=order_by,
            order_reversed=order_reversed,
            limit=limit,
            offset=offset,
            filters=filters
        )

    async def select_count(
        self,
        **filters: Mapping
    ) -> int:
        return await self._do_select_count(filters=filters)

    async def get(
        self,
        **filters: Mapping
    ):
        """
        """
        return await self._do_get(filters=filters)

    async def insert(
        self,
        **values: Mapping
    ):
        """
        """
        return await self._do_insert(values=values)

    async def getsert(
        self,
        filters: Mapping,
        **values: Mapping
    ): ...

    async def bulksert(
        self,
        *values: Iterable[Mapping]
    ):
        """
        """
        return await self._do_bulksert(*values)

    async def update(
        self,
        filters: Mapping,
        **values: Mapping
    ):
        """
        """
        return await self._do_update(
            filters=filters,
            values=values
        )

    async def upsert(
        self,
        **values: Mapping
    ): ...

    async def delete(
        self,
        **filters: Mapping
    ) -> None:
        """
        """
        await self._do_delete(filters=filters)


