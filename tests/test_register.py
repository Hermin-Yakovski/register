import pytest

def test_method_class_exists():
    from register.register import Method
    m = Method(1)
    assert int(m) == 1

def test_method_equality():
    from register.register import Method
    m1 = Method(1)
    m2 = Method(1)
    m3 = Method(2)
    assert m1 == m2
    assert m1 != m3

def test_method_not_equal_to_int():
    from register.register import Method
    m = Method(1)
    assert m != 1
    assert m != "1"

def test_method_hashable():
    from register.register import Method
    m1 = Method(1)
    m2 = Method(1)
    assert hash(m1) == hash(m2)
    {m1: "value"}  # Should not raise

def test_register_all_method():
    from register.register import Register
    assert int(Register.ALL) == 0

def test_register_sum_method():
    from register.register import Register
    assert int(Register.SUM) == 1

def test_register_max_method():
    from register.register import Register
    assert int(Register.MAX) == 2

def test_register_min_method():
    from register.register import Register
    assert int(Register.MIN) == 3

def test_register_range_method():
    from register.register import Register
    assert int(Register.RANGE) == 4

def test_dimension_as_key_init():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    assert dak is not None

def test_dimension_as_key_getitem_returns_dict():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    result = dak[key]
    assert isinstance(result, dict)

def test_dimension_as_key_iterable():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    _ = dak[key]
    assert key in iter(dak)

def test_dimension_as_key_pop_removes_key():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    key = ("dim1", "dim2")
    _ = dak[key]
    result = dak.pop(key)
    assert result == {}
    assert key not in iter(dak)

def test_dimension_as_key_pop_nonexistent_returns_empty():
    from register.register import DimensionAsKey
    dak = DimensionAsKey()
    result = dak.pop(("nonexistent",))
    assert result == {}

def test_register_getitem_returns_dimension_as_key():
    from register.register import Register, DimensionAsKey
    from register.parameter import Id
    reg = Register()
    result = reg[Id]
    assert isinstance(result, DimensionAsKey)

def test_register_iteration_yields_parameters():
    from register.register import Register
    from register.parameter import Id
    reg = Register()
    _ = reg[Id]
    assert Id in iter(reg)

def test_register_contains():
    from register.register import Register
    from register.parameter import Id, Code
    reg = Register()
    _ = reg[Id]
    assert Id in reg
    assert Code not in reg

def test_register_store_and_retrieve_value():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension
    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    assert reg[Id][(dim,)][(1,)] == 42
