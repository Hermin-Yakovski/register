import pytest
from register.key import _BaseKey, RegisterKey, NumKey, StrKey, DimensionKey, DimensionCollectionKey
from register.dimension import Dimension
from register.exception import RegisterError


class ConcreteKey(_BaseKey):
    """Minimal concrete key for testing _BaseKey."""
    pass


class TestBaseKey:
    def test_init(self):
        k = ConcreteKey(1, "test", "测试")
        assert k.id == 1
        assert k.name == "test"
        assert k.name_cn == "测试"

    def test_str_repr(self):
        k = ConcreteKey(1, "test", "测试")
        assert str(k) == "test"
        assert repr(k) == "test"

    def test_hash(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(1, "a", "B")
        assert hash(k1) == hash(k2)

    def test_eq_same_class(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(1, "a", "B")
        assert k1 == k2

    def test_eq_different_id(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(2, "a", "A")
        assert k1 != k2

    def test_eq_different_class(self):
        class OtherKey(_BaseKey):
            pass
        k1 = ConcreteKey(1, "a", "A")
        k2 = OtherKey(1, "a", "A")
        assert k1 != k2

    def test_sum_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="sum not supported"):
            k.sum({})

    def test_mean_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="mean not supported"):
            k.mean({})

    def test_min_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="min not supported"):
            k.min({})

    def test_max_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="max not supported"):
            k.max({})

    def test_range_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="range not supported"):
            k.range({})

    def test_validate_raises(self):
        k = ConcreteKey(1, "a", "A")
        with pytest.raises(NotImplementedError, match="validate not supported"):
            k.validate({})

    def test_is_register_key(self):
        k = ConcreteKey(1, "a", "A")
        assert isinstance(k, RegisterKey)

    def test_sum_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.sum, '_register_key_delegable', False) is True

    def test_mean_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.mean, '_register_key_delegable', False) is True

    def test_min_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        k = ConcreteKey(1, "a", "A")
        assert getattr(k.range, '_register_key_delegable', False) is True


class TestNumKey:
    def test_init_default_float(self):
        k = NumKey(1, "amount", "件量")
        assert k.vtype is float

    def test_init_int(self):
        k = NumKey(1, "count", "计数", int)
        assert k.vtype is int

    def test_init_bool(self):
        k = NumKey(1, "flag", "标志", bool)
        assert k.vtype is bool

    def test_init_invalid_vtype(self):
        with pytest.raises(RegisterError, match="vtype must be float, int, or bool"):
            NumKey(1, "bad", "坏", str)

    def test_sum_float(self):
        k = NumKey(1, "a", "A", float)
        result = k.sum({(1,): 1.5, (2,): 2.5})
        assert result == 4.0
        assert isinstance(result, float)

    def test_sum_int(self):
        k = NumKey(1, "a", "A", int)
        result = k.sum({(1,): 3, (2,): 7})
        assert result == 10
        assert isinstance(result, int)

    def test_sum_bool(self):
        k = NumKey(1, "a", "A", bool)
        result = k.sum({(1,): True, (2,): True, (3,): False})
        assert result is True  # bool(2) == True
        assert isinstance(result, bool)

    def test_sum_empty(self):
        k = NumKey(1, "a", "A", float)
        result = k.sum({})
        assert result == 0.0

    def test_mean_float(self):
        k = NumKey(1, "a", "A", float)
        result = k.mean({(1,): 2.0, (2,): 4.0})
        assert result == 3.0

    def test_mean_int(self):
        k = NumKey(1, "a", "A", int)
        result = k.mean({(1,): 2, (2,): 4})
        assert result == 3.0

    def test_mean_bool(self):
        k = NumKey(1, "a", "A", bool)
        result = k.mean({(1,): True, (2,): False, (3,): True})
        assert result == pytest.approx(2 / 3)

    def test_mean_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="mean requires at least one value"):
            k.mean({})

    def test_min_float(self):
        k = NumKey(1, "a", "A", float)
        assert k.min({(1,): 3.0, (2,): 1.0}) == 1.0

    def test_min_int(self):
        k = NumKey(1, "a", "A", int)
        assert k.min({(1,): 3, (2,): 1}) == 1

    def test_min_bool(self):
        k = NumKey(1, "a", "A", bool)
        assert k.min({(1,): True, (2,): False}) is False

    def test_min_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="min requires at least one value"):
            k.min({})

    def test_max_float(self):
        k = NumKey(1, "a", "A", float)
        assert k.max({(1,): 3.0, (2,): 1.0}) == 3.0

    def test_max_int(self):
        k = NumKey(1, "a", "A", int)
        assert k.max({(1,): 3, (2,): 1}) == 3

    def test_max_bool(self):
        k = NumKey(1, "a", "A", bool)
        assert k.max({(1,): True, (2,): False}) is True

    def test_max_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="max requires at least one value"):
            k.max({})

    def test_range_float(self):
        k = NumKey(1, "a", "A", float)
        assert k.range({(1,): 1.0, (2,): 5.0}) == 4.0

    def test_range_int(self):
        k = NumKey(1, "a", "A", int)
        assert k.range({(1,): 1, (2,): 5}) == 4

    def test_range_bool(self):
        k = NumKey(1, "a", "A", bool)
        assert k.range({(1,): True, (2,): False}) == 1

    def test_range_empty(self):
        k = NumKey(1, "a", "A", float)
        with pytest.raises(RegisterError, match="range requires at least one value"):
            k.range({})

    def test_validate_pass(self):
        k = NumKey(1, "a", "A", float)
        result = k.validate({(1,): 1.0, (2,): 2.0})
        assert result == {(1,): True, (2,): True}

    def test_validate_fail(self):
        k = NumKey(1, "a", "A", float)
        result = k.validate({(1,): 1.0, (2,): "bad"})
        assert result == {(1,): True, (2,): False}

    def test_validate_int(self):
        k = NumKey(1, "a", "A", int)
        result = k.validate({(1,): 5, (2,): 3.14})
        assert result == {(1,): True, (2,): False}

    def test_sum_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.sum, '_register_key_delegable', False) is True

    def test_mean_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.mean, '_register_key_delegable', False) is True

    def test_min_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        k = NumKey(1, "a", "A", float)
        assert getattr(k.range, '_register_key_delegable', False) is True


class TestStrKey:
    def test_init(self):
        k = StrKey(1, "name", "名称")
        assert k.id == 1
        assert k.name == "name"

    def test_min(self):
        k = StrKey(1, "a", "A")
        assert k.min({(1,): "banana", (2,): "apple"}) == "apple"

    def test_min_empty(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(RegisterError, match="min requires at least one value"):
            k.min({})

    def test_max(self):
        k = StrKey(1, "a", "A")
        assert k.max({(1,): "banana", (2,): "apple"}) == "banana"

    def test_max_empty(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(RegisterError, match="max requires at least one value"):
            k.max({})

    def test_sum_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.sum({(1,): "a"})

    def test_mean_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.mean({(1,): "a"})

    def test_range_raises(self):
        k = StrKey(1, "a", "A")
        with pytest.raises(NotImplementedError):
            k.range({(1,): "a"})

    def test_validate_pass(self):
        k = StrKey(1, "a", "A")
        result = k.validate({(1,): "hello", (2,): "world"})
        assert result == {(1,): True, (2,): True}

    def test_validate_fail(self):
        k = StrKey(1, "a", "A")
        result = k.validate({(1,): "hello", (2,): 42})
        assert result == {(1,): True, (2,): False}

    def test_min_is_delegable(self):
        k = StrKey(1, "a", "A")
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        k = StrKey(1, "a", "A")
        assert getattr(k.max, '_register_key_delegable', False) is True


class TestDimensionKey:
    def test_init(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.id == 1
        assert k.name == "locationId"
        assert k.name_cn == "地点ID"
        assert k._dim is dim

    def test_min(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.min({(1,): 3, (2,): 1}) == 1

    def test_min_empty(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(RegisterError):
            k.min({})

    def test_max(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.max({(1,): 3, (2,): 1}) == 3

    def test_max_empty(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(RegisterError, match="max requires at least one value"):
            k.max({})

    def test_range(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert k.range({(1,): 1, (2,): 5}) == (1, 5)

    def test_range_empty(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(RegisterError, match="range requires at least one value"):
            k.range({})

    def test_sum_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.sum({(1,): 1})

    def test_mean_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.mean({(1,): 1})

    def test_validate(self):
        from register import Register, Id
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        ref = Register()
        ref[Id][dim,][1,] = 1
        ref[Id][dim,][2,] = 2
        result = k.validate({(1,): 1, (2,): 3}, reference=ref)
        assert result == {(1,): True, (2,): False}

    def test_min_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionKey(1, dim)
        assert getattr(k.range, '_register_key_delegable', False) is True


class TestDimensionCollectionKey:
    def test_init_default_list(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert k._iter_type is list

    def test_init_set(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim, set)
        assert k._iter_type is set

    def test_init_invalid_type(self):
        dim = Dimension("location", "地点", "L")
        with pytest.raises(RegisterError, match="iter_type must be"):
            DimensionCollectionKey(1, dim, dict)

    def test_min_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.min({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): 1, (2,): 4}

    def test_max_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.max({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): 3, (2,): 5}

    def test_range_per_index(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        result = k.range({(1,): [3, 1, 2], (2,): [5, 4]})
        assert result == {(1,): (1, 3), (2,): (4, 5)}

    def test_sum_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.sum({(1,): [1, 2]})

    def test_mean_raises(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        with pytest.raises(NotImplementedError):
            k.mean({(1,): [1, 2]})

    def test_validate(self):
        from register import Register, Id
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        ref = Register()
        ref[Id][dim,][1,] = 1
        ref[Id][dim,][2,] = 2
        ref[Id][dim,][3,] = 3
        result = k.validate(
            {(1,): [1, 2], (2,): [1, 99], (3,): "bad"},
            reference=ref,
        )
        assert result == {(1,): True, (2,): False, (3,): False}

    def test_min_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.min, '_register_key_delegable', False) is True

    def test_max_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.max, '_register_key_delegable', False) is True

    def test_range_is_delegable(self):
        dim = Dimension("location", "地点", "L")
        k = DimensionCollectionKey(1, dim)
        assert getattr(k.range, '_register_key_delegable', False) is True


class TestDelegable:
    def test_marks_function(self):
        from register.key import delegable

        def my_func(self, selected):
            return None

        decorated = delegable(my_func)
        assert getattr(decorated, "_register_key_delegable", False) is True

    def test_returns_same_function(self):
        from register.key import delegable

        def my_func(self, selected):
            return None

        decorated = delegable(my_func)
        assert decorated is my_func

    def test_unmarked_function_has_no_marker(self):
        def my_func(self, selected):
            return None

        assert getattr(my_func, "_register_key_delegable", False) is False
