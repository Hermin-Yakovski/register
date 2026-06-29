from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from .dimension import Dimension
from .exception import RegisterError


if TYPE_CHECKING:
    from .register import DimensionAsKey


class RegisterKey(ABC):
    """Public protocol for any class used as a key in Register[K].

    Provides identity (id, name, name_cn), five aggregation methods,
    and a validate method for checking stored data.
    """

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
    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool: ...


class _BaseKey(RegisterKey):
    """Internal base — not exported. Provides identity fields and common behavior."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: Any = None) -> None:
        self._id = id
        self._name = name
        self._name_cn = name_cn
        self.vtype = vtype

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._id == getattr(other, "_id", None)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn


class ParameterKey(_BaseKey):
    """Key for scalar values."""

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if self.vtype in (int, float, bool):
            return sum(args)
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            return dict(Counter(args))
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        if self.vtype in (int, float, bool):
            return sum(args) / len(args)
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        if self.vtype in (int, float, bool, str):
            return min(args)
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        if self.vtype in (int, float, bool, str):
            return max(args)
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        if self.vtype in (int, float, bool):
            return max(args) - min(args)
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                try:
                    if not isinstance(value, self.vtype):
                        return False
                except TypeError:
                    # vtype is an instance (e.g. Dimension), not a type class
                    if value is not self.vtype:
                        return False
        return True


class PositionKey(_BaseKey):
    """Key for positional values — tuples of the same length."""

    def __init__(
        self, id: int, name: str, name_cn: str, vtype: Any = None, arity: int = 0
    ) -> None:
        super().__init__(id, name, name_cn, vtype)
        if arity < 1:
            raise RegisterError("arity must be >= 1")
        self.arity = arity

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("sum requires at least one value")
        if self.vtype in (int, float, bool):
            return [sum(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("mean requires at least one value")
        if self.vtype in (int, float, bool):
            return [sum(elems) / len(args) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("min requires at least one value")
        if self.vtype in (int, float, bool):
            return [min(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("max requires at least one value")
        if self.vtype in (int, float, bool):
            return [max(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise RegisterError("range requires at least one value")
        if self.vtype in (int, float, bool):
            return [max(elems) - min(elems) for elems in zip(*args, strict=True)]
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                if not isinstance(value, tuple):
                    return False
                if len(value) != self.arity:
                    return False
                if not all(isinstance(elem, self.vtype) for elem in value):
                    return False
        return True


class IterableKey(_BaseKey):
    """Key for iterable values — variable-length collections of vtype."""

    def _validate_args(self, args: tuple[Any, ...]) -> None:
        for a in args:
            if not a:
                raise RegisterError("iterable must not be empty")

    def sum(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        if self.vtype in (int, float, bool):
            return [sum(a) for a in args]
        elif self.vtype is str or isinstance(self.vtype, Dimension):
            from collections import Counter
            return [dict(Counter(a)) for a in args]
        raise NotImplementedError(f"sum not implemented for vtype={self.vtype}")

    def mean(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool):
            return [sum(a) / len(a) for a in args]
        raise NotImplementedError(f"mean not implemented for vtype={self.vtype}")

    def min(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool, str):
            return [min(a) for a in args]
        raise NotImplementedError(f"min not implemented for vtype={self.vtype}")

    def max(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool, str):
            return [max(a) for a in args]
        raise NotImplementedError(f"max not implemented for vtype={self.vtype}")

    def range(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> Any:
        self._validate_args(args)
        if self.vtype in (int, float, bool):
            return [max(a) - min(a) for a in args]
        raise NotImplementedError(f"range not implemented for vtype={self.vtype}")

    def validate(self, data: DimensionAsKey, *args: Any, **kwargs: Any) -> bool:
        if self.vtype is None:
            return True
        for _dim_tuple, idx_dict in data._data.items():
            for _idx_tuple, value in idx_dict.items():
                try:
                    elements = iter(value)
                except TypeError:
                    return False
                if not all(isinstance(elem, self.vtype) for elem in elements):
                    return False
        return True