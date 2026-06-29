import pytest
from register.key import RegisterKey, ParameterKey, PositionKey, IterableKey
from register.register import DimensionAsKey


class TestRegisterKey:
    """RegisterKey is an ABC — cannot be instantiated directly."""

    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            RegisterKey()

    def test_subclass_must_implement_all_abstract(self) -> None:
        class IncompleteKey(RegisterKey):
            pass

        with pytest.raises(TypeError):
            IncompleteKey()


class TestBaseKeyViaParameterKey:
    """_BaseKey is private; test its behavior through ParameterKey."""

    def test_id_property(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert p.id == 1

    def test_name_property(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name == "age"

    def test_name_cn_property(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name_cn == "年龄"

    def test_str(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert str(p) == "age"

    def test_repr(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert repr(p) == "age"

    def test_hash_based_on_id(self) -> None:
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "different", "不同", str)
        assert hash(p1) == hash(p2)

    def test_eq_same_class_same_id(self) -> None:
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "age", "年龄", int)
        assert p1 == p2

    def test_eq_same_class_different_id(self) -> None:
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(2, "name", "名称", str)
        assert p1 != p2

    def test_eq_different_class_same_id(self) -> None:
        p = ParameterKey(1, "x", "X", int)
        pos = PositionKey(1, "x", "X", int, arity=2)
        assert p != pos

    def test_eq_with_non_key_object(self) -> None:
        p = ParameterKey(1, "age", "年龄", int)
        assert p != "not a key"
        assert p != 1

    def test_vtype_defaults_to_none(self) -> None:
        p = ParameterKey(1, "x", "X")
        assert p.vtype is None

    def test_isinstance_register_key(self) -> None:
        p = ParameterKey(1, "x", "X", int)
        assert isinstance(p, RegisterKey)


class TestParameterKeySum:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_sum_int(self) -> None:
        k = self._make_key(int)
        assert k.sum(DimensionAsKey(), 1, 2, 3) == 6

    def test_sum_float(self) -> None:
        k = self._make_key(float)
        assert k.sum(DimensionAsKey(), 1.5, 2.5) == 4.0

    def test_sum_bool(self) -> None:
        k = self._make_key(bool)
        assert k.sum(DimensionAsKey(), True, False, True) == 2

    def test_sum_int_empty(self) -> None:
        k = self._make_key(int)
        assert k.sum(DimensionAsKey()) == 0

    def test_sum_str(self) -> None:
        k = self._make_key(str)
        result = k.sum(DimensionAsKey(), "a", "b", "a", "c")
        assert result == {"a": 2, "b": 1, "c": 1}

    def test_sum_str_empty(self) -> None:
        k = self._make_key(str)
        assert k.sum(DimensionAsKey()) == {}

    def test_sum_dimension(self) -> None:
        from register.dimension import Dimension
        d1 = Dimension("r1", "区域1", "R1")
        d2 = Dimension("r2", "区域2", "R2")
        k = ParameterKey(1, "test", "测试", d1)
        result = k.sum(DimensionAsKey(), d1, d2, d1)
        assert result == {d1: 2, d2: 1}

    def test_sum_unsupported_vtype(self) -> None:
        k = self._make_key(list)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), [1], [2])


class TestParameterKeyMean:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_mean_int(self) -> None:
        k = self._make_key(int)
        assert k.mean(DimensionAsKey(), 2, 4, 6) == 4.0

    def test_mean_float(self) -> None:
        k = self._make_key(float)
        assert k.mean(DimensionAsKey(), 1.0, 3.0) == 2.0

    def test_mean_bool(self) -> None:
        k = self._make_key(bool)
        assert k.mean(DimensionAsKey(), True, False, True) == pytest.approx(2 / 3)

    def test_mean_empty_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey())

    def test_mean_str_not_implemented(self) -> None:
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.mean(DimensionAsKey(), "a", "b")


class TestParameterKeyMin:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_min_int(self) -> None:
        k = self._make_key(int)
        assert k.min(DimensionAsKey(), 3, 1, 2) == 1

    def test_min_float(self) -> None:
        k = self._make_key(float)
        assert k.min(DimensionAsKey(), 3.5, 1.5, 2.5) == 1.5

    def test_min_bool(self) -> None:
        k = self._make_key(bool)
        assert k.min(DimensionAsKey(), True, False, True) is False

    def test_min_str(self) -> None:
        k = self._make_key(str)
        assert k.min(DimensionAsKey(), "banana", "apple", "cherry") == "apple"

    def test_min_empty_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.min(DimensionAsKey())

    def test_min_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.min(DimensionAsKey(), d)


class TestParameterKeyMax:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_max_int(self) -> None:
        k = self._make_key(int)
        assert k.max(DimensionAsKey(), 3, 1, 2) == 3

    def test_max_float(self) -> None:
        k = self._make_key(float)
        assert k.max(DimensionAsKey(), 3.5, 1.5, 2.5) == 3.5

    def test_max_bool(self) -> None:
        k = self._make_key(bool)
        assert k.max(DimensionAsKey(), True, False, True) is True

    def test_max_str(self) -> None:
        k = self._make_key(str)
        assert k.max(DimensionAsKey(), "banana", "apple", "cherry") == "cherry"

    def test_max_empty_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.max(DimensionAsKey())

    def test_max_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.max(DimensionAsKey(), d)


class TestParameterKeyRange:
    def _make_key(self, vtype):
        return ParameterKey(1, "test", "测试", vtype)

    def test_range_int(self) -> None:
        k = self._make_key(int)
        assert k.range(DimensionAsKey(), 3, 1, 5) == 4

    def test_range_float(self) -> None:
        k = self._make_key(float)
        assert k.range(DimensionAsKey(), 3.5, 1.5, 2.5) == 2.0

    def test_range_bool(self) -> None:
        k = self._make_key(bool)
        assert k.range(DimensionAsKey(), True, False) == 1

    def test_range_empty_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.range(DimensionAsKey())

    def test_range_str_not_implemented(self) -> None:
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), "a", "b")

    def test_range_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = ParameterKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), d)


class TestPositionKeyConstructor:
    def test_arity_stored(self) -> None:
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        assert k.arity == 2

    def test_arity_zero_raises(self) -> None:
        from register.exception import RegisterError
        with pytest.raises(RegisterError):
            PositionKey(1, "xy", "坐标", float, arity=0)

    def test_arity_negative_raises(self) -> None:
        from register.exception import RegisterError
        with pytest.raises(RegisterError):
            PositionKey(1, "xy", "坐标", float, arity=-1)

    def test_isinstance_register_key(self) -> None:
        k = PositionKey(1, "xy", "坐标", float, arity=2)
        assert isinstance(k, RegisterKey)

    def test_eq_same_class_same_id(self) -> None:
        k1 = PositionKey(1, "xy", "坐标", float, arity=2)
        k2 = PositionKey(1, "xy", "坐标", float, arity=3)
        assert k1 == k2

    def test_eq_different_class(self) -> None:
        p = ParameterKey(1, "x", "X", int)
        pos = PositionKey(1, "x", "X", int, arity=2)
        assert p != pos


class TestPositionKeyAggregation:
    def _make_key(self, vtype=float, arity=3):
        return PositionKey(1, "xyz", "坐标", vtype, arity=arity)

    def test_sum_int(self) -> None:
        k = self._make_key(int, arity=3)
        result = k.sum(DimensionAsKey(), (1, 2, 3), (4, 5, 6))
        assert result == [5, 7, 9]

    def test_sum_float(self) -> None:
        k = self._make_key(float, arity=2)
        result = k.sum(DimensionAsKey(), (1.0, 2.0), (3.0, 4.0))
        assert result == [4.0, 6.0]

    def test_sum_bool(self) -> None:
        k = self._make_key(bool, arity=2)
        result = k.sum(DimensionAsKey(), (True, False), (True, True))
        assert result == [2, 1]

    def test_mean_float(self) -> None:
        k = self._make_key(float, arity=3)
        result = k.mean(DimensionAsKey(), (1.0, 2.0, 3.0), (3.0, 4.0, 5.0))
        assert result == [2.0, 3.0, 4.0]

    def test_min_int(self) -> None:
        k = self._make_key(int, arity=3)
        result = k.min(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [1, 2, 3]

    def test_max_int(self) -> None:
        k = self._make_key(int, arity=3)
        result = k.max(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [4, 5, 6]

    def test_range_int(self) -> None:
        k = self._make_key(int, arity=3)
        result = k.range(DimensionAsKey(), (1, 5, 3), (4, 2, 6))
        assert result == [3, 3, 3]

    def test_mismatched_lengths_raises(self) -> None:
        k = self._make_key(int, arity=3)
        with pytest.raises(ValueError):
            k.sum(DimensionAsKey(), (1, 2, 3), (4, 5))

    def test_empty_args_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int, arity=3)
        with pytest.raises(RegisterError):
            k.sum(DimensionAsKey())

    def test_mean_empty_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(float, arity=2)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey())

    def test_str_vtype_not_implemented(self) -> None:
        k = PositionKey(1, "x", "X", str, arity=2)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), ("a", "b"))


class TestIterableKeyAggregation:
    def _make_key(self, vtype=int):
        return IterableKey(1, "scores", "分数", vtype)

    # sum
    def test_sum_int(self) -> None:
        k = self._make_key(int)
        result = k.sum(DimensionAsKey(), [1, 2, 3], [4, 5])
        assert result == [6, 9]

    def test_sum_float(self) -> None:
        k = self._make_key(float)
        result = k.sum(DimensionAsKey(), [1.0, 2.0], [3.0])
        assert result == [3.0, 3.0]

    def test_sum_bool(self) -> None:
        k = self._make_key(bool)
        result = k.sum(DimensionAsKey(), [True, False, True], [True])
        assert result == [2, 1]

    def test_sum_int_empty_iterable(self) -> None:
        k = self._make_key(int)
        result = k.sum(DimensionAsKey(), [], [1, 2])
        assert result == [0, 3]

    def test_sum_str(self) -> None:
        k = self._make_key(str)
        result = k.sum(DimensionAsKey(), ["a", "b", "a"], ["c"])
        assert result == [{"a": 2, "b": 1}, {"c": 1}]

    def test_sum_dimension(self) -> None:
        from register.dimension import Dimension
        d1 = Dimension("r1", "区域1", "R1")
        d2 = Dimension("r2", "区域2", "R2")
        k = IterableKey(1, "test", "测试", d1)
        result = k.sum(DimensionAsKey(), [d1, d2, d1], [d2])
        assert result == [{d1: 2, d2: 1}, {d2: 1}]

    def test_sum_empty_args(self) -> None:
        k = self._make_key(int)
        result = k.sum(DimensionAsKey())
        assert result == []

    def test_sum_unsupported_vtype(self) -> None:
        k = IterableKey(1, "test", "测试", list)
        with pytest.raises(NotImplementedError):
            k.sum(DimensionAsKey(), [[1], [2]])

    # mean
    def test_mean_int(self) -> None:
        k = self._make_key(int)
        result = k.mean(DimensionAsKey(), [1, 2, 3], [4, 5])
        assert result == [2.0, 4.5]

    def test_mean_empty_iterable_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.mean(DimensionAsKey(), [])

    def test_mean_str_not_implemented(self) -> None:
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.mean(DimensionAsKey(), ["a", "b"])

    # min
    def test_min_int(self) -> None:
        k = self._make_key(int)
        result = k.min(DimensionAsKey(), [3, 1, 2], [5, 4])
        assert result == [1, 4]

    def test_min_str(self) -> None:
        k = self._make_key(str)
        result = k.min(DimensionAsKey(), ["banana", "apple", "cherry"], ["date", "elderberry"])
        assert result == ["apple", "date"]

    def test_min_empty_iterable_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.min(DimensionAsKey(), [])

    def test_min_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.min(DimensionAsKey(), [d])

    # max
    def test_max_int(self) -> None:
        k = self._make_key(int)
        result = k.max(DimensionAsKey(), [3, 1, 2], [5, 4])
        assert result == [3, 5]

    def test_max_str(self) -> None:
        k = self._make_key(str)
        result = k.max(DimensionAsKey(), ["banana", "apple", "cherry"], ["date", "elderberry"])
        assert result == ["cherry", "elderberry"]

    def test_max_empty_iterable_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.max(DimensionAsKey(), [])

    def test_max_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.max(DimensionAsKey(), [d])

    # range
    def test_range_int(self) -> None:
        k = self._make_key(int)
        result = k.range(DimensionAsKey(), [3, 1, 5], [4, 2])
        assert result == [4, 2]

    def test_range_empty_iterable_raises(self) -> None:
        from register.exception import RegisterError
        k = self._make_key(int)
        with pytest.raises(RegisterError):
            k.range(DimensionAsKey(), [])

    def test_range_str_not_implemented(self) -> None:
        k = self._make_key(str)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), ["a", "b"])

    def test_range_dimension_not_implemented(self) -> None:
        from register.dimension import Dimension
        d = Dimension("r", "区域", "R")
        k = IterableKey(1, "test", "测试", d)
        with pytest.raises(NotImplementedError):
            k.range(DimensionAsKey(), [d])

    # isinstance
    def test_isinstance_register_key(self) -> None:
        k = IterableKey(1, "scores", "分数", int)
        assert isinstance(k, RegisterKey)