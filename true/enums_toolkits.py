"""
This module provides a robust framework for defining specialized Enum classes in Python, extending
the native Enum capabilities. The included classes and decorators enable advanced metadata handling,
serialization, and validation across different data types, such as integers, floats, bytes, dictionaries,
and complex numbers.

Keys:
    - `metadata`: A decorator to enhance Enums with metadata configuration for detailed descriptions and
    custom attributes.
    - `SerializedEnumMeta`: A metaclass for Enums that allows dictionary and JSON-based initialization
    and serialization.
    - `DynamicEnum` and `DynamicEnumMember`: A flexible class for dynamic enum generation, supporting
    custom member addition and removal.
    - Specialized Enum classes (`IterableEnum`, `IteratorEnum`, `GeneratorEnum`, `RangingEnum`,
      `ByteEnum`, `FloatEnum`, `ComplexNumberEnum`, `DictEnum`, `SetEnum`): Each class ensures values
      conform to specific types or data structures, raising appropriate errors for invalid assignments.

These enhancements allow for increased type safety, custom error handling, and adaptable usage
across various applications, particularly useful in scenarios requiring dynamic enum definitions
or type-enforced enumerations.
"""

import json
from enum import EnumMeta, unique, ReprEnum
from typing import Generic, Iterator, Generator, Callable

from true.exceptions import EnumTypeError, EnumValidationError
from true.toolkits import is_iterable, is_iterator, is_generator
from true.types import JsonType
from enum import Enum
from typing import Type, Union, NoReturn, Dict, Any, Optional, ClassVar, TypeVar
from dataclasses import dataclass
from true.exceptions import EnumMetadataError

T = TypeVar('T')

E = TypeVar('E', bound=Enum)


@dataclass
class MetadataConfig:
    """Configuration for enum metadata."""
    include_bit_length: bool = True
    include_type_info: bool = True
    custom_attributes: Dict[str, Any] = None
    default_value: Any = "N/A"


def metadata(config: Optional[MetadataConfig] = None) -> Callable[[Type[E]], Type[E]]:
    """A decorator that adds metadata capabilities to Enum classes.

    Args:
        config: Configuration object for metadata handling.
            If not provided, default configuration will be used.

    Returns:
        A decorator function that enhances the Enum class with metadata capabilities.

    Raises:
        EnumMetadataError: If there are issues with metadata configuration.
    """
    config = config or MetadataConfig()

    def decorator(cls: Type[E]) -> Type[E]:
        def get_description(self) -> str:
            """Generate a detailed description of the enum member."""
            attributes = {
                "Value": self.value,
                "Default": config.default_value
            }

            if config.include_type_info:
                attributes["Type"] = type(self.value).__name__

            if config.include_bit_length:
                attributes["Size (bits)"] = getattr(self.value, 'bit_length', lambda: "N/A")()

            attributes.update(config.custom_attributes or {})

            description = [f"{self.__class__.__name__} Member: {self.name}"]
            description.extend(f"{key}: {value}" for key, value in attributes.items())
            return "\n".join(description)

        # noinspection PyIncorrectDocstring,PyUnusedLocal
        def set_description(self, *args: str, **kwargs: Any) -> Union[str, NoReturn]:
            """
            Set a custom description for the enum member.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                Union[str, NoReturn]: Custom description or raises EnumMetadataError.
            """
            if not args and not kwargs:
                raise EnumMetadataError("Expected at least one argument")

            if len(args) == 1:
                if not isinstance(args[0], str):
                    raise EnumMetadataError("Single argument must be string")
                return args[0]

            if kwargs:
                return "\n".join(f"{key}: {value}" for key, value in kwargs.items())

            if len(args) != 4:
                raise EnumMetadataError(
                    "Expected either 1 string argument or 4 arguments for full description"
                )

            attributes = dict(zip(["Type", "Value", "Size (bits)", "Default"], args))
            return "\n".join(f"{key}: {value}" for key, value in attributes.items())

        # noinspection PyUnusedLocal
        def delete_description(self) -> None:
            """Reset the description to default."""
            pass

        # noinspection PyDecorator,PyUnresolvedReferences,PyIncorrectDocstring,PyShadowingNames
        @classmethod
        def extend_description(cls, member: Union[str, T], additional_info: Dict[str, Any]) -> str:
            """
            Extend the description of an enum member with additional information.

            Args:
                member: Enum member or its name.
                additional_info: Dictionary of additional information.

            Returns:
                str: Extended description.
            """
            if isinstance(member, str):
                member = cls.get(member)

            if not member:
                raise EnumMetadataError(f"Member '{member}' not found in {cls.__name__}")

            base_description = member.describe
            additional_description = "\n".join(f"{key}: {value}" for key, value in additional_info.items())
            return f"{base_description}\n{'=' * 20}\n{additional_description}"

        # Add class-level metadata
        # noinspection PyTypeHints
        cls._metadata_config: ClassVar[MetadataConfig] = config

        # Add properties and methods
        cls.describe = property(fget=get_description, fset=set_description, fdel=delete_description)
        cls.extend_description = extend_description

        return cls

    return decorator


class SerializedEnumMeta(EnumMeta):
    def __getitem__(cls, item: Any) -> Enum:
        """
        Allow enum items to be retrieved using bracket notation (Enum[item]).
        Provides a custom KeyError message.
        """
        try:
            return cls.__members__[item]
        except KeyError:
            raise KeyError(f"'{item}' is not a valid member of {cls.__name__}")

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        """
        Custom Meta class for advanced Enum features.
        """
        # noinspection PyTypeChecker
        cls = super().__new__(mcs, name, bases, namespace)

        return cls

    @classmethod
    def from_dict(cls, name: str, members: Dict[str, Any]) -> Type[Enum]:
        """Generate an Enum class from a dictionary of member names and values."""
        return Enum(name, members)

    @classmethod
    def from_json(cls, name: str, json_data: JsonType) -> Type[Enum]:
        """Generate an Enum class from a JSON string or dictionary."""
        if isinstance(json_data, str):
            try:
                members = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError("Invalid JSON data provided.") from e
        elif isinstance(json_data, dict):
            members = json_data
        else:
            raise TypeError("from_json expects a JSON string or a dictionary.")

        return cls.from_dict(name, members)

    def to_dict(cls):
        """

        :return: Dict[str, Any]
        """
        return {member.name: member.value for member in cls}

    def to_json(cls):
        """

        :return: JsonType
        """
        d = cls.to_dict()
        return json.dumps(d)


class DynamicEnum:
    """A dynamic enumeration class that allows runtime modification of members.

    This class provides functionality to create and manage enum-like objects that can be modified
    during runtime, unlike traditional Python enums. It supports adding and removing members
    dynamically while maintaining the familiar enum interface.

    Attributes:
        _value2member_map_ (Dict[Any, Any]): Mapping of values to enum members.
    """

    _value2member_map_: Dict[Any, 'DynamicEnum'] = {}

    def __init__(self, **kwargs):
        self._member_names_ = []
        self._member_map_ = {}
        self._value2member_map_: Dict[Any, Any] = {}

        # Initialize with provided members
        for name, value in kwargs.items():
            self.add_member(name, value)

    def __getitem__(self, item):
        return self._member_map_.get(item)

    def __getattr__(self, name):
        try:
            return self._member_map_[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def __iter__(self) -> Iterator['DynamicEnumMember']:
        return iter(self._member_map_.values())

    def __len__(self) -> int:
        return len(self._member_map_)

    def __contains__(self, item) -> bool:
        if isinstance(item, str):
            return item in self._member_map_
        if isinstance(item, DynamicEnumMember):
            return item in self._member_map_.values()
        return False

    def __repr__(self):
        items = [f"{name}={repr(member.value)}" for name, member in self._member_map_.items()]
        return f"{self.__class__.__name__}({', '.join(items)})"

    def add_member(self, name: str, value: Any) -> None:
        """Adds a new member to the enumeration.

        Args:
            name (str): The name of the new enum member.
            value (Any): The value associated with the enum member.

        Raises:
            ValueError: If the name is invalid or already exists.
        """
        if not name.isidentifier():
            raise ValueError(f"Invalid member name: {name}")

        if hasattr(self, name):
            raise ValueError(f"Member {name} already exists")

        member = DynamicEnumMember(name, value, self)
        self._member_names_.append(name)
        self._member_map_[name] = member
        self._value2member_map_[value] = member
        setattr(self, name, member)

    def remove_member(self, name: str) -> None:
        """Removes a member from the enumeration.

        Args:
            name (str): The name of the enum member to remove.

        Raises:
            ValueError: If the member does not exist.
        """
        if name not in self._member_map_:
            raise ValueError(f"Member {name} does not exist")
        member = self._member_map_[name]
        self._member_names_.remove(name)
        del self._member_map_[name]
        del self._value2member_map_[member.value]
        delattr(self, name)

    @property
    def names(self) -> list:
        """Returns a list of all member names.

        Returns:
            list: List of member names.
        """
        return self._member_names_

    @property
    def values(self) -> list:
        """Returns a list of all member values.

        Returns:
            list: List of member values.
        """
        return list(self._value2member_map_.keys())

    @classmethod
    def from_enum(cls, enum_class: type[Enum]) -> 'DynamicEnum':
        """Creates a DynamicEnum from an existing Enum class.

        Args:
            enum_class (type[Enum]): The source Enum class to convert.

        Returns:
            DynamicEnum: A new DynamicEnum instance with members from the source Enum.
        """
        kwargs = {member.name: member.value for member in enum_class}
        return cls(**kwargs)


class DynamicEnumMember:
    """Represents a member of a DynamicEnum.

    This class encapsulates the name and value of an enum member and provides
    comparison and string representation functionality.

    Attributes:
        _name (str): The name of the enum member.
        _value (Any): The value of the enum member.
        _enum_class (DynamicEnum): Reference to the parent enum class.
    """

    def __init__(self, name: str, value: Any, enum_class: DynamicEnum):
        self._name = name
        self._value = value
        self._enum_class = enum_class

    @property
    def name(self) -> str:
        """Gets the name of the enum member.
        Returns:
            str: The name of the enum member.
        """
        return self._name

    @property
    def value(self) -> Any:
        """Gets the value of the enum member.

        Returns:
            Any: The value of the enum member.
        """
        return self._value

    def __eq__(self, other):
        if isinstance(other, DynamicEnumMember):
            return self._value == other._value
        return self._value == other

    def __hash__(self):
        return hash(self._value)

    def __str__(self):
        return f"{self._enum_class.__class__.__name__}.{self._name}"

    def __repr__(self):
        return f"<{self._enum_class.__class__.__name__}.{self._name}: {repr(self._value)}>"


class IterableEnum(Generic[T]):
    """Enumeration for iterable objects.

    This class ensures that the value is an iterable.

    Raises:
        EnumTypeError: If the provided value is not iterable.
    """

    __slots__ = ('_value_',)  # Use slots to restrict instance attributes

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, member in cls.__dict__.items():
            if not name.startswith("_") and not is_iterable(member):
                raise EnumTypeError(f"Enum member '{name}' must be iterable", type(member).__name__)


class IteratorEnum(Generic[T]):
    """Enumeration for iterator objects.

    This class ensures that the value is an iterator.

    Raises:
        EnumTypeError: If the provided value is not an iterator.
    """

    __slots__ = ('_value_',)  # Use slots to restrict instance attributes

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, member in cls.__dict__.items():
            if not name.startswith("_") and not is_iterator(member):
                raise EnumTypeError('Iterator', type(kwargs).__name__)


class GeneratorEnum(Generic[T], Enum):
    """Enumeration for generator objects.

    This class ensures that the value is a generator.

    Raises:
        EnumTypeError: If the provided value is not a generator.
    """

    def __new__(cls, value: Generator[T, None, None]):
        if not is_generator(value):
            raise EnumTypeError('Generator', type(value).__name__)
        obj = object.__new__(cls)  # Create a new instance of the enum class
        obj._value_ = value  # Assign the value to the enum instance
        return obj

    @property
    def value(self):
        return list(self._value_)

    @property
    def name(self):
        return self._name_


@unique
class ByteEnum(bytes, ReprEnum):
    """Enumeration for byte values.

    This class ensures that values are of type bytes.

    Raises:
        EnumTypeError: If the provided value is not of type bytes.
    """

    def __new__(cls, value: bytes):
        if not isinstance(value, bytes):
            raise EnumTypeError('bytes', type(value).__name__)
        obj = bytes.__new__(cls, value)
        return obj


@unique
class FloatEnum(float, ReprEnum):
    """Enumeration for float values.

    This class ensures that values are of type float.

    Raises:
        EnumTypeError: If the provided value is not of type float.
    """

    def __new__(cls, value: float, *args, **kwargs):
        if not isinstance(value, float):
            raise EnumTypeError('float', type(value).__name__)
        obj = float.__new__(cls, value)
        return obj


@unique
class ComplexNumberEnum(complex, ReprEnum):
    def __new__(cls, value: complex, *args, **kwargs):
        if not isinstance(value, complex):
            raise EnumTypeError('complex', type(value).__name__)
        obj = complex.__new__(cls, value)
        return obj


@unique
class DictEnum(dict, ReprEnum):
    """Enumeration for dictionary values.

    This class ensures that a single dictionary is provided during instantiation.

    Raises:
        EnumValidationError: If more than one argument is provided or the first argument is not a dictionary.
    """

    def __new__(cls, *args: Any, **kwargs: Any):
        if len(args) > 1 or (args and not isinstance(args[0], dict)):
            raise EnumValidationError("DictEnum requires a single dictionary argument.")
        obj = dict.__new__(cls, *args, **kwargs)
        return obj


@unique
class SetEnum(set, ReprEnum):
    """Enumeration for set values.

    This class ensures that the provided value is of type set, list, or tuple.

    Raises:
        EnumTypeError: If the provided value is not of type set, list, or tuple.
    """

    def __new__(cls, iterable: set):
        if not isinstance(iterable, set):
            raise EnumTypeError('set', type(iterable).__name__)
        obj = set.__new__(cls)
        return obj


@unique
class ListEnum(list, ReprEnum):
    """Enumeration for list values.

    This class ensures that the provided value is of type list or tuple.

    Raises:
        EnumTypeError: If the provided value is not of type list or tuple.
    """

    def __new__(cls, iterable: list):
        if not isinstance(iterable, list):
            raise EnumTypeError('list', type(iterable).__name__)
        obj = list.__new__(cls)
        return obj


@unique
class TupleEnum(tuple, ReprEnum):
    """Enumeration for tuple values.

    This class ensures that the provided value is of type list or tuple.

    Raises:
        EnumTypeError: If the provided value is not of type list or tuple.
    """

    def __new__(cls, iterable: tuple):
        if not isinstance(iterable, tuple):
            raise EnumTypeError('tuple', type(iterable).__name__)
        obj = tuple.__new__(cls, iterable)
        return obj
