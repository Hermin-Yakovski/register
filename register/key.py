from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from .dimension import Dimension
from .exception import RegisterError

Selected = dict[tuple[int, ...], Any]


F = TypeVar("F", bound=Callable[..., Any])


def delegable(fn: F) -> F:
    """Mark a method as a delegable aggregation function."""
    fn._register_key_delegable = True  # type: ignore[attr-defined]
    return fn


class RegisterKey(ABC):
    """Public protocol for any class used as a key in Register[K]."""

    @property
    @abstractmethod
    def id(self) -> int: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def name_cn(self) -> str: ...

    @abstractmethod
    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]: ...


class _BaseKey(RegisterKey):
    """Internal base — not exported."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        self._id = id
        self._name = name
        self._name_cn = name_cn

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._id, self._name))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._id == getattr(other, "_id", None)
            and self._name == getattr(other, "_name", None)
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn

    @delegable
    def sum(self, selected: Selected) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    @delegable
    def mean(self, selected: Selected) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    @delegable
    def min(self, selected: Selected) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    @delegable
    def max(self, selected: Selected) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    @delegable
    def range(self, selected: Selected) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        raise NotImplementedError(f"validate not supported for {type(self).__name__}")


class NumKey(_BaseKey):
    """Key for numerical values (int, float, bool)."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    @delegable
    def sum(self, selected: Selected) -> Any:
        return self.vtype(sum(selected.values()))

    @delegable
    def mean(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("mean requires at least one value")
        return sum(selected.values()) / len(selected)

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return self.vtype(min(selected.values()))

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return self.vtype(max(selected.values()))

    @delegable
    def range(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return self.vtype(max(selected.values()) - min(selected.values()))

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {idx: isinstance(v, self.vtype) for idx, v in selected.items()}


class StrKey(_BaseKey):
    """Key for string values."""

    def __init__(self, id: int, name: str, name_cn: str) -> None:
        super().__init__(id, name, name_cn)

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        return {k: isinstance(v, str) for k, v in selected.items()}


class DimensionKey(_BaseKey):
    """Key for dimension values (always int)."""

    def __init__(self, id: int, dim: Dimension) -> None:
        super().__init__(id, dim.name + "Id", dim.name_cn + "ID")
        self._dim = dim

    @delegable
    def min(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("min requires at least one value")
        return min(selected.values())

    @delegable
    def max(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("max requires at least one value")
        return max(selected.values())

    @delegable
    def range(self, selected: Selected) -> Any:
        if not selected:
            raise RegisterError("range requires at least one value")
        return min(selected.values()), max(selected.values())

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id

        reference = kwargs["reference"]
        return {k: (v,) in reference[Id][self._dim,] for k, v in selected.items()}


class DimensionCollectionKey(_BaseKey):
    """Key for collections of dimension values."""

    def __init__(self, id: int, dim: Dimension, iter_type: type = list) -> None:
        super().__init__(id, dim.name + "Collection", dim.name_cn + "集合")
        if iter_type not in (set, list, tuple):
            raise RegisterError(f"iter_type must be set, list, or tuple, got {iter_type}")
        self._dim = dim
        self._iter_type = iter_type

    @delegable
    def min(self, selected: Selected) -> Selected:
        return {k: min(v) for k, v in selected.items()}

    @delegable
    def max(self, selected: Selected) -> Selected:
        return {k: max(v) for k, v in selected.items()}

    @delegable
    def range(self, selected: Selected) -> Selected:
        return {k: (min(v), max(v)) for k, v in selected.items()}

    def validate(self, selected: Selected, **kwargs: Any) -> dict[tuple[int, ...], bool]:
        from .parameter import Id

        reference = kwargs["reference"]
        result: dict[tuple[int, ...], bool] = {}
        for k, v in selected.items():
            if isinstance(v, self._iter_type):
                result[k] = all((elem,) in reference[Id][self._dim,] for elem in v)
            else:
                result[k] = False
        return result
