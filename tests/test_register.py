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


def test_select_returns_all_indices_when_target_none():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "a"
    reg[Id][(dim,)][(2,)] = "b"
    reg[Id][(dim,)][(3,)] = "c"
    result = list(reg.select(Id, (dim,)))
    assert result == [(1,), (2,), (3,)]


def test_select_filters_by_exact_match():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = "a"
    reg[Id][(dim,)][(2,)] = "b"
    result = list(reg.select(Id, (dim,), (1,)))
    assert result == [(1,)]


def test_select_filters_with_all_method():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = "a"
    reg[Id][(dim1, dim2)][(1, 20)] = "b"
    reg[Id][(dim1, dim2)][(2, 10)] = "c"
    result = list(reg.select(Id, (dim1, dim2), (Register.ALL, 10)))
    assert result == [(1, 10), (2, 10)]


def test_select_with_multiple_dimensions():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = "a"
    reg[Id][(dim1, dim2)][(1, 20)] = "b"
    reg[Id][(dim1, dim2)][(2, 10)] = "c"
    result = list(reg.select(Id, (dim1, dim2), (1, 10)))
    assert result == [(1, 10)]


# --- __repr__ tests ---


def test_method_repr_known():
    from register.register import Method

    assert repr(Method(0)) == "ALL"
    assert repr(Method(1)) == "SUM"
    assert repr(Method(2)) == "MAX"
    assert repr(Method(3)) == "MIN"
    assert repr(Method(4)) == "RANGE"


def test_method_repr_unknown():
    from register.register import Method

    assert repr(Method(99)) == "Method(99)"


def test_dimension_as_key_repr_empty():
    from register.register import DimensionAsKey

    dak = DimensionAsKey()
    assert repr(dak) == "DimensionAsKey(empty)"


def test_dimension_as_key_repr_with_data():
    from register.register import DimensionAsKey
    from register.dimension import Dimension

    dak = DimensionAsKey()
    dim = Dimension("Region", "区域", "R")
    dak[(dim,)][(1,)] = "a"
    dak[(dim,)][(2,)] = "b"
    result = repr(dak)
    assert "Region" in result
    assert "2" in result
    assert result.startswith("DimensionAsKey(")


def test_register_repr_empty():
    from register.register import Register

    reg = Register()
    assert repr(reg) == "Register(empty)"


def test_register_repr_with_data():
    from register.register import Register
    from register.parameter import Id, Name
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("House", "仓", "W")
    reg[Id][(dim,)][(1,)] = 1
    reg[Id][(dim,)][(2,)] = 2
    reg[Name][(dim,)][(1,)] = "Shanghai"

    result = repr(reg)
    assert "params=2" in result
    assert "cells=3" in result
    assert "id: 2" in result
    assert "name: 1" in result


# --- New tests from Task 6: MEAN, bounded TypeVar, and validate ---


class TestMethodEnum:
    def test_mean_exists(self) -> None:
        from register.register import Method
        assert Method(5) is not None

    def test_mean_repr(self) -> None:
        from register.register import Method
        assert repr(Method(5)) == "MEAN"

    def test_mean_equality(self) -> None:
        from register.register import Method
        assert Method(5) == Method(5)

    def test_mean_inequality(self) -> None:
        from register.register import Method
        assert Method(5) != Method(1)

    def test_all_methods(self) -> None:
        from register.register import Method
        names = {repr(Method(i)) for i in range(6)}
        assert names == {"ALL", "SUM", "MAX", "MIN", "RANGE", "MEAN"}


class TestRegisterClassMethods:
    def test_mean_class_attr(self) -> None:
        from register.register import Method, Register
        assert Register.MEAN == Method(5)

    def test_all_methods_present(self) -> None:
        from register.register import Method, Register
        assert Register.ALL == Method(0)
        assert Register.SUM == Method(1)
        assert Register.MAX == Method(2)
        assert Register.MIN == Method(3)
        assert Register.RANGE == Method(4)
        assert Register.MEAN == Method(5)


class TestRegisterValidate:
    def test_validate_empty_register(self) -> None:
        from register.register import Register
        reg = Register()
        assert reg.validate() is True

    def test_validate_valid_data(self) -> None:
        from register.register import Register
        from register.key import ParameterKey
        reg = Register()
        key = ParameterKey(1, "age", "年龄", int)
        dak = reg[key]
        dak[()][(1,)] = 25
        dak[()][(2,)] = 30
        assert reg.validate() is True

    def test_validate_invalid_data(self) -> None:
        from register.register import Register
        from register.key import ParameterKey
        reg = Register()
        key = ParameterKey(1, "age", "年龄", int)
        dak = reg[key]
        dak[()][(1,)] = 25
        dak[()][(2,)] = "not an int"
        assert reg.validate() is False

    def test_validate_multiple_keys(self) -> None:
        from register.register import Register
        from register.key import ParameterKey
        reg = Register()
        k1 = ParameterKey(1, "age", "年龄", int)
        k2 = ParameterKey(2, "name", "名称", str)
        reg[k1][()][(1,)] = 25
        reg[k2][()][(1,)] = "Alice"
        assert reg.validate() is True

    def test_validate_one_key_invalid(self) -> None:
        from register.register import Register
        from register.key import ParameterKey
        reg = Register()
        k1 = ParameterKey(1, "age", "年龄", int)
        k2 = ParameterKey(2, "name", "名称", str)
        reg[k1][()][(1,)] = 25
        reg[k2][()][(1,)] = 42
        assert reg.validate() is False
