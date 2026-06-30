from __future__ import annotations

import logging
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


_METHOD_NAMES: dict[int, str] = {
    1: "sum",
    2: "max",
    3: "min",
    4: "range",
    5: "mean",
}


class Selection(Generic[K]):
    _key: K
    _data: dict[tuple[int, ...], Any]

    def __init__(self, key: K, data: dict[tuple[int, ...], Any]) -> None:
        self._key = key
        self._data = data

    def sum(self, **kwargs: Any) -> Any:
        return self._key.sum(self._data, **kwargs)

    def mean(self, **kwargs: Any) -> Any:
        return self._key.mean(self._data, **kwargs)

    def min(self, **kwargs: Any) -> Any:
        return self._key.min(self._data, **kwargs)

    def max(self, **kwargs: Any) -> Any:
        return self._key.max(self._data, **kwargs)

    def range(self, **kwargs: Any) -> Any:
        return self._key.range(self._data, **kwargs)

    def agg(self, method: Method, **kwargs: Any) -> Any:
        name = _METHOD_NAMES[int(method)]
        fn = getattr(self._key, name)
        return fn(self._data, **kwargs)


class IndexSpace(Generic[K]):
    _key: K
    _data: dict[tuple[int, ...], Any]

    def __init__(self, key: K, data: dict[tuple[int, ...], Any]) -> None:
        self._key = key
        self._data = data

    def __getitem__(self, index: tuple) -> Any | Selection[K]:
        if _has_slice(index):
            filtered = _resolve(index, self._data)
            return Selection(self._key, filtered)
        return self._data[index]

    def __setitem__(self, index: tuple[int, ...], value: Any) -> None:
        self._data[index] = value

    def __contains__(self, index: tuple[int, ...]) -> bool:
        return index in self._data

    def update(self, other: dict[tuple[int, ...], Any]) -> None:
        self._data.update(other)

    def __repr__(self) -> str:
        return f"IndexSpace({self._key}, {len(self._data)} entries)"


class KeyView(Generic[K]):
    _key: K
    _data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]

    def __init__(self, key: K, data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]) -> None:
        self._key = key
        self._data = data

    def __getitem__(self, dims: tuple[Dimension, ...]) -> IndexSpace[K]:
        if dims not in self._data:
            self._data[dims] = {}
        return IndexSpace(self._key, self._data[dims])

    def __iter__(self) -> Iterator[tuple[Dimension, ...]]:
        return iter(self._data)

    def __repr__(self) -> str:
        if not self._data:
            return f"KeyView({self._key}, empty)"
        parts = []
        for dim_tuple, idx_dict in self._data.items():
            dim_names = ",".join(repr(d) for d in dim_tuple)
            parts.append(f"({dim_names}): {len(idx_dict)}")
        return f"KeyView({self._key}, {{{', '.join(parts)}}})"

    def pop(self, dims: tuple[Dimension, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(dims, {})


class Register(Generic[K]):
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    MEAN: Method = Method(5)

    _data: dict[K, dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]]

    def __init__(self) -> None:
        self._data = {}

    def __getitem__(self, key: K) -> KeyView[K]:
        if key not in self._data:
            self._data[key] = {}
        return KeyView(key, self._data[key])

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        if not self._data:
            return "Register(empty)"
        total_cells = 0
        param_summaries = []
        for param, dim_data in self._data.items():
            cell_count = sum(len(idx_dict) for idx_dict in dim_data.values())
            total_cells += cell_count
            param_summaries.append(f"{param}: {cell_count}")
        return f"Register(params={len(self._data)}, cells={total_cells}, {{{', '.join(param_summaries)}}})"

    def select(
        self,
        key: K,
        dimension: tuple[Dimension, ...],
        target: tuple[int | None, ...] | None = None,
    ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(j is None or i == j for i, j in zip(index, target)):
                yield index

    def validate(self, **kwargs: Any) -> Register[K]:
        result: Register[K] = Register()
        for key in self._data:
            for dims in self._data[key]:
                result[key][dims].update(key.validate(self._data[key][dims], **kwargs))
        return result


def _has_slice(index: tuple) -> bool:
    if not isinstance(index, tuple):
        index = (index,)
    return any(isinstance(elem, (slice, list)) for elem in index)


def _resolve(index: tuple, data: dict[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
    if not isinstance(index, tuple):
        index = (index,)
    return {k: v for k, v in data.items() if _matches(k, index)}


def _matches(idx_tuple: tuple[int, ...], pattern: tuple) -> bool:
    for actual, selector in zip(idx_tuple, pattern):
        if isinstance(selector, int):
            if actual != selector:
                return False
        elif isinstance(selector, list):
            if actual not in selector:
                return False
        elif isinstance(selector, slice):
            if selector.start is not None and actual < selector.start:
                return False
            if selector.stop is not None and actual >= selector.stop:
                return False
    return True


__all__ = [
    "Register",
    "Method",
    "KeyView",
    "IndexSpace",
    "Selection",
]
