import json
from enum import Enum, EnumMeta, unique, ReprEnum
from typing import TypeVar, Any, Dict, Type, Union, NoReturn, Generic, Iterable, Iterator, Generator

from happy import is_iterable, is_iterator, is_generator
from happy.exceptions import EnumTypeError, EnumValidationError
from happy.types import JsonType

T = TypeVar('T')


class AdvancedEnumMeta(EnumMeta):
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
        """
        Dynamically create a new Enum class from a dictionary.

        Args:
            name (str): The name of the new Enum class.
            members (dict): A dictionary where keys are member names and values are member values.

        Returns:
            Type[Enum]: A new Enum class.
        """
        return Enum(name, members)

    @classmethod
    def from_json(cls, name: str, json_data: JsonType) -> Type[Enum]:
        """
        Dynamically create a new Enum class from a JSON string or dictionary.

        Args:
            name (str): The name of the new Enum class.
            json_data (JsonType): A JSON string or dictionary representing enum members.

        Returns:
            Type[Enum]: A new Enum class.
        """
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


def metadata(cls: Type[Enum]) -> Type[Enum]:
    """
    Decorator to enhance Enum classes with additional methods and properties.
    """

    @property
    def describe(self) -> str:
        """
        Generate a detailed description of the enum member.
        """
        attributes = {
            "Type": type(self.value).__name__,
            "Value": self.value,
            "Size (bits)": self.value.bit_length(),
            "Default": "N/A",  # Can be customized based on context
        }
        description = [f"{self.__class__.__name__} Member: {self.name}"]
        description.extend([f"{key}: {value}" for key, value in attributes.items()])
        return "\n".join(description)

    @describe.setter
    def describe(self, *args: str) -> Union[str, NoReturn]:
        arg_len = len(args)
        if arg_len < 1 or not isinstance(args[0], str):
            raise ValueError("Expected at least one str argument. or four arguments.")
        if arg_len == 1:
            return args[0]
        if 1 <= arg_len < 4:
            raise ValueError("Expected at least one str argument. or four arguments.")

        attributes = {
            "Type": args[0],
            "Value": args[1],
            "Size (bits)": args[2],
            "Default": args[3],  # Can be customized based on context
        }
        description = [f"{self.__class__.__name__} Member: {self.name}"]
        description.extend([f"{key}: {value}" for key, value in attributes.items()])
        return "\n".join(description)

    @describe.deleter
    def describe(self):
        pass

    def extend_description(cls, additional_info: dict) -> str:
        """
        Extend the description of the enum member with additional information.
        Useful for advanced users needing more contextual information.
        """
        base_description = cls.describe
        additional_description = [f"{key}: {value}" for key, value in additional_info.items()]
        return base_description + "\n" + "\n".join(additional_description)

    # noinspection PyTypeChecker
    cls.describe = property(fset=describe.setter, fget=describe, fdel=describe.deleter)
    cls.extend_description = classmethod(extend_description)

    return cls


class DynamicEnum(Enum):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def add_member(self, name, value):
        setattr(self, name, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class IterableEnum(Generic[T]):
    def __new__(cls, value: Iterable[T]):
        if not is_iterable(value):
            raise EnumTypeError('Iterable', type(value).__name__)
        Iterable.__new__(cls)
        self = super().__new__(cls, value)
        self.value = value
        return self



class IteratorEnum(Generic[T]):
    def __new__(cls, value: Iterator[T]):
        if not is_iterator(value):
            raise EnumTypeError('Iterator', type(value).__name__)
        Iterator.__new__(cls)
        self = super().__new__(cls, value)
        self.value = value
        return self


class GeneratorEnum(Generic[T], Enum):
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
class RangingEnum(int, ReprEnum):
    def __new__(cls, value: int, min_value: int, max_value: int):
        if not isinstance(value, int):
            raise EnumTypeError('int', type(value).__name__)
        if not (min_value <= value <= max_value):
            raise EnumValidationError(f"Value must be between {min_value} and {max_value}.")
        obj = int.__new__(cls, value)
        return obj


@unique
class ByteEnum(bytes, ReprEnum):
    def __new__(cls, value: bytes):
        if not isinstance(value, bytes):
            raise EnumTypeError('bytes', type(value).__name__)
        obj = bytes.__new__(cls, value)
        return obj


@unique
class FloatEnum(float, ReprEnum):
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
    def __new__(cls, *args: Any, **kwargs: Any):
        if len(args) > 1 or (args and not isinstance(args[0], dict)):
            raise EnumValidationError("DictEnum requires a single dictionary argument.")
        obj = dict.__new__(cls, *args, **kwargs)
        return obj


@unique
class SetEnum(set, ReprEnum):
    def __new__(cls, iterable: Any):
        if not isinstance(iterable, (set, list, tuple)):
            raise EnumTypeError('set, list, or tuple', type(iterable).__name__)
        obj = set.__new__(cls)
        return obj


@unique
class ListEnum(list, ReprEnum):
    def __new__(cls, iterable: Any):
        if not isinstance(iterable, (list, tuple)):
            raise EnumTypeError('list or tuple', type(iterable).__name__)
        obj = list.__new__(cls)
        return obj


@unique
class TupleEnum(tuple, ReprEnum):
    def __new__(cls, iterable: Any):
        if not isinstance(iterable, (list, tuple)):
            raise EnumTypeError('list or tuple', type(iterable).__name__)
        obj = tuple.__new__(cls, iterable)
        return obj