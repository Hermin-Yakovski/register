class RegisterError(Exception):
    """Base exception for all register errors."""


class ValidationError(RegisterError):
    """Raised when type/index validation fails."""


class DimensionError(RegisterError):
    """Raised for dimension-related issues."""


__all__ = [
    "DimensionError",
    "RegisterError",
    "ValidationError",
]
