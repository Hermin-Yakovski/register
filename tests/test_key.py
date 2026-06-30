import pytest
from register.key import _BaseKey, RegisterKey


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
        k2 = ConcreteKey(1, "b", "B")
        assert hash(k1) == hash(k2)

    def test_eq_same_class(self):
        k1 = ConcreteKey(1, "a", "A")
        k2 = ConcreteKey(1, "b", "B")
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

    def test_is_register_key(self):
        k = ConcreteKey(1, "a", "A")
        assert isinstance(k, RegisterKey)