class RegisterError(Exception):
    """Base exception for all register errors."""

    pass


class ValidationError(RegisterError):
    """Raised when type/index validation fails."""

    pass


class DimensionError(RegisterError):
    """Raised for dimension-related issues."""

    pass
