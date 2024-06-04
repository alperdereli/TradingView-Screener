from __future__ import annotations

from typing import TYPE_CHECKING
from tradingview_screener.constants import COLUMNS


if TYPE_CHECKING:
    from typing import Literal, Optional, Iterable
    from tradingview_screener.query import FilterOperationDict


class Column:
    """
    A Column object represents a field in the tradingview stock screener,
    and it's used in SELECT queries and WHERE queries with the `Query` object.

    A `Column` supports all the comparison operations:
    `<`, `<=`, `>`, `>=`, `==`, `!=`, and also other methods like `between()`, `isin()`, etc.

    Examples:

    Some of the operations that you can do with `Column` objects:
    >>> Column('close') >= 2.5
    >>> Column('close').between(2.5, 15)
    >>> Column('high') > Column('VWAP')
    >>> Column('close').between(Column('EMA5'), Column('EMA20')
    >>> Column('type').isin(['stock', 'fund'])
    >>> Column('description').like('apple')  # the same as `description LIKE '%apple%'`
    """

    def __init__(self, name: str) -> None:
        """
        Create a column object from a given column name

        :param name: string, should be either a key or a value from the `COLUMNS` dictionary
        """
        # if `name` is a dictionary key: get its value. otherwise make sure that it's a
        # dictionary value.
        self.name = COLUMNS.get(name, name)

    @staticmethod
    def _extract_name(obj) -> ...:
        if isinstance(obj, Column):
            return obj.name
        return obj

    def __gt__(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'greater', 'right': self._extract_name(other)}

    def __ge__(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'egreater', 'right': self._extract_name(other)}

    def __lt__(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'less', 'right': self._extract_name(other)}

    def __le__(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'eless', 'right': self._extract_name(other)}

    def __eq__(self, other) -> FilterOperationDict:  # pyright: ignore [reportIncompatibleMethodOverride]
        return {'left': self.name, 'operation': 'equal', 'right': self._extract_name(other)}

    def __ne__(self, other) -> FilterOperationDict:  # pyright: ignore [reportIncompatibleMethodOverride]
        return {'left': self.name, 'operation': 'nequal', 'right': self._extract_name(other)}

    def crosses(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'crosses', 'right': self._extract_name(other)}

    def crosses_above(self, other) -> FilterOperationDict:
        return {
            'left': self.name,
            'operation': 'crosses_above',
            'right': self._extract_name(other),
        }

    def crosses_below(self, other) -> FilterOperationDict:
        return {
            'left': self.name,
            'operation': 'crosses_below',
            'right': self._extract_name(other),
        }

    def _impl_above_below_pct(
        self, operation: Literal['above%', 'below%'], column: Column | str, pct1, pct2=None
    ) -> FilterOperationDict:
        if pct2:
            return {
                'left': self.name,
                'operation': 'in_range%',
                'right': [self._extract_name(column), *sorted([pct1, pct2])],
            }
        return {
            'left': self.name,
            'operation': operation,
            'right': [self._extract_name(column), pct1],
        }

    def above_pct(
        self, column: Column | str, pct1: float, pct2: Optional[float] = None
    ) -> FilterOperationDict:
        """
        Examples:

        The closing price is higher than the VWAP by more than 3%
        >>> Column('close').above_pct('VWAP', 1.03)

        The percentage change between the Close and the EMA is between 20% and 50%
        >>> Column('close').above_pct('EMA200', 1.2, 1.5)

        closing price is above the 52-week-low by more than 150%
        >>> Column('close').above_pct('price_52_week_low', 2.5)
        """
        return self._impl_above_below_pct('above%', column=column, pct1=pct1, pct2=pct2)

    def below_pct(
        self, column: Column | str, pct1, pct2: Optional[float] = None
    ) -> FilterOperationDict:
        """
        Examples:

        TODO
        """
        return self._impl_above_below_pct('below%', column=column, pct1=pct1, pct2=pct2)

    def has(self, values: Iterable) -> FilterOperationDict:
        """
        Field contains any of the values

        (it's the same as isin(), except that it works on fields of type `set`)
        """
        return {'left': self.name, 'operation': 'has', 'right': list(values)}

    def has_none_of(self, values: Iterable) -> FilterOperationDict:
        """
        Field doesn't contain any of the values
        """
        return {'left': self.name, 'operation': 'has_none_of', 'right': list(values)}

    def between(self, left, right) -> FilterOperationDict:
        return {
            'left': self.name,
            'operation': 'in_range',
            'right': [self._extract_name(left), self._extract_name(right)],
        }

    def not_between(self, left, right) -> FilterOperationDict:
        return {
            'left': self.name,
            'operation': 'not_in_range',
            'right': [self._extract_name(left), self._extract_name(right)],
        }

    def isin(self, values: Iterable) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'in_range', 'right': list(values)}

    def like(self, other) -> FilterOperationDict:
        return {'left': self.name, 'operation': 'match', 'right': self._extract_name(other)}

    def __repr__(self) -> str:
        return f'< Column({self.name!r}) >'
