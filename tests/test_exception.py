import pytest

def test_register_error_exists():
    from register.exception import RegisterError
    assert issubclass(RegisterError, Exception)

def test_validation_error_exists():
    from register.exception import ValidationError, RegisterError
    assert issubclass(ValidationError, RegisterError)

def test_dimension_error_exists():
    from register.exception import DimensionError, RegisterError
    assert issubclass(DimensionError, RegisterError)

def test_can_raise_register_error():
    from register.exception import RegisterError
    with pytest.raises(RegisterError):
        raise RegisterError("test error")

def test_can_raise_validation_error():
    from register.exception import ValidationError
    with pytest.raises(ValidationError):
        raise ValidationError("validation failed")

def test_can_raise_dimension_error():
    from register.exception import DimensionError
    with pytest.raises(DimensionError):
        raise DimensionError("dimension error")
