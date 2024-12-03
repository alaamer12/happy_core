"""
This module defines a set of classes and utilities for working with various types of versioning, numerical types, and identifiers. The primary focus is on enforcing validation rules for various data types, including version strings, large numbers (BigInt and BigDecimal), UUIDs, ULIDs, and scientific numbers. It includes functionality for enforcing constraints on value ranges and formats, providing robust error handling for invalid inputs.

Key Features:
- Version validation and parsing, supporting formats like SemVer, CalVer, Date Versioning, and Major/Minor versions.
- Custom types for numeric validation, including `ValidatedInt`, `ValidatedFloat`, `BigInt`, and `BigDecimal`, with support for context-based validation (positive, negative, unsigned).
- UUID and ULID handling with strict format checks for both string and integer-based identifiers, as well as support for versioned UUIDs.
- Scientific number validation and parsing with support for scientific notation.
- Type hints and generic utilities for better typing and code clarity.
- Error handling via custom exceptions for invalid data types and values.

Classes:
- `VersionValidatorMixin`: A mixin that provides version validation functionality for versioning classes.
- `Version`: A base class for version objects, supporting parsing, comparison, and validation of version strings.
- `SemVersion`, `DateVersion`, `CalVersion`, `MajorMinorVersion`: Specific version classes for different versioning schemes.
- `ValidatedNumber`, `ValidatedInt`, `ValidatedFloat`: Base and derived classes for validated numeric types.
- `BigInt`, `BigDecimal`: Classes for handling large integer and decimal values, with strict validation rules based on system architecture and floating-point range.
- `UUIDType`, `StrUUIDType`, `IntUUIDType`: Classes for working with UUIDs, supporting both string and integer-based types with versioned variants.
- `ScientificNumber`: A class for handling scientific notation values.
- `ULIDType`, `StrULIDType`, `IntULIDType`: Classes for working with ULIDs.

Exceptions:
- `UnsuitableBigIntError`: Raised when a value is not valid for a `BigInt`.
- `UnsuitableBigDecimalError`: Raised when a value is not valid for a `BigDecimal`.
- `InvalidUUIDError`: Raised when a UUID is not in the correct format.
- `InvalidUUIDVersionError`: Raised when a UUID version is incorrect.
- `InvalidULIDError`: Raised when a ULID is invalid.
- `ScientificNumberError`: Raised for invalid scientific notation inputs.

Utility Functions:
- `is_scientific_notation`: A helper function to check if a string represents a valid scientific notation.
"""

import platform
import re
from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, NewType, NoReturn, Type, Generic, TypeVar, Literal, Optional, ClassVar

import uuid_utils as uuid

from .exceptions import UnsuitableBigIntError, UnsuitableBigDecimalError, InvalidUUIDError, \
    InvalidUUIDVersionError, \
    InvalidULIDError
from .re import (CALVER_STYLE, SEMVER_STYLE,
                 DATE_VERSION_STYLE, MAJOR_MINOR_VERSION_STYLE)

T = TypeVar('T')

Infinity = NewType("Infinity", float)

PositiveInfinity = Infinity(float("inf"))
NegativeInfinity = Infinity(float("-inf"))

JsonType = NewType('JsonType', dict)
XmlType = NewType('XmlType', dict)
YamlType = NewType('YamlType', dict)
TomlType = NewType('TomlType', dict)


class VersionValidatorMixin:

    @classmethod
    def __new__(cls, value: str, *args, **kwargs):
        if isinstance(value, str):
            # noinspection PyUnresolvedReferences
            pattern = cls.PATTERN  # Each subclass will define its own pattern
            if not re.match(pattern, value):
                raise ValueError(f"{value} is not a valid {cls.__name__.lower()}.")
        return super().__new__(cls)


@dataclass
class Version:
    major: str
    minor: str
    patch: Optional[str] = None
    tag: Optional[str] = None

    PATTERNS: ClassVar[set] = {
        SEMVER_STYLE,
        DATE_VERSION_STYLE,
        MAJOR_MINOR_VERSION_STYLE,
        CALVER_STYLE
    }

    def __new__(cls, value: str, *args, **kwargs):
        if isinstance(value, str):
            for pattern in cls.PATTERNS:
                if re.match(pattern, value):
                    return super().__new__(cls)
            raise ValueError(f"{value} is not a valid version.")
        return super().__new__(cls)

    def __str__(self) -> str:
        version_parts = [self.major, self.minor]
        if self.patch is not None:
            version_parts.append(self.patch)
        base_version = ".".join(version_parts)

        if self.tag:
            return f"{base_version}-{self.tag}"
        return base_version

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.tag))

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(major='{self.major}', minor='{self.minor}', patch='{self.patch}', tag='{self.tag}')"

    @property
    def version(self) -> str:
        return str(self)


class SemVersion(VersionValidatorMixin, Version):
    PATTERN = SEMVER_STYLE


class DateVersion(VersionValidatorMixin, Version):
    PATTERN = DATE_VERSION_STYLE


class CalVersion(VersionValidatorMixin, Version):
    PATTERN = CALVER_STYLE


class MajorMinorVersion(VersionValidatorMixin, Version):
    PATTERN = MAJOR_MINOR_VERSION_STYLE

    def __init__(self, major: str, minor: str, patch: Optional[str] = None, tag: Optional[str] = None):
        if patch is not None:
            raise ValueError("MajorMinorVersion cannot have a patch number")
        super().__init__(major=major, minor=minor, patch=None, tag=tag)


class ClassType(Generic[T]):
    """
    A class that represents a class type for type hinting.

    Usage:
        def func(cls: ClassType[Enum]) → None:
            ...
    """

    def __new__(cls, *args, **kwargs) -> Union[T, NoReturn]:
        # Check if the `T` is a class.
        if not isinstance(T, type):
            raise TypeError(f"{T} is not a class type.")
        return super().__new__(cls)

    def __class_getitem__(cls, item):
        return Type[item]


class NaN(float):
    def __new__(cls, value: float):
        if not isinstance(value, float):
            raise TypeError(f"NaN can only be created from a float.")
        return super().__new__(cls, float('nan'))


class ValidatedNumber(ABC):
    @classmethod
    def validate(cls, value: Union[int, float]) -> bool:
        """Validate the input value. Return True if valid, False otherwise."""
        pass

    @classmethod
    def get_error_message(cls, value: Union[int, float]) -> str:
        """Get the error message for invalid values."""
        return f"{value} is not a valid {cls.__name__}."


class ValidatedInt(int, ValidatedNumber):
    def __new__(cls: Type[T], value: int) -> T:
        if not cls.validate(value):
            raise ValueError(cls.get_error_message(value))
        return super().__new__(cls, value)


class ValidatedFloat(float, ValidatedNumber):
    def __new__(cls: Type[T], value: float) -> T:
        if not cls.validate(value):
            raise ValueError(cls.get_error_message(value))
        return super().__new__(cls, value)


class PositiveInt(ValidatedInt):
    @classmethod
    def validate(cls, value: int) -> bool:
        return value > 0


class NegativeInt(ValidatedInt):
    @classmethod
    def validate(cls, value: int) -> bool:
        return value < 0


class UnsignedInt(ValidatedInt):
    @classmethod
    def validate(cls, value: int) -> bool:
        return value >= 0


class PositiveFloat(ValidatedFloat):
    @classmethod
    def validate(cls, value: float) -> bool:
        return value > 0


class NegativeFloat(ValidatedFloat):
    @classmethod
    def validate(cls, value: float) -> bool:
        return value < 0


class UnsignedFloat(ValidatedFloat):
    @classmethod
    def validate(cls, value: float) -> bool:
        return value >= 0


class BigInt(int):
    arch = platform.architecture()[0]
    _INT_MAX = 2 ** 63 - 1 if arch == '64bit' else 2 ** 31 - 1
    _INT_MIN = -2 ** 63 if arch == '64bit' else -2 ** 31

    def __new__(cls, value: int,
                strict: bool = False,
                context: Literal["Positive", "Negative", "Unsigned"] = "Positive") -> Union['BigInt', NoReturn]:

        # Handle wrong value
        cls.__handle_wrong_value(value)

        # Strict mode: ensure the value is larger than regular ints or exceeds BigInt limits
        if strict:
            # Check if the value is positive BigInt not normal int
            if value < cls._INT_MAX and (context == "Positive" or context == "Unsigned"):
                raise UnsuitableBigIntError(
                    f"The value {value} is not a positive BigInt enough, if you intend to use; set 'strict' to False.")
            # Check if the value is positive BigInt not normal int
            if value > cls._INT_MIN and (context == "Negative" or context == "Unsigned"):
                raise UnsuitableBigIntError(
                    f"The value {value} is not a negative BigInt enough, if you intend to use; set 'strict' to False.")

        # Check if positive value
        if context == "Positive" and value <= 0:
            raise UnsuitableBigIntError(f"BigInt expected a positive value, got: {value}")
        # Check if negative value
        if context == "Negative" and value >= 0:
            raise UnsuitableBigIntError(f"BigInt expected a negative value, got: {value}")

        return super(BigInt, cls).__new__(cls, value)

    @staticmethod
    def __handle_wrong_value(value: int):
        # Try to convert the value to an integer and raise an error if it's a float
        if isinstance(value, float):
            raise UnsuitableBigIntError(f"Float values are not allowed for BigInt: {value}")

        try:
            value = int(value)
        except (ValueError, TypeError):
            raise UnsuitableBigIntError(f"Value '{value}' cannot be converted to an integer.")


class ScientificNumberError(ValueError, TypeError):
    def __init__(self, message: str):
        super().__init__(message)


def is_scientific_notation(num_str):
    """Check if the given string is in scientific notation."""
    pattern = r'^[+-]?(\d+(\.\d+)?|\.\d+)([eE][+-]?\d+)?$'
    return bool(re.match(pattern, num_str))


class ScientificNumber(str):
    def __new__(cls, value: str):
        """
        Scientific Number consists of:
            Coefficient (or Mantissa): This is the significant figure, which can be a whole number or a decimal. It represents the main digits of the number.
            Exponent: This is denoted by the letter e (or E), followed by a sign (+ or -) and an integer. The exponent indicates how many places the decimal point should be moved to convert the scientific notation back to the standard form.
            Decimal: This part is included in the coefficient and indicates the precise value of the number based on where the decimal point is placed.
        :param value:
        """
        if not is_scientific_notation(value):
            raise ScientificNumberError(f"{value} is not a valid scientific notation.")
        return super().__new__(cls, value)


class BigDecimal(Decimal):
    _FLOAT_MAX: ClassVar[float] = 1.7976931348623157e+308
    _FLOAT_MIN: ClassVar[float] = 2.2250738585072014e-308

    def __new__(cls, value: Union[float, Decimal, Infinity, NaN],
                strict: bool = False,
                context: Literal["Positive", "Negative", "Unsigned"] = "Positive", stop_warnings: bool = False) -> \
            Union['BigDecimal', NoReturn]:
        try:
            decimal_value = super(BigDecimal, cls).__new__(cls, value)
        except (ValueError, TypeError):
            raise UnsuitableBigDecimalError(f"Value '{value}' cannot be converted to Decimal.")

        try:
            float_value = float(decimal_value)
        except OverflowError as e:
            raise UnsuitableBigDecimalError(f"BigDecimal value '{decimal_value}' exceeds float range.") from e

        abs_float_value = abs(float_value)

        if strict:
            # Check if the number didn't exceed the float limits.
            if abs_float_value > cls._FLOAT_MAX:
                raise UnsuitableBigDecimalError(f"BigDecimal exceeds float maximum: {decimal_value}")
            # Check if the number is below the float minimum.
            if abs_float_value < cls._FLOAT_MIN:
                raise UnsuitableBigDecimalError(f"BigDecimal is below float minimum: {decimal_value}")
            if abs_float_value == cls._FLOAT_MAX or abs_float_value == cls._FLOAT_MIN and not stop_warnings:
                import warnings
                warnings.warn(f"BigDecimal at the limit: {decimal_value}", stacklevel=2)

        if context == "Positive" and float_value < 0:
            raise UnsuitableBigDecimalError(f"BigDecimal expected a positive value, got: {decimal_value}")
        if context == "Negative" and float_value > 0:
            raise UnsuitableBigDecimalError(f"BigDecimal expected a negative value, got: {decimal_value}")

        return decimal_value


class UUIDType(ABC):
    def __new__(cls, value) -> Union['UUIDType', NoReturn]:
        value = cls._convert_value(value)
        cls._validate_length(value)
        instance = super().__new__(cls, value)
        instance.uuid = cls._create_uuid(value)
        cls._validate_version(instance.uuid)
        return instance

    @classmethod
    def _convert_value(cls, value: Union[str, int]) -> Union[str, int, NoReturn]:
        """Convert the value to the appropriate type (str or int)."""
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def _validate_length(cls, value: Union[str, int]) -> Union[str, int]:
        """Validate the length of the input value."""
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def _create_uuid(cls, value: Union[str, int]) -> ClassType['UUIDType']:
        """Create a UUID instance based on the input value."""
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def _validate_version(cls, uuid_obj: ClassType['UUIDType']):
        """Optionally validate the UUID version."""
        pass


# String-based UUID with validation
class StrUUIDType(UUIDType, str):
    @classmethod
    def _convert_value(cls, value):
        try:
            return str(value)
        except (ValueError, TypeError):
            raise InvalidUUIDError(f"Invalid UUID string: {value}")

    @classmethod
    def _validate_length(cls, value):
        if len(value) != 36:
            raise InvalidUUIDError(f"Invalid UUID string: {value}")


# Integer-based UUID with validation
class IntUUIDType(UUIDType, int):
    @classmethod
    def _convert_value(cls, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise InvalidUUIDError(f"Invalid UUID integer: {value}")

    @classmethod
    def _validate_length(cls, value):
        if not (0 <= value <= 2 ** 128 - 1):
            raise InvalidUUIDError(f"Invalid UUID integer: {value}")


# Versioned UUID classes
class UUIDVersionMixin(UUIDType):
    VERSION = None

    @classmethod
    def _validate_version(cls, uuid_obj):
        # noinspection PyUnresolvedReferences
        if uuid_obj.version != cls.VERSION:
            raise InvalidUUIDVersionError(f"UUID {uuid_obj} is not of version {cls.VERSION}.")

    @classmethod
    def _create_uuid(cls, value: Union[str, int]) -> ClassType['UUIDType']:
        uuid_v = getattr(uuid, "uuid{v}".format(v=cls.VERSION))
        return uuid_v(value)


class UUIDV1(UUIDVersionMixin):
    VERSION = 1


class UUIDV2(UUIDVersionMixin):
    VERSION = 2


class UUIDV3(UUIDVersionMixin):
    VERSION = 3


class UUIDV4(UUIDVersionMixin):
    VERSION = 4


class UUIDV5(UUIDVersionMixin):
    VERSION = 5


class StrUUIDV1(StrUUIDType, UUIDVersionMixin):
    VERSION = 1


class StrUUIDV2(StrUUIDType, UUIDVersionMixin):
    VERSION = 2


class StrUUIDV3(StrUUIDType, UUIDVersionMixin):
    VERSION = 3


class StrUUIDV4(StrUUIDType, UUIDVersionMixin):
    VERSION = 4


class StrUUIDV5(StrUUIDType, UUIDVersionMixin):
    VERSION = 5


# Similarly for integer-based UUIDs
class IntUUIDV1(IntUUIDType, UUIDVersionMixin):
    VERSION = 1


class IntUUIDV2(IntUUIDType, UUIDVersionMixin):
    VERSION = 2


class IntUUIDV3(IntUUIDType, UUIDVersionMixin):
    VERSION = 3


class IntUUIDV4(IntUUIDType, UUIDVersionMixin):
    VERSION = 4


class IntUUIDV5(IntUUIDType, UUIDVersionMixin):
    VERSION = 5


class ULIDType(ABC):
    # TODO: Add validation
    pass


class StrULIDType(ULIDType):
    def __new__(cls, value: str):
        try:
            str(value)
        except (ValueError, TypeError):
            raise InvalidULIDError(f"Invalid ULID: {value}")

        if len(str(value)) != 26:
            raise InvalidULIDError(f"Invalid ULID: {value}")
        return super().__new__(cls, value)


class IntULIDType(ULIDType):
    def __new__(cls, value: int):
        try:
            int(value)
        except (ValueError, TypeError):
            raise InvalidULIDError(f"Invalid ULID: {value}")

        if len(str(value)) != 37:
            raise InvalidULIDError(f"Invalid ULID: {value}")

        return super().__new__(cls, value)


class JsonMixin:
    import json

    @classmethod
    def to_json(cls, value):
        return cls.json.dumps(value)

    @classmethod
    def from_json(cls, value):
        return cls.json.loads(value)


class YamlMixin:
    try:
        import yaml
    except ImportError:
        yaml = None
        import warnings
        warnings.warn("YAML support is not available. Please install the 'pyyaml' package.", stacklevel=2)
    else:
        @classmethod
        def to_yaml(cls, value):
            return cls.yaml.dump(value)

        @classmethod
        def from_yaml(cls, value):
            return cls.yaml.load(value)


class TomlMixin:
    import tomlkit

    @classmethod
    def to_toml(cls, value):
        return cls.tomlkit.dumps(value)

    @classmethod
    def from_toml(cls, value):
        return cls.tomlkit.loads(value)
