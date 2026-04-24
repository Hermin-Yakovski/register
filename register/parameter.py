from typing import Any, Type


class Parameter:
    _id: int
    _name: str
    _name_cn: str
    vtype: Type

    def __init__(self, id: int, name: str, name_cn: str, vtype: Type = Any):
        self._id = id
        self._name = name
        self._name_cn = name_cn
        self.vtype = vtype

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other.id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def name_cn(self):
        return self._name_cn


# Common parameters used across all services
Id = Parameter(1, 'id', 'ID', int)
Code = Parameter(2, 'code', '编码', str)
Name = Parameter(3, 'name', '名称', str)
