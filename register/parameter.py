from .key import NumKey, StrKey

Id = NumKey(1, "id", "ID", int)
Code = StrKey(2, "code", "编码")
Name = StrKey(3, "name", "名称")

__all__ = [
    "Id",
    "Code",
    "Name",
]
