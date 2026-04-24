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


def test_as_frames_empty_register():
    from register.register import Register

    reg = Register()
    frames = reg.as_frames()
    assert frames == {}


def test_as_frames_single_value():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    frames = reg.as_frames()
    assert len(frames) == 1
    df = frames[(dim,)]
    assert df.iloc[0]["id"] == 42  # Parameter value is in "id" column


def test_as_frames_multiple_parameters():
    from register.register import Register
    from register.parameter import Id, Name
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    reg[Name][(dim,)][(1,)] = "test_name"
    frames = reg.as_frames()
    df = frames[(dim,)]
    assert df.iloc[0]["id"] == 42
    assert df.iloc[0]["name"] == "test_name"


def test_as_frames_display_cn():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    reg[Id][(dim,)][(1,)] = 42
    frames = reg.as_frames(display_cn=True)
    df = frames[(dim,)]
    assert "测试" in df.columns
    assert df.iloc[0]["ID"] == 42


def test_as_frames_multiple_dimensions():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    reg[Id][(dim1, dim2)][(1, 10)] = 42
    frames = reg.as_frames()
    df = frames[(dim1, dim2)]
    assert df.iloc[0]["test1"] == 1
    assert df.iloc[0]["test2"] == 10
    assert df.iloc[0]["id"] == 42


def test_as_frames_multiple_dimension_keys_for_same_parameter():
    from register.register import Register
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")
    # Same parameter (Id) with different dimension combinations
    reg[Id][(dim1,)][(1,)] = 100
    reg[Id][(dim2,)][(2,)] = 200
    frames = reg.as_frames()
    # Should have two separate frames
    assert len(frames) == 2
    # Check first frame
    df1 = frames[(dim1,)]
    assert df1.iloc[0]["test1"] == 1
    assert df1.iloc[0]["id"] == 100
    # Check second frame
    df2 = frames[(dim2,)]
    assert df2.iloc[0]["test2"] == 2
    assert df2.iloc[0]["id"] == 200


def test_validate_with_valid_data_no_errors():
    from register.register import Register, DimensionAsKey
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[Id][(dim,)][(1,)] = 42
    # Should not raise
    reg.validate(dim_registry)


def test_validate_with_invalid_type_logs_warning():
    from register.register import Register, DimensionAsKey
    from register.parameter import Id
    from register.dimension import Dimension

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[Id][(dim,)][(1,)] = "not_an_int"  # Wrong type
    # Should log warning but not raise
    reg.validate(dim_registry, raise_errors=False)


def test_validate_with_invalid_type_raises_error():
    from register.register import Register, DimensionAsKey
    from register.parameter import Id
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[Id][(dim,)][(1,)] = "not_an_int"
    with pytest.raises(ValidationError):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_any_type_accepts_anything():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from typing import Any

    reg = Register()
    param = Parameter(100, "any_param", "任意参数", Any)
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[param][(dim,)][(1,)] = "anything"
    reg.validate(dim_registry, raise_errors=True)  # Should not raise


def test_validate_with_list_type():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension

    reg = Register()
    param = Parameter(100, "list_param", "列表参数", list[int])
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[param][(dim,)][(1,)] = [1, 2, 3]
    reg.validate(dim_registry, raise_errors=True)  # Should not raise


def test_validate_with_invalid_list_element_type():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    param = Parameter(100, "list_param", "列表参数", list[int])
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None  # Register index 1 as valid
    reg[param][(dim,)][(1,)] = [1, "not_int", 3]
    with pytest.raises(ValidationError):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_invalid_container_type_not_list():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    param = Parameter(100, "list_param", "列表参数", list[int])
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None
    reg[param][(dim,)][(1,)] = "not_a_list"  # String instead of list
    with pytest.raises(ValidationError, match="expected <class 'list'>"):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_invalid_container_type_not_set():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    param = Parameter(100, "set_param", "集合参数", set[int])
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None
    reg[param][(dim,)][(1,)] = [1, 2, 3]  # List instead of set
    with pytest.raises(ValidationError, match="expected <class 'set'>"):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_invalid_container_type_not_tuple():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    param = Parameter(100, "tuple_param", "元组参数", tuple[int])
    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()
    dim_registry[(dim,)][(1,)] = None
    reg[param][(dim,)][(1,)] = {1, 2, 3}  # Set instead of tuple
    with pytest.raises(ValidationError, match="expected <class 'tuple'>"):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_list_of_dimension_valid():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension

    reg = Register()
    # Define a dimension to be used as the element type
    region_dim = Dimension("region", "地区", "REG")
    # Create a Parameter with vtype=list[region_dim] (list of that dimension)
    param = Parameter(100, "regions_param", "地区参数", list[region_dim])

    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()

    # Register index 1 for dim, and indices 1, 2, 3 for region_dim
    dim_registry[(dim,)][(1,)] = None
    dim_registry[(region_dim,)][(1,)] = None
    dim_registry[(region_dim,)][(2,)] = None
    dim_registry[(region_dim,)][(3,)] = None

    # Store a list of valid indices - should not raise
    reg[param][(dim,)][(1,)] = [1, 2, 3]
    reg.validate(dim_registry, raise_errors=True)  # Should not raise


def test_validate_with_list_of_dimension_invalid_element():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    # Define a dimension to be used as the element type
    region_dim = Dimension("region", "地区", "REG")
    # Create a Parameter with vtype=list[region_dim] (list of that dimension)
    param = Parameter(100, "regions_param", "地区参数", list[region_dim])

    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()

    # Register index 1 for dim, and indices 1, 2, 3 for region_dim
    dim_registry[(dim,)][(1,)] = None
    dim_registry[(region_dim,)][(1,)] = None
    dim_registry[(region_dim,)][(2,)] = None
    dim_registry[(region_dim,)][(3,)] = None

    # Store a list with an invalid index (5) - should raise ValidationError
    reg[param][(dim,)][(1,)] = [1, 2, 5]
    with pytest.raises(ValidationError, match="value 5 does not match any index of dimension region"):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_dimension_type():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension

    reg = Register()
    # Define dim2 as the dimension type for the parameter
    dim2 = Dimension("test2", "测试2", "TS2")
    param = Parameter(100, "dim_param", "维度参数", dim2)

    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()

    # Register index 1 as valid for dim, and index 3 as valid for dim2
    dim_registry[(dim,)][(1,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store 3 as value - should be valid since it's registered in dim2
    reg[param][(dim,)][(1,)] = 3
    reg.validate(dim_registry, raise_errors=True)  # Should not raise


def test_validate_with_invalid_dimension_value():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import ValidationError

    reg = Register()
    # Define dim2 as the dimension type for the parameter
    dim2 = Dimension("test2", "测试2", "TS2")
    param = Parameter(100, "dim_param", "维度参数", dim2)

    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()

    # Register index 1 as valid for dim, and index 3 as valid for dim2
    dim_registry[(dim,)][(1,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store 5 as value - should fail since 5 is not registered
    reg[param][(dim,)][(1,)] = 5
    with pytest.raises(ValidationError):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_invalid_dimension_value_logs_warning():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension

    reg = Register()
    # Define dim2 as the dimension type for the parameter
    dim2 = Dimension("test2", "测试2", "TS2")
    param = Parameter(100, "dim_param", "维度参数", dim2)

    dim = Dimension("test", "测试", "TST")
    dim_registry = DimensionAsKey()

    # Register index 1 as valid for dim, and index 3 as valid for dim2
    dim_registry[(dim,)][(1,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store 5 as value - should log warning but not raise
    reg[param][(dim,)][(1,)] = 5
    reg.validate(dim_registry, raise_errors=False)  # Should log warning only


def test_validate_with_valid_index_per_dimension():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from typing import Any

    reg = Register()
    # Define dim1 and dim2
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")

    # Create parameter with Any type for testing
    param = Parameter(100, "test_param", "测试参数", Any)

    # Create dimension registry and register indices 1, 2, 3 for each dimension
    dim_registry = DimensionAsKey()
    dim_registry[(dim1,)][(1,)] = None
    dim_registry[(dim1,)][(2,)] = None
    dim_registry[(dim1,)][(3,)] = None
    dim_registry[(dim2,)][(1,)] = None
    dim_registry[(dim2,)][(2,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store values with valid indices - should not raise exceptions
    reg[param][(dim1, dim2)][(1, 1)] = None
    reg[param][(dim1, dim2)][(3, 3)] = None
    reg.validate(dim_registry, raise_errors=True)  # Should not raise


def test_validate_with_invalid_index_per_dimension():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import DimensionError
    from typing import Any

    reg = Register()
    # Define dim1 and dim2
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")

    # Create parameter with Any type for testing
    param = Parameter(100, "test_param", "测试参数", Any)

    # Create dimension registry and register indices 1, 2, 3 for each dimension
    dim_registry = DimensionAsKey()
    dim_registry[(dim1,)][(1,)] = None
    dim_registry[(dim1,)][(2,)] = None
    dim_registry[(dim1,)][(3,)] = None
    dim_registry[(dim2,)][(1,)] = None
    dim_registry[(dim2,)][(2,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store value with invalid index (4) - should raise DimensionError
    reg[param][(dim1, dim2)][(1, 4)] = None
    with pytest.raises(DimensionError, match="index 4 does not match any index"):
        reg.validate(dim_registry, raise_errors=True)


def test_validate_with_mismatch_length_index_per_dimension():
    from register.register import Register, DimensionAsKey
    from register.parameter import Parameter
    from register.dimension import Dimension
    from register.exception import DimensionError
    from typing import Any

    reg = Register()
    # Define dim1 and dim2
    dim1 = Dimension("test1", "测试1", "T1")
    dim2 = Dimension("test2", "测试2", "T2")

    # Create parameter with Any type for testing
    param = Parameter(100, "test_param", "测试参数", Any)

    # Create dimension registry and register indices
    dim_registry = DimensionAsKey()
    dim_registry[(dim1,)][(1,)] = None
    dim_registry[(dim1,)][(2,)] = None
    dim_registry[(dim1,)][(3,)] = None
    dim_registry[(dim2,)][(1,)] = None
    dim_registry[(dim2,)][(2,)] = None
    dim_registry[(dim2,)][(3,)] = None

    # Store value with mismatched index length - (1,) for (dim1, dim2)
    reg[param][(dim1, dim2)][(1,)] = None
    # Note: Current implementation uses zip() which silently handles length mismatch
    # This test may need adjustment based on actual implementation behavior
    with pytest.raises(DimensionError):
        reg.validate(dim_registry, raise_errors=True)
