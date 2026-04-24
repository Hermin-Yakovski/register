import pytest
from register import Register, Parameter, Dimension
from register.dimension import Index, Metric
from register.parameter import Id, Code, Name


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

    reg[Id][(region, product)][("Beijing", "Widget")] = 1
    reg[Id][(region, product)][("Beijing", "Gadget")] = 2
    reg[Id][(region, product)][("Shanghai", "Widget")] = 3
    reg[Id][(region, product)][("Shanghai", "Gadget")] = 4

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
    """Price Parameter with float type."""
    return Parameter(4, "price", "价格", float)


@pytest.fixture
def region_dimension():
    """Region Dimension with pre-filled indices."""
    dim = Dimension("region", "地区", "REG")
    reg = Register()
    # Register some indices
    reg._data[dim][(Index,)][("Beijing",)] = None
    reg._data[dim][(Index,)][("Shanghai",)] = None
    return dim, reg
