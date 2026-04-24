def test_import_register():
    from register import Register
    assert Register is not None

def test_import_parameter():
    from register import Parameter
    assert Parameter is not None

def test_import_dimension():
    from register import Dimension
    assert Dimension is not None

def test_import_index():
    from register import Index
    assert Index is not None

def test_import_metric():
    from register import Metric
    assert Metric is not None

def test_import_common_parameters():
    from register import Id, Code, Name
    assert Id is not None
    assert Code is not None
    assert Name is not None

def test_import_exceptions():
    from register import RegisterError, ValidationError, DimensionError
    assert RegisterError is not None
    assert ValidationError is not None
    assert DimensionError is not None

def test_import_from_exception_module():
    from register.exception import RegisterError, ValidationError, DimensionError
    assert RegisterError is not None
    assert ValidationError is not None
    assert DimensionError is not None
