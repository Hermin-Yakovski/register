from .key import NumKey, StrKey

Id = NumKey(1, "Id", "ID", int)
Code = StrKey(2, "Code", "编码")
Name = StrKey(3, "Name", "名称")

__all__ = [
    "Id",
    "Code",
    "Name",
]
