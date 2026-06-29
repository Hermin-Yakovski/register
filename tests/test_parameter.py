def test_parameterkey_creation():
    from register.key import ParameterKey

    param = ParameterKey(1, "test", "测试", int)
    assert param.id == 1
    assert param.name == "test"
    assert param.name_cn == "测试"
    assert param.vtype is int


def test_parameterkey_default_vtype_is_none():
    from register.key import ParameterKey

    param = ParameterKey(1, "test", "测试")
    assert param.vtype is None


def test_parameterkey_str_returns_name():
    from register.key import ParameterKey

    param = ParameterKey(1, "test", "测试")
    assert str(param) == "test"


def test_parameterkey_repr_returns_name():
    from register.key import ParameterKey

    param = ParameterKey(1, "test", "测试")
    assert repr(param) == "test"
    # Explicitly call __repr__ to ensure line coverage
    assert param.__repr__() == "test"


def test_parameterkey_hashable():
    from register.key import ParameterKey

    param1 = ParameterKey(1, "test", "测试")
    param2 = ParameterKey(1, "test", "测试")
    assert hash(param1) == hash(param2)


def test_parameterkey_equality():
    from register.key import ParameterKey

    param1 = ParameterKey(1, "test", "测试")
    param2 = ParameterKey(1, "test", "测试")
    param3 = ParameterKey(2, "other", "其他")
    assert param1 == param2
    assert param1 != param3
    # Explicitly call __eq__ to ensure line coverage
    assert param1.__eq__(param2) is True
    assert param1.__eq__(param3) is False
    # Test with non-ParameterKey to cover the isinstance check
    assert param1.__eq__("not a parameterkey") is False
    assert param1.__eq__(None) is False


def test_parameterkey_equality_based_on_id():
    from register.key import ParameterKey

    param1 = ParameterKey(1, "name1", "测试1")
    param2 = ParameterKey(1, "name2", "测试2")
    assert param1 == param2  # Equal because ids match


def test_id_parameter_exists():
    from register.parameter import Id

    assert Id.id == 1
    assert Id.name == "id"
    assert Id.name_cn == "ID"
    assert Id.vtype is int


def test_code_parameter_exists():
    from register.parameter import Code

    assert Code.id == 2
    assert Code.name == "code"
    assert Code.name_cn == "编码"
    assert Code.vtype is str


def test_name_parameter_exists():
    from register.parameter import Name

    assert Name.id == 3
    assert Name.name == "name"
    assert Name.name_cn == "名称"
    assert Name.vtype is str


def test_parameterkey_implements_has_vtype_protocol():
    from register.key import ParameterKey

    param = ParameterKey(1, "test", "测试", int)
    assert hasattr(param, "vtype")
    assert param.vtype is int