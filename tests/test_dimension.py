
def test_dimension_creation():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert dim.name == "test"
    assert dim.name_cn == "测试"
    assert dim.sign == "TST"

def test_dimension_str_returns_sign():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert str(dim) == "TST"

def test_dimension_repr_returns_name():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert repr(dim) == "test"

def test_dimension_hashable():
    from register.dimension import Dimension
    dim1 = Dimension("test", "测试", "TST")
    dim2 = Dimension("test", "测试", "TST")
    assert hash(dim1) == hash(dim2)

def test_dimension_equality():
    from register.dimension import Dimension
    dim1 = Dimension("test", "测试", "TST")
    dim2 = Dimension("test", "测试", "TST")
    dim3 = Dimension("other", "其他", "OTH")
    assert dim1 == dim2
    assert dim1 != dim3

def test_dimension_equality_based_on_sign():
    from register.dimension import Dimension
    dim1 = Dimension("name1", "测试1", "TST")
    dim2 = Dimension("name2", "测试2", "TST")
    assert dim1 == dim2  # Equal because signs match

def test_index_dimension_exists():
    from register.dimension import Index
    assert Index.name == "Index"
    assert Index.name_cn == "下标"
    assert Index.sign == "IX"

def test_metric_dimension_exists():
    from register.dimension import Metric
    assert Metric.name == "Metric"
    assert Metric.name_cn == "指标汇总"
    assert Metric.sign == "MTC"

def test_dimension_sign_property():
    from register.dimension import Dimension
    dim = Dimension("test", "测试", "TST")
    assert dim.sign == "TST"
