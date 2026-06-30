import pytest
from register import Register, Dimension
from register.key import _BaseKey


class _TestKey(_BaseKey):
    """Minimal key for testing — replaces ParameterKey in conftest."""
    pass


@pytest.fixture
def empty_register():
    """Empty Register instance."""
    return Register()


@pytest.fixture
def sample_register():
    """Register populated with sample data."""
    reg = Register()

    # NOTE: sample_register fixtures will be rebuilt when ParameterKey is
    # re-implemented. This placeholder keeps the fixture importable.
    return reg


@pytest.fixture
def sample_dimension():
    """Sample Dimension for testing."""
    return Dimension("test", "测试", "TST")


@pytest.fixture
def sample_parameter():
    """Sample key for testing."""
    return _TestKey(100, "test_param", "测试参数")


@pytest.fixture
def price_parameter():
    """Price key with a float-like label."""
    return _TestKey(4, "price", "价格")
