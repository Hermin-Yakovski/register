import pytest
from typing import Any

def test_parameter_creation():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试", int)
    assert param.id == 1
    assert param.name == "test"
    assert param.name_cn == "测试"
    assert param.vtype == int

def test_parameter_default_vtype_is_any():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert param.vtype == Any

def test_parameter_str_returns_name():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert str(param) == "test"

def test_parameter_repr_returns_name():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试")
    assert repr(param) == "test"

def test_parameter_hashable():
    from register.parameter import Parameter
    param1 = Parameter(1, "test", "测试")
    param2 = Parameter(1, "test", "测试")
    assert hash(param1) == hash(param2)

def test_parameter_equality():
    from register.parameter import Parameter
    param1 = Parameter(1, "test", "测试")
    param2 = Parameter(1, "test", "测试")
    param3 = Parameter(2, "other", "其他")
    assert param1 == param2
    assert param1 != param3

def test_parameter_equality_based_on_id():
    from register.parameter import Parameter
    param1 = Parameter(1, "name1", "测试1")
    param2 = Parameter(1, "name2", "测试2")
    assert param1 == param2  # Equal because ids match

def test_id_parameter_exists():
    from register.parameter import Id
    assert Id.id == 1
    assert Id.name == "id"
    assert Id.name_cn == "ID"
    assert Id.vtype == int

def test_code_parameter_exists():
    from register.parameter import Code, Any
    assert Code.id == 2
    assert Code.name == "code"
    assert Code.name_cn == "编码"
    assert Code.vtype == str

def test_name_parameter_exists():
    from register.parameter import Name
    assert Name.id == 3
    assert Name.name == "name"
    assert Name.name_cn == "名称"
    assert Name.vtype == str

def test_parameter_implements_has_vtype_protocol():
    from register.parameter import Parameter
    param = Parameter(1, "test", "测试", int)
    assert hasattr(param, "vtype")
    assert param.vtype == int
