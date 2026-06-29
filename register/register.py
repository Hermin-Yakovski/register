from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Generic, TypeVar, TYPE_CHECKING

from .dimension import Dimension
from .key import RegisterKey

if TYPE_CHECKING:
    from typing import Generator, Iterator


K = TypeVar("K", bound=RegisterKey)

logger = logging.getLogger("register")


class Method(int):
    _NAMES: dict[int, str] = {0: "ALL", 1: "SUM", 2: "MAX", 3: "MIN", 4: "RANGE", 5: "MEAN"}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return False
        return int(self) == int(other)

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return True
        return int(self) != int(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        return self._NAMES.get(int(self), f"Method({int(self)})")


class DimensionAsKey:
    _data: dict[tuple[Any, ...], dict[tuple[int, ...], Any]]

    def __init__(self) -> None:
        self._data = defaultdict(dict)

    def __getitem__(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data[key]

    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        return iter(self._data)

    def __repr__(self) -> str:
        if not self._data:
            return "DimensionAsKey(empty)"
        parts = []
        for dim_tuple, idx_dict in self._data.items():
            dim_names = ",".join(repr(d) for d in dim_tuple)
            parts.append(f"({dim_names}): {len(idx_dict)}")
        return f"DimensionAsKey({{{', '.join(parts)}}})"

    def pop(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(key, {})


class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)
    _data: dict[K, DimensionAsKey]

    def __init__(self) -> None:
        self._data = defaultdict(DimensionAsKey)

    def __getitem__(self, key: K) -> DimensionAsKey:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        if not self._data:
            return "Register(empty)"
        total_cells = 0
        param_summaries = []
        for param, dak in self._data.items():
            cell_count = sum(len(idx_dict) for idx_dict in dak._data.values())
            total_cells += cell_count
            param_summaries.append(f"{param}: {cell_count}")
        return f"Register(params={len(self._data)}, cells={total_cells}, {{{', '.join(param_summaries)}}})"

    def select(
        self,
        key: K,
        dimension: tuple[Dimension, ...],
        target: tuple[int, ...] | None = None,
    ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(self.ALL == j or i == j for i, j in zip(index, target)):
                yield index

    def validate(self, **config: Any) -> bool:
        rs: bool = True
        for key in self._data:
            data = self._data[key]
            rs &= key.validate(data, **config)
        return rs


__all__ = [
    "Register",
]
