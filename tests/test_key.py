import pytest
from register.key import RegisterKey, ParameterKey, PositionKey, IterableKey


class TestRegisterKey:
    """RegisterKey is an ABC — cannot be instantiated directly."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RegisterKey()

    def test_subclass_must_implement_all_abstract(self):
        class IncompleteKey(RegisterKey):
            pass

        with pytest.raises(TypeError):
            IncompleteKey()


class TestBaseKeyViaParameterKey:
    """_BaseKey is private; test its behavior through ParameterKey."""

    def test_id_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.id == 1

    def test_name_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name == "age"

    def test_name_cn_property(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p.name_cn == "年龄"

    def test_str(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert str(p) == "age"

    def test_repr(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert repr(p) == "age"

    def test_hash_based_on_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "different", "不同", str)
        assert hash(p1) == hash(p2)

    def test_eq_same_class_same_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(1, "age", "年龄", int)
        assert p1 == p2

    def test_eq_same_class_different_id(self):
        p1 = ParameterKey(1, "age", "年龄", int)
        p2 = ParameterKey(2, "name", "名称", str)
        assert p1 != p2

    def test_eq_different_class_same_id(self):
        p = ParameterKey(1, "x", "X", int)
        pos = PositionKey(1, "x", "X", int, arity=2)
        assert p != pos

    def test_eq_with_non_key_object(self):
        p = ParameterKey(1, "age", "年龄", int)
        assert p != "not a key"
        assert p != 1

    def test_vtype_defaults_to_none(self):
        p = ParameterKey(1, "x", "X")
        assert p.vtype is None

    def test_isinstance_register_key(self):
        p = ParameterKey(1, "x", "X", int)
        assert isinstance(p, RegisterKey)
