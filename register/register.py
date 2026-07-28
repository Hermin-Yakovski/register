from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .dimension import Dimension
from .key import RegisterKey, Selected

if TYPE_CHECKING:
    from collections.abc import Iterator, KeysView, ValuesView


K = TypeVar("K", bound=RegisterKey)

logger = logging.getLogger("register")


class Selection(Generic[K]):
    _key: K
    _dims: tuple[Dimension, ...]
    _data: Selected

    def __init__(self, key: K, dims: tuple[Dimension, ...], data: Selected) -> None:
        self._key = key
        self._dims = dims
        self._data = data

    def items(self) -> Iterator[tuple[tuple[int, ...], Any]]:
        return iter(self._data.items())

    def values(self) -> Iterator[Any]:
        return iter(self._data.values())

    def keys(self) -> Iterator[tuple[int, ...]]:
        return iter(self._data.keys())

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: tuple[int, ...]) -> bool:
        return key in self._data

    def get(self, key: tuple[int, ...], default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            fn = getattr(self._key, name)
        except AttributeError:
            raise AttributeError(f"{type(self._key).__name__} has no delegable method '{name}'")
        if not callable(fn) or not getattr(fn, "_register_key_delegable", False):
            raise AttributeError(f"{type(self._key).__name__} has no delegable method '{name}'")

        def wrapper(**kwargs: Any) -> Any:
            return fn(self, **kwargs)

        return wrapper

    def __repr__(self) -> str:
        dim_names = ",".join(repr(d) for d in self._dims)
        return f"Selection({self._key}, ({dim_names}), {len(self._data)} entries)"


class IndexSpace(Generic[K]):
    _key: K
    _dims: tuple[Dimension, ...]
    _data: dict[tuple[int, ...], Any]

    def __init__(
        self, key: K, dims: tuple[Dimension, ...], data: dict[tuple[int, ...], Any]
    ) -> None:
        self._key = key
        self._dims = dims
        self._data = data

    def __getitem__(self, index: tuple[Any, ...]) -> Any | Selection[K]:
        if _has_slice(index):
            filtered = _resolve(index, self._data)
            return Selection(self._key, self._dims, filtered)
        return self._data[index]

    def __setitem__(self, index: tuple[int, ...], value: Any) -> None:
        self._data[index] = value

    def __contains__(self, index: tuple[int, ...]) -> bool:
        return index in self._data

    def update(self, other: dict[tuple[int, ...], Any]) -> None:
        self._data.update(other)

    def __repr__(self) -> str:
        dim_names = ",".join(repr(d) for d in self._dims)
        return f"IndexSpace({self._key}, ({dim_names}), {len(self._data)} entries)"

    def keys(self) -> KeysView[tuple[int, ...]]:
        return self._data.keys()

    def values(self) -> ValuesView[Any]:
        return self._data.values()

    @property
    def all(self) -> Selection[K]:
        return self[tuple(slice(None) for _ in self._dims)]

    @property
    def first(self) -> tuple[tuple[int, ...], Any]:
        return next(iter(self._data.items()))

    def __len__(self) -> int:
        return len(self._data)


class KeyView(Generic[K]):
    _key: K
    _data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]

    def __init__(
        self, key: K, data: dict[tuple[Dimension, ...], dict[tuple[int, ...], Any]]
    ) -> None:
        self._key = key
        self._data = data

    def __getitem__(self, dims: tuple[Dimension, ...]) -> IndexSpace[K]:
        if dims not in self._data:
            self._data[dims] = {}
        return IndexSpace(self._key, dims, self._data[dims])

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

    def validate(self, **kwargs: Any) -> Register[K]:
        result: Register[K] = Register()
        kwargs.setdefault("reference", self)
        for key in self._data:
            for dims in self._data[key]:
                result[key][dims].update(key.validate(self._data[key][dims], **kwargs))
        return result


def _has_slice(index: tuple[Any, ...]) -> bool:
    if not isinstance(index, tuple):
        index = (index,)
    return any(isinstance(elem, (slice, list)) for elem in index)


def _resolve(
    index: tuple[Any, ...], data: dict[tuple[int, ...], Any]
) -> dict[tuple[int, ...], Any]:
    if not isinstance(index, tuple):
        index = (index,)
    return {k: v for k, v in data.items() if _matches(k, index)}


def _matches(idx_tuple: tuple[int, ...], pattern: tuple[Any, ...]) -> bool:
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
    "IndexSpace",
    "KeyView",
    "Register",
    "Selection",
]
