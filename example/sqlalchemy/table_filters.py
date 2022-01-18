from sqlalchemy import Column, Table, and_
from sqlalchemy.sql.expression import BinaryExpression
from typing import Mapping


class AlchemyFilters:
    """
    """

    _table: Table

    def _get_column(
        self,
        name: str
    ) -> Column:
        column = self._table.columns.get(name)
        if isinstance(column, Column):
            return column
        raise 

    _lookup_operators = {
        'e': lambda c, v: c == v,
        'ne': lambda c, v: c != v,
        'l': lambda c, v: c < v,
        'le': lambda c, v: c <= v,
        'g': lambda c, v: c > v,
        'ge': lambda c, v: c >= v,
        'like': lambda c, v: c.like(v),
        'ilike': lambda c, v: c.ilike(v),
        'in': lambda c, v: c.in_(v)
    }

    def _build_expression(
        self,
        lookup,
        value
    ) -> BinaryExpression:
        i = lookup.rindex('__')
        column_name, operator_name = lookup[:i], lookup[i+2:]
        column = self._get_column(column_name)
        lookup_operator = self._lookup_operators.get(operator_name)
        if not callable(lookup_operator):
            raise 
        return lookup_operator(column, value)

    def build_where_clause(
        self,
        **filters: Mapping
    ):
        """
        """
        E = []
        for l, v in filters.items():
            try:
                e = self._build_expression(l, v)
            except:
                continue
            E.append(e)
        return and_(*E)


