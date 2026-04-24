from typing import Any, TypeVar

K = TypeVar("K")


class Parameter:
    _id: int
    _name: str
    _name_cn: str
    vtype: type

    def __init__(self, id: int, name: str, name_cn: str, vtype: type = Any) -> None:
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
        return isinstance(other, Parameter) and self._id == other.id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn


# Common parameters used across all services
Id = Parameter(1, "id", "ID", int)
Code = Parameter(2, "code", "编码", str)
Name = Parameter(3, "name", "名称", str)
