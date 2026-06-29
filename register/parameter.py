from .key import ParameterKey

Id = ParameterKey(1, "id", "ID", int)
Code = ParameterKey(2, "code", "编码", str)
Name = ParameterKey(3, "name", "名称", str)


__all__ = [
    "Id",
    "Code",
    "Name",
]