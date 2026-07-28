import pytest

from register import Dimension, NumKey, Register
from register.parameter import Id


@pytest.fixture
def empty_register():
    """Empty Register instance."""
    return Register()


@pytest.fixture
def sample_register():
    """Register populated with sample data."""
    reg = Register()
    region = Dimension("region", "地区", "REG")
    product = Dimension("product", "产品", "PRD")

    reg[Id][(region, product)][(1, 1)] = 1
    reg[Id][(region, product)][(1, 2)] = 2
    reg[Id][(region, product)][(2, 1)] = 3
    reg[Id][(region, product)][(2, 2)] = 4

    return reg


@pytest.fixture
def sample_dimension():
    """Sample Dimension for testing."""
    return Dimension("test", "测试", "TST")


@pytest.fixture
def sample_num_key():
    """Sample NumKey for testing."""
    return NumKey(100, "test_param", "测试参数", int)


@pytest.fixture
def price_key():
    """Price NumKey with float type."""
    return NumKey(4, "price", "价格", float)
