class EnumValidationError(Exception):
    """Custom error for invalid enum values."""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidULIDError(Exception):
    """Exception raised for invalid ULIDs."""
    pass


class PrivateAccessError(Exception):
    """Exception raised when trying to access a private method or variable."""
    pass


class ProtectedAccessError(Exception):
    """Exception raised when trying to access a protected method or variable outside of inheritance."""
    pass


class BreakerThresholdError(Exception):
    """Exception raised when the threshold is reached in a breaker decorator."""
    pass


class LoggingError(Exception):
    """Base class for logging exceptions."""
    pass


class AccessControlError(Exception):
    """Base exception for all access control related errors."""
    pass


class LoaderError(Exception):
    """Base exception for loader-related errors"""
    pass


class EnhancedDataclassError(Exception):
    """Base exception for enhanced dataclass errors"""
    pass


class RecycleBinError(Exception):
    """Base exception for RecycleBin operations."""
    pass


class UnificationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


# Subclasses of Exception subclasses (TypeError, ValueError, etc.)
class EnumTypeError(TypeError):
    """Custom error for type mismatches in enum."""

    def __init__(self, expected_type: str, actual_type: str):
        super().__init__(f"Expected type: {expected_type}, but got: {actual_type}")


class UnsuitableValueError(ValueError):
    """Base class for exceptions when a value is unsuitable."""
    pass


class InvalidUUIDError(ValueError):
    """Exception raised for invalid UUIDs."""
    pass


class InvalidUUIDVersionError(ValueError):
    """Exception raised when a UUID does not match the expected version."""
    pass


# Subclasses of custom exceptions
class ConfigurationError(LoggingError):
    """Raised when there's a configuration error."""
    pass


class InvalidLogLevelError(LoggingError):
    """Raised when an invalid log level is specified."""
    pass


class InvalidInheritanceError(AccessControlError):
    """Raised when attempting to inherit from a private class."""
    pass


class PluginNotFoundError(LoaderError):
    """Raised when a plugin cannot be found"""
    pass


class OperatorNotSupportedError(EnhancedDataclassError):
    """Raised when an operator is not supported for the given types"""
    pass


class NoOperatorGroupError(EnhancedDataclassError):
    """Raised when no operator group is specified"""
    pass


class ItemNotFoundError(RecycleBinError):
    """Raised when an item is not found in the recycle bin."""

    def __init__(self, message: str):
        super().__init__(message)


class StorageFullError(RecycleBinError):
    """Raised when recycle bin storage limit is exceeded."""
    pass


class RestoreError(RecycleBinError):
    """Raised when item restoration fails."""
    pass


class UnsuitableBigIntError(UnsuitableValueError):
    """Raised when an integer value is unsuitable."""
    pass


class UnsuitableBigDecimalError(UnsuitableValueError):
    """Raised when a decimal value is unsuitable."""
    pass
