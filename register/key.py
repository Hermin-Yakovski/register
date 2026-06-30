from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .exception import RegisterError


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
    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any: ...

    @abstractmethod
    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]: ...


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

    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"sum not supported for {type(self).__name__}")

    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"mean not supported for {type(self).__name__}")

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"min not supported for {type(self).__name__}")

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"max not supported for {type(self).__name__}")

    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        raise NotImplementedError(f"range not supported for {type(self).__name__}")

    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        raise NotImplementedError(f"validate not supported for {type(self).__name__}")


class NumKey(_BaseKey):
    """Key for numerical values (int, float, bool)."""

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = float) -> None:
        super().__init__(id, name, name_cn)
        if vtype not in (float, int, bool):
            raise RegisterError(f"vtype must be float, int, or bool, got {vtype}")
        self.vtype = vtype

    def sum(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        return self.vtype(sum(selection.values()))

    def mean(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("mean requires at least one value")
        return sum(selection.values()) / len(selection)

    def min(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("min requires at least one value")
        return min(selection.values())

    def max(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("max requires at least one value")
        return max(selection.values())

    def range(self, selection: dict[tuple[int, ...], Any], **kwargs: Any) -> Any:
        if not selection:
            raise RegisterError("range requires at least one value")
        return max(selection.values()) - min(selection.values())

    def validate(
        self, selection: dict[tuple[int, ...], Any], **kwargs: Any
    ) -> dict[tuple[int, ...], bool]:
        return {idx: isinstance(v, self.vtype) for idx, v in selection.items()}
