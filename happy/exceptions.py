class EnumTypeError(TypeError):
    """Custom error for type mismatches in enum."""

    def __init__(self, expected_type: str, actual_type: str):
        super().__init__(f"Expected type: {expected_type}, but got: {actual_type}")


class MarkException(Exception):
    """Base exception for Mark decorators."""
    pass


class TrivialOperationError(MarkException):
    """Exception raised for errors in trivial operations."""


class ComplexOperationError(MarkException):
    """Exception raised for errors in complex operations."""


class CriticalOperationError(MarkException):
    """Exception raised for critical operation failures."""


class BrokenOperationError(MarkException):
    """Exception raised when an operation is broken."""


class LongTimeRunningError(MarkException):
    """Exception raised when a long-time running operation fails."""


class SlowOperationError(MarkException):
    """Exception raised for slow operation failures."""


class DebuggingOperationError(MarkException):
    """Exception raised during debugging operations."""


class EnumValidationError(Exception):
    """Custom error for invalid enum values."""

    def __init__(self, message: str):
        super().__init__(message)


# Custom Exceptions
class ThirdPartyServiceError(Exception):
    """Base exception for third-party service errors."""
    pass


class ConnectionError(ThirdPartyServiceError):
    """Exception raised for connection-related errors."""
    pass


class OperationError(ThirdPartyServiceError):
    """Exception raised for general operation errors."""
    pass


class ServiceNotFoundError(ThirdPartyServiceError):
    """Exception raised when a service is not found."""
    pass


class UnsuitableValueError(ValueError):
    """Base class for exceptions when a value is unsuitable."""
    pass


class UnsuitableBigIntError(UnsuitableValueError):
    """Raised when an integer value is unsuitable."""
    pass


class UnsuitableBigDecimalError(UnsuitableValueError):
    """Raised when a decimal value is unsuitable."""
    pass


class InvalidUUIDError(ValueError):
    """Exception raised for invalid UUIDs."""
    pass


class InvalidUUIDVersionError(ValueError):
    """Exception raised when a UUID does not match the expected version."""
    pass


class InvalidULIDError(Exception):
    """Exception raised for invalid ULIDs."""
    pass


class EnvError(Exception):
    """Exception raised for environment errors."""
    pass


class ScientificError(ValueError):
    """Exception raised when an invalid scientific notation is provided."""
    pass


class MissingOptionalDependency(ImportError):
    """Exception raised when an optional dependency is missing or not installed."""
    pass

class PoolException(Exception):
    """Base exception class for Pool-related errors."""
    pass


class PoolTimeoutException(PoolException):
    """Raised when acquiring a resource times out."""
    pass


class PoolShutdownException(PoolException):
    """Raised when operations are attempted on a shutdown pool."""
    pass


class PoolClosedException(PoolException):
    """Raised when operations are attempted on a closed pool."""
    pass


class PoolEmptyException(PoolException):
    """Raised when the pool is empty and no resources are available."""
    pass


class EventListenerError(Exception):
    """Base exception for EventListener errors."""
    pass


class HandlerAlreadyRegistered(EventListenerError):
    """Raised when attempting to register a handler that's already registered."""
    pass


class HandlerNotFound(EventListenerError):
    """Raised when attempting to deregister a handler that's not registered."""
    pass


class EventDispatchError(EventListenerError):
    """Raised when an error occurs during event dispatch."""

    def __init__(self, errors: list):
        self.errors = errors
        message = f"Errors occurred during event dispatch: {errors}"
        super().__init__(message)

class GrepException(Exception):
    pass


class FileTypeNotSupported(GrepException):
    pass

class TransactionError(Exception):
    """Base class for transaction-related exceptions."""
    pass


class TransactionCommitError(TransactionError):
    """Raised when a transaction fails to commit."""
    pass


class TransactionRollbackError(TransactionError):
    """Raised when a transaction fails to roll back."""
    pass

class PipelineException(Exception):
    """Base class for all pipeline-related exceptions."""
    pass

class PipelineExecutionException(PipelineException):
    """Raised when pipeline execution fails."""
    pass

class InvalidPipelineStepException(PipelineException):
    """Raised when a pipeline step is invalid."""
    pass
