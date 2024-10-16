import os
import platform
from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
from typing import Union, NewType, NoReturn, Dict, Protocol, Any, Optional, Type, Generic, TypeVar, Literal

import uuid_utils as uuid

from happy.exceptions import UnsuitableBigIntError, UnsuitableBigDecimalError, InvalidUUIDError, \
    InvalidUUIDVersionError, InvalidULIDError, ScientificError
from happy.number import is_scientific_notation

PathLike = Union[str, os.PathLike, None]

Infinity = NewType("Infinity", float)

PositiveInfinity = Infinity(float("inf"))
NegativeInfinity = Infinity(float("-inf"))

JsonType = NewType('JsonType', dict)
XmlType = NewType('XmlType', dict)
YamlType = NewType('YamlType', dict)
TomlType = NewType('TomlType', dict)

EnvPath = Union[PathLike, Dict, JsonType, NoReturn]

T = TypeVar('T')


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
            raise TypeError(f"{T} is not a class.")
        return super().__new__(cls)

    def __class_getitem__(cls, item):
        return Type[item]


class NaN(float):
    def __new__(cls):
        return super().__new__(cls, float('nan'))


class PositiveInt(int):
    def __new__(cls, value: int):
        if value <= 0:
            raise ValueError(f"{value} is not a positive integer.")
        return super().__new__(cls, value)


class NegativeInt(int):
    def __new__(cls, value: int):
        if value >= 0:
            raise ValueError(f"{value} is not a negative integer.")
        return super().__new__(cls, value)


class UnsignedInt(int):
    def __new__(cls, value: int):
        if value < 0:
            raise ValueError(f"{value} is not a positive integer.")
        return super().__new__(cls, value)


class PositiveFloat(float):
    def __new__(cls, value: float):
        if value <= 0:
            raise ValueError(f"{value} is not a positive float.")
        return super().__new__(cls, value)


class NegativeFloat(float):
    def __new__(cls, value: float):
        if value >= 0:
            raise ValueError(f"{value} is not a negative float.")
        return super().__new__(cls, value)


class UnsignedFloat(float):
    def __new__(cls, value: float):
        if value < 0:
            raise ValueError(f"{value} is not a positive float.")
        return super().__new__(cls, value)


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
            raise ScientificError(f"{value} is not a valid scientific notation.")
        return super().__new__(cls, value)


class BigDecimal(Decimal):
    _FLOAT_MAX = 1.7976931348623157e+308
    _FLOAT_MIN = 2.2250738585072014e-308

    def __new__(cls, value: Union[float, Decimal, Infinity, NaN],
                strict: bool = False,
                context: Literal["Positive", "Negative", "Unsigned"] = "Positive") -> Union['BigDecimal', NoReturn]:
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
            if abs_float_value == cls._FLOAT_MAX or abs_float_value == cls._FLOAT_MIN:
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
        if uuid_obj.version != cls.VERSION:
            raise InvalidUUIDVersionError(f"UUID {uuid_obj} is not of version {cls.VERSION}.")

    @classmethod
    def _create_uuid(cls, value: Union[str, int]) -> ClassType['UUIDType']:
        uuid_v = getattr(uuid, "uuid{v}".format(v=cls.VERSION))
        return uuid_v(value)


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


@dataclass
class AvifencConfig(Protocol):
    min: str
    max: str


class LoggingProtocol(Protocol):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        ...


class NullLogging(LoggingProtocol):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        ...


class AuthProviderProtocol(Protocol):
    def get_authorization_url(self) -> str:
        ...

    def retrieve_token(self, authorization_response: str) -> Dict[str, Any]:
        ...

    def fetch_user_info(self) -> Dict[str, Any]:
        ...


# Protocol Definitions
class ThirdPartyServiceProviderProtocol(Protocol):
    async def connect(self) -> None:
        ...

    async def close_connection(self) -> None:
        ...

    @classmethod
    def register(cls, config: Dict[str, str]) -> None:
        ...


class BaaSProviderProtocol(ThirdPartyServiceProviderProtocol):
    async def create_user(self, user_data: Dict[str, Any]) -> None:
        ...

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        ...

    async def insert_data(self, data: Dict[str, Any]) -> None:
        ...

    async def update_data(self, user_id: str, data: Dict[str, Any]) -> None:
        ...

    async def delete_data(self, user_id: str) -> None:
        ...

    async def fetch_data(self, query: str) -> Dict[str, Any]:
        ...
