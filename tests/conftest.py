import pytest
from register import Register, Parameter, Dimension
from register.dimension import Index
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
def sample_parameter():
    """Sample Parameter for testing."""
    return Parameter(100, "test_param", "测试参数", int)


@pytest.fixture
def price_parameter():
    """Price Parameter with a float type."""
    return Parameter(4, "price", "价格", float)
