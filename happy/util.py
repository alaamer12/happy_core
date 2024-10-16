import asyncio
import functools
# noinspection PyCompatibility
import imghdr
import json
import os
import random
import threading
from collections import OrderedDict
from contextlib import contextmanager, asynccontextmanager
from enum import ReprEnum, unique, Enum, EnumMeta
from threading import RLock
from typing import List, Any, Optional, Mapping, MutableMapping, Iterable, Iterator, Generator, Generic, TypeVar, Type, \
    NoReturn, Union, Dict, Callable, Coroutine, Sized

import pydub.generators
from PIL import Image
from moviepy.editor import ImageSequenceClip, ImageClip

from happy.exceptions import EnumTypeError, EnumValidationError
from happy.types import JsonType
import abc
import concurrent.futures
import logging
import time

T = TypeVar('T')


def is_image(path):
    return imghdr.what(path)


def _random_color() -> tuple[int, int, int]:
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


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


def is_iterable(x: Any) -> bool:
    return isinstance(x, Iterable)


def is_iterator(x: Any) -> bool:
    return isinstance(x, Iterator)


def is_generator(x: Any) -> bool:
    return isinstance(x, Generator)


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
class RangeEnum(int, ReprEnum):
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


def find_first_index(sequence: List[Any], target: Any) -> Optional[int]:
    """Find the first index of 'target' in the sequence."""
    try:
        return sequence.index(target)
    except ValueError:
        return None  # Target not found


def find_last_index(sequence: List[Any], target: Any) -> Optional[int]:
    """Find the last index of 'target' in the sequence."""
    try:
        return len(sequence) - 1 - sequence[::-1].index(target)
    except ValueError:
        return None  # Target not found


def find_all_indices(sequence: List[Any], target: Any) -> List[int]:
    """Find all indices of 'target' in the sequence."""
    return [index for index, value in enumerate(sequence) if value == target]


def find_next_indices(sequence: List[Any], target: Any, start_index: int = 0) -> List[int]:
    """Find all indices of 'target' in the sequence after 'start_index'."""
    return [index for index, value in enumerate(sequence[start_index:], start=start_index) if value == target]


def replace_all(sequence: List[Any], target: Any, replacement: Any) -> List[Any]:
    """Replace all occurrences of 'target' with 'replacement' in the sequence."""
    return [replacement if value == target else value for value in sequence]


def remove_all(sequence: List[Any], target: Any) -> List[Any]:
    """Remove all occurrences of 'target' from the sequence."""
    return [value for value in sequence if value != target]


def find_all(sequence: List[Any], target: Any) -> List[Any]:
    """Find all occurrences of 'target' in the sequence."""
    return [value for value in sequence if value == target]


class ComplexTypeValidator:
    def __init__(self, value, expected_type):
        self.value = value
        self.expected_type = expected_type

    def validate(self) -> bool:
        if isinstance(self.expected_type, type):
            return isinstance(self.value, self.expected_type)
        _types = [list, dict, set, tuple]
        if self.expected_type in _types:
            _validate_type = getattr(self, f"_validate_{self.expected_type.__name__.lower()}_type")
            return _validate_type()
        return False

    def _validate_list_type(self) -> bool:
        if not isinstance(self.value, list) or len(self.expected_type) != 1:
            return False
        return all(ComplexTypeValidator(v, self.expected_type[0]).validate() for v in self.value)

    def _validate_dict_type(self) -> bool:
        if not isinstance(self.value, dict) or len(self.expected_type) != 1:
            return False
        key_type, value_type = list(self.expected_type.items())[0]
        return all(ComplexTypeValidator(k, key_type).validate() and ComplexTypeValidator(v, value_type).validate()
                   for k, v in self.value.items())

    def _validate_set_type(self) -> bool:
        if not isinstance(self.value, set) or len(self.expected_type) != 1:
            return False
        element_type = list(self.expected_type)[0]
        return all(ComplexTypeValidator(e, element_type).validate() for e in self.value)

    def _validate_tuple_type(self) -> bool:
        if not isinstance(self.value, tuple) or len(self.value) != len(self.expected_type):
            return False
        return all(ComplexTypeValidator(v, t).validate() for v, t in zip(self.value, self.expected_type))


@functools.total_ordering
class Constant:
    def __init__(self, **kwargs):
        self.__initialize_constants(**kwargs)

    def __initialize_constants(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    def __setattr__(self, key, value):
        raise AttributeError("Cannot modify a constant")

    def __delattr__(self, key):
        raise AttributeError("Cannot delete a constant")

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Constant) and self.__dict__ == other.__dict__

    def __lt__(self, other):
        if not isinstance(other, Constant):
            return NotImplemented
        return tuple(sorted(self.__dict__.items())) < tuple(sorted(other.__dict__.items()))


@functools.total_ordering
class Pointer:
    def __init__(self, value=None):
        """Initialize the pointer with a value."""
        self._value = [value]  # Use a list to hold the reference

    def get(self):
        """Dereference the pointer to access the value."""
        return self._value[0]

    def set(self, value):
        """Dereference the pointer and set the new value."""
        self._value[0] = value

    def address(self):
        """Return the 'address' of the pointer, which in this case is its own id."""
        return id(self._value)

    def point_to(self, other_pointer):
        """Point this pointer to the memory location of another pointer."""
        if isinstance(other_pointer, Pointer):
            self._value = other_pointer._value
        else:
            raise TypeError("point_to expects another Pointer instance")

    def is_null(self):
        """Check if the pointer is null (i.e., points to None)."""
        return self._value[0] is None

    def __str__(self):
        """String representation showing the value and the 'address'."""
        return f"{self.__class__.__name__}(value={self._value[0]}, address={self.address()})"

    def __repr__(self):
        return self.__str__()

    def __del__(self):
        self._value[0] = None

    def __lt__(self, other):
        if not isinstance(other, Pointer):
            return NotImplemented
        return self.get() < other.get()


class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return key.lower() in self._store

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.items()) == dict(other.items())

    def lower_keys(self):
        """Like keys(), but with all lowercase keys."""
        return (keyval[0] for keyval in self._store.values())

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


class LookupDict(dict):
    """Dictionary lookup object."""

    def __init__(self, name=None):
        self.name = name
        super().__init__()

    def __repr__(self):
        return f"<lookup '{self.name}'>"

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


from abc import ABC, abstractmethod


def _create_file(filename, header, size, content):
    """
    Internal method to create a dummy file with specified header and size.

    :param filename: Name of the file to create.
    :param header: Header bytes of the file.
    :param size: Total size of the file in bytes.
    :param content: Content to fill the file.
    """
    try:
        with open(filename, 'wb') as f:
            f.write(header)
            remaining_size = size - len(header)
            if remaining_size > 0:
                f.write(content * (remaining_size // len(content)) +
                        content[:remaining_size % len(content)])
    except Exception as e:
        print(f"Failed to create file {filename}: {e}")


class FileCreator(ABC):
    """
    Abstract base class that defines the template for creating a dummy file.
    """

    FILE_HEADERS = {
        '.pdf': b'%PDF-1.4\n%',
        '.epub': b'PK\x03\x04',
        '.docx': b'PK\x03\x04',
        '.xlsx': b'PK\x03\x04',
        '.txt': b'',
        '.jpg': b'\xFF\xD8\xFF',
        '.png': b'\x89PNG\r\n\x1a\n',
        '.gif': b'GIF89a',
        '.zip': b'PK\x03\x04',
        '.mp3': b'ID3',  # MP3 audio file
        '.wav': b'RIFF',  # WAV audio file
        '.mp4': b'ftyp',  # MP4 video file
        '.avi': b'RIFF',  # AVI video file
        '.mkv': b'\x1A\x45\xDF\xA3',  # MKV video file
        '.json': b'{',  # JSON file
        '.yaml': b'---',  # YAML file
        '.toml': b'[[',  # TOML file
        '.svg': b'<?xml version="1.0"?>',  # SVG file
        '.bmp': b'BM',  # BMP image file
        '.tiff': b'II*\x00',  # TIFF image file
        '.tar': b'ustar',  # TAR file
        '.rar': b'Rar!',  # RAR file
        '.7z': b'7z\xBC\xAF\x27\x1C',  # 7z file
    }

    def __init__(self, default_size=1024, default_content=None):
        """
        Initialize the FileCreator instance.

        :param default_size: Default size of the dummy file in bytes.
        :param default_content: Default content to fill the dummy file.
        """
        self.default_size = default_size
        self.default_content = default_content or b'0'
        self.created_files = []

    def create_file(self, filename=None, size=None, content=None):
        """
        Template method to create a dummy file.

        :param filename: Name of the file to create.
        :param size: Size of the file in bytes.
        :param content: Content to fill the file.
        """
        filename = filename or self.get_default_filename()
        size = size or self.default_size
        header = self.get_header()
        content = content.encode() if isinstance(content, str) else content or self.default_content
        _create_file(filename, header, size, content)
        self.created_files.append(filename)
        print(f"Created dummy file: {filename} ({size} bytes)")

    @abstractmethod
    def get_header(self):
        """
        Abstract method to get the header bytes for the file type.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_default_filename(self):
        """
        Abstract method to get the default filename for the file type.
        Must be implemented by subclasses.
        """
        pass

    def list_created_files(self):
        """
        List all created dummy files.

        :return: List of filenames.
        """
        return self.created_files.copy()

    def reset(self):
        """
        Reset the list of created files.
        """
        self.created_files = []

    def __repr__(self):
        return f"<{self.__class__.__name__} created: {len(self.created_files)} files>"

    def __str__(self):
        return f"{self.__class__.__name__} Utility - {len(self.created_files)} files created."


# Concrete File Creators
class PDFFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.pdf']

    def get_default_filename(self):
        return 'dummy.pdf'


class EPUBFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.epub']

    def get_default_filename(self):
        return 'dummy.epub'


class DOCXFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.docx']

    def get_default_filename(self):
        return 'dummy.docx'


class XLSXFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.xlsx']

    def get_default_filename(self):
        return 'dummy.xlsx'


class TXTFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.txt']

    def get_default_filename(self):
        return 'dummy.txt'

    def create_file(self, filename=None, size=None, content=None):
        """
        Override to handle text content encoding.
        """
        content = content.encode() if isinstance(content, str) else content or self.default_content
        super().create_file(filename, size, content)


class JPGFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.jpg']

    def get_default_filename(self):
        return 'dummy.jpg'


class PNGFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.png']

    def get_default_filename(self):
        return 'dummy.png'


class GIFFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.gif']

    def get_default_filename(self):
        return 'dummy.gif'


class ZIPFileCreator(FileCreator):
    def get_header(self):
        return self.FILE_HEADERS['.zip']

    def get_default_filename(self):
        return 'dummy.zip'


# Factory to get the appropriate FileCreator
class DummyFile:
    """
    A class to manage the creation out for various types of dummy files using the Template Pattern.
    """

    def __init__(self, default_size=1024, default_content=None):
        self.default_size = default_size
        self.default_content = default_content or b'0'
        self.created_files = []

        # Mapping extensions to their respective creators
        self.creators = {
            '.pdf': PDFFileCreator(default_size, default_content),
            '.epub': EPUBFileCreator(default_size, default_content),
            '.docx': DOCXFileCreator(default_size, default_content),
            '.xlsx': XLSXFileCreator(default_size, default_content),
            '.txt': TXTFileCreator(default_size, default_content),
            '.jpg': JPGFileCreator(default_size, default_content),
            '.png': PNGFileCreator(default_size, default_content),
            '.gif': GIFFileCreator(default_size, default_content),
            '.zip': ZIPFileCreator(default_size, default_content),
            # Add more creators as needed
        }

    def create_file(self, extension, filename=None, size=None, content=None):
        """
        Generic method to create a dummy file based on the extension.

        :param extension: File extension (e.g., '.pdf').
        :param filename: Name of the file to create.
        :param size: Size of the file in bytes.
        :param content: Content to fill the file.
        """
        creator = self.creators.get(extension)
        if not creator:
            print(f"No creator available for extension '{extension}'.")
            return
        creator.create_file(filename, size, content)
        self.created_files.extend(creator.created_files)

    def create_custom(self, filename, extension, header=None, size=None, content=None):
        """
        Create a custom dummy file.

        :param filename: Name of the file.
        :param extension: File extension (e.g., '.custom').
        :param header: Custom header bytes.
        :param size: Size of the file in bytes.
        :param content: Custom content to fill the file.
        """

        class CustomFileCreator(FileCreator):
            def get_header_inner(self):
                return header or self.FILE_HEADERS.get(extension, b'')

            def get_header(self):
                return self.get_header_inner()

            def get_default_filename(self):
                return filename

        custom_creator = CustomFileCreator(self.default_size, self.default_content)
        custom_creator.FILE_HEADERS[extension] = header or b''
        custom_creator.create_file(filename, size, content)
        self.created_files.extend(custom_creator.created_files)

    def list_created_files(self):
        """
        List all created dummy files.

        :return: List of filenames.
        """
        return self.created_files.copy()

    def reset(self):
        """
        Reset the list of created files.
        """
        self.created_files = []
        for creator in self.creators.values():
            creator.reset()
        print("Reset the list of created files.")

    @staticmethod
    def create_image(output_path):
        color = _random_color()
        img = Image.new('RGB', (100, 100), color=color)  # Create images with varying shades of red
        img.save(output_path)  # Save images as PNG files

    def create_video(self, output_path, sequence_dir=None, codec="libx264", fps=10):
        images = [file for file in os.listdir(sequence_dir) if is_image(os.path.join(sequence_dir, file))]
        temp_dir = os.path.join(os.getcwd(), "temp")

        if not images or sequence_dir is None:
            for i in range(10):
                path = os.path.join(temp_dir, f"image_{i:03d}.png")
                self.create_image(path)
                images.append(path)
        clip = ImageSequenceClip(images, fps=fps)
        clip.write_videofile(output_path, codec=codec)

        # Cleanup
        os.removedirs(temp_dir)

    @staticmethod
    def create_static_video(image_path, output_path, codec="libx264", duration=5):
        # Load the image and set its duration
        clip = ImageClip(image_path).set_duration(duration)
        clip.write_videofile(output_path, codec=codec)

    @staticmethod
    def create_audio(filename, duration=3000, frequency=440):
        # Generate a sine wave of specified frequency and duration (in milliseconds)
        audio = pydub.generators.Sine(frequency).to_audio_segment(duration=duration)
        # Export the audio to the specified format
        audio.export(filename, format=filename.split('.')[-1])

    def __repr__(self):
        total_files = sum(len(creator.created_files) for creator in self.creators.values())
        return f"<DummyFile created: {total_files} files>"

    def __str__(self):
        total_files = sum(len(creator.created_files) for creator in self.creators.values())
        return f"DummyFile Utility - {total_files} files created."

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


# Define the Protocol interface
class Protocol(abc.ABC):
    @abc.abstractmethod
    def execute(self, competitor: 'Competitor', config: 'BenchmarkConfiguration') -> Any:
        """
        Execute the protocol against a competitor.
        """
        pass


# Define the Competitor interface
class Competitor(abc.ABC):
    @abc.abstractmethod
    def prepare(self):
        """
        Prepare the competitor for benchmarking.
        """
        pass

    @abc.abstractmethod
    def teardown(self):
        """
        Clean up after benchmarking.
        """
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the competitor.
        """
        pass


# Define the BenchmarkConfiguration dataclass
from dataclasses import dataclass, field


@dataclass
class BenchmarkConfiguration:
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 10.0  # Default timeout in seconds
    concurrency: int = 4  # Number of concurrent threads


# Define BenchmarkResult dataclass
@dataclass
class BenchmarkResult:
    competitor_name: str
    success: bool
    result: Any = None
    error: str = ""
    duration: float = 0.0


# Define the ReportGenerator interface
class ReportGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, results: List[BenchmarkResult]) -> str:
        """
        Generate a report from the benchmarking results.
        """
        pass


# Implement a simple ReportGenerator that generates a text report
class TextReportGenerator(ReportGenerator):
    def generate(self, results: List[BenchmarkResult]) -> str:
        report_lines = ["Benchmark Report", "=" * 50]
        for result in results:
            report_lines.append(f"Competitor: {result.competitor_name}")
            report_lines.append(f"Success: {result.success}")
            if result.success:
                report_lines.append(f"Result: {result.result}")
            else:
                report_lines.append(f"Error: {result.error}")
            report_lines.append(f"Duration: {result.duration:.4f} seconds")
            report_lines.append("-" * 50)
        return "\n".join(report_lines)


# Define the Benchmark class
class Benchmark:
    def __init__(
            self,
            competitors: List[Competitor],
            protocol: Protocol,
            config: BenchmarkConfiguration,
            report_generator: ReportGenerator
    ):
        self.competitors = competitors
        self.protocol = protocol
        self.config = config
        self.report_generator = report_generator
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Benchmark initialized with %d competitors.", len(competitors))

    def run_benchmark(self) -> str:
        results: List[BenchmarkResult] = []
        self.logger.info("Starting benchmark...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.concurrency) as executor:
            future_to_competitor = {
                executor.submit(self._benchmark_competitor, competitor): competitor
                for competitor in self.competitors
            }

            for future in concurrent.futures.as_completed(future_to_competitor):
                competitor = future_to_competitor[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)
                    self.logger.debug("Benchmark completed for %s.", competitor.get_name())
                except concurrent.futures.TimeoutError:
                    self.logger.error("Benchmark timed out for %s.", competitor.get_name())
                    results.append(BenchmarkResult(
                        competitor_name=competitor.get_name(),
                        success=False,
                        error="Timeout",
                        duration=self.config.timeout
                    ))
                except Exception as e:
                    self.logger.exception("Error benchmarking %s: %s", competitor.get_name(), str(e))
                    results.append(BenchmarkResult(
                        competitor_name=competitor.get_name(),
                        success=False,
                        error=str(e)
                    ))

        report = self.report_generator.generate(results)
        self.logger.info("Benchmark completed.")
        return report

    def _benchmark_competitor(self, competitor: Competitor) -> BenchmarkResult:
        self.logger.debug("Preparing competitor %s.", competitor.get_name())
        competitor.prepare()
        start_time = time.time()
        try:
            result = self.protocol.execute(competitor, self.config)
            duration = time.time() - start_time
            self.logger.debug("Execution successful for %s in %.4f seconds.", competitor.get_name(), duration)
            return BenchmarkResult(
                competitor_name=competitor.get_name(),
                success=True,
                result=result,
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error("Execution failed for %s: %s", competitor.get_name(), str(e))
            return BenchmarkResult(
                competitor_name=competitor.get_name(),
                success=False,
                error=str(e),
                duration=duration
            )
        finally:
            self.logger.debug("Tearing down competitor %s.", competitor.get_name())
            competitor.teardown()


class LoggerProtocol(ABC):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...

# Define custom exceptions
class TransactionError(Exception):
    """Base class for transaction-related exceptions."""
    pass

class TransactionCommitError(TransactionError):
    """Raised when a transaction fails to commit."""
    pass

class TransactionRollbackError(TransactionError):
    """Raised when a transaction fails to rollback."""
    pass


class Transaction:
    """
    A class to manage transactional operations with support for synchronous and asynchronous functions,
    logging, callbacks, and advanced transaction management.

    Attributes:
        enable_logging (bool): Flag to enable logging.
        logger (Optional[LoggerProtocol]): Logger instance for transaction logging.
        loop (Optional[asyncio.AbstractEventLoop]): Event loop for async operations.
        _operations (List[Callable[[], Any]]): List of synchronous operations.
        _async_operations (List[Callable[[], Coroutine[Any, Any, Any]]]): List of asynchronous operations.
        _lock (RLock): Lock for managing concurrent access.
        _active (bool): Indicates if a transaction is currently active.
        _savepoints (List[Dict[str, List]]): List of savepoints for transaction state.
        _commit_callbacks (List[Callable[[], Any]]): List of commit callbacks.
        _rollback_callbacks (List[Callable[[], Any]]): List of rollback callbacks.
    """

    def __init__(
            self,
            enable_logging: bool = False,
            logger: Optional[LoggerProtocol] = None,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self._operations: List[Callable[[], Any]] = []
        self._async_operations: List[Callable[[], Coroutine[Any, Any, Any]]] = []
        self._lock = RLock()
        self._active = False
        self._logger = logger or self._configure_default_logger() if enable_logging else None
        self._savepoints: List[Dict[str, List]] = []
        self._commit_callbacks: List[Callable[[], Any]] = []
        self._rollback_callbacks: List[Callable[[], Any]] = []
        self._loop = loop or asyncio.get_event_loop()
        self._traceback = {} # TODO: implement

    @staticmethod
    def _configure_default_logger() -> logging.Logger:
        logger = logging.getLogger('TransactionLogger')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def begin(self):
        with self._lock:
            if self._active:
                if self._logger:
                    self._logger.warning("Nested transactions are not supported directly. Use savepoints.")
                raise TransactionError("Transaction already active. Use savepoints for nested transactions.")
            self._active = True
            self._operations = []
            self._async_operations = []
            self._savepoints = []
            if self._logger:
                self._logger.info("Transaction started.")

    async def begin_async(self):
        self.begin()

    def commit(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to commit.")
            try:
                for operation in self._operations:
                    operation()
                for async_op in self._async_operations:
                    if asyncio.iscoroutinefunction(async_op):
                        self._loop.run_until_complete(async_op())
                    else:
                        async_op()
                for callback in self._commit_callbacks:
                    callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction committed successfully.")
            except Exception as e:
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.error(f"Transaction failed to commit: {e}")
                raise TransactionCommitError(f"Failed to commit transaction: {e}") from e

    async def commit_async(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to commit.")
            try:
                for operation in self._operations:
                    operation()
                for async_op in self._async_operations:
                    if asyncio.iscoroutinefunction(async_op):
                        await async_op()
                    else:
                        async_op()
                for callback in self._commit_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction committed successfully.")
            except Exception as e:
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.error(f"Transaction failed to commit: {e}")
                raise TransactionCommitError(f"Failed to commit transaction: {e}") from e

    def rollback(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to rollback.")
            try:
                for callback in self._rollback_callbacks:
                    callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction rolled back.")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Transaction failed to rollback: {e}")
                raise TransactionRollbackError(f"Failed to rollback transaction: {e}") from e

    async def rollback_async(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to rollback.")
            try:
                for callback in self._rollback_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                self._active = False
                self._operations.clear()
                self._async_operations.clear()
                self._savepoints.clear()
                if self._logger:
                    self._logger.info("Transaction rolled back.")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Transaction failed to rollback: {e}")
                raise TransactionRollbackError(f"Failed to rollback transaction: {e}") from e

    def add_operation(self, operation: Callable[[], Any]):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction. Call begin() before adding operations.")
            self._operations.append(operation)
            if self._logger:
                self._logger.debug(f"Operation added: {operation}")

    def add_async_operation(self, operation: Callable[[], Coroutine[Any, Any, Any]]):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction. Call begin() before adding operations.")
            self._async_operations.append(operation)
            if self._logger:
                self._logger.debug(f"Async operation added: {operation}")

    @contextmanager
    def savepoint(self):
        with self._lock:
            if not self._active:
                raise TransactionError("No active transaction to create a savepoint.")
            savepoint = {
                'operations': list(self._operations),
                'async_operations': list(self._async_operations)
            }
            self._savepoints.append(savepoint)
            if self._logger:
                self._logger.info("Savepoint created.")
            try:
                yield
            except Exception as e:
                last_savepoint = self._savepoints.pop()
                self._operations = last_savepoint['operations']
                self._async_operations = last_savepoint['async_operations']
                if self._logger:
                    self._logger.info("Rolled back to the last savepoint.")
                raise e

    @asynccontextmanager
    async def async_savepoint(self):
        async with self._lock_async():
            if not self._active:
                raise TransactionError("No active transaction to create a savepoint.")
            savepoint = {
                'operations': list(self._operations),
                'async_operations': list(self._async_operations)
            }
            self._savepoints.append(savepoint)
            if self._logger:
                self._logger.info("Savepoint created.")
            try:
                yield
            except Exception as e:
                last_savepoint = self._savepoints.pop()
                self._operations = last_savepoint['operations']
                self._async_operations = last_savepoint['async_operations']
                if self._logger:
                    self._logger.info("Rolled back to the last savepoint.")
                raise e

    def register_commit_callback(self, callback: Callable[[], Any]):
        with self._lock:
            self._commit_callbacks.append(callback)
            if self._logger:
                self._logger.debug(f"Commit callback registered: {callback}")

    def register_rollback_callback(self, callback: Callable[[], Any]):
        with self._lock:
            self._rollback_callbacks.append(callback)
            if self._logger:
                self._logger.debug(f"Rollback callback registered: {callback}")

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except TransactionError:
                self.rollback()
                raise

    async def __aenter__(self):
        await self.begin_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback_async()
        else:
            try:
                await self.commit_async()
            except TransactionError:
                await self.rollback_async()
                raise

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(active={self._active}, "
            f"operations={len(self._operations)}, "
            f"async_operations={len(self._async_operations)}, "
            f"savepoints={len(self._savepoints)})"
        )

    def is_active(self) -> bool:
        return self._active

    def operation_count(self) -> int:
        return len(self._operations) + len(self._async_operations)

    @contextmanager
    def lock(self):
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()

    @asynccontextmanager
    async def lock_async(self):
        await asyncio.to_thread(self._lock.acquire)
        try:
            yield
        finally:
            self._lock.release()

    @asynccontextmanager
    async def lock_async(self):
        await asyncio.to_thread(self._lock.acquire)
        try:
            yield
        finally:
            self._lock.release()
#
# class Pool:
#     def __init__(self, max_workers: int = 10):
#         self._max_workers: int = max_workers
#         self._lock = threading.Lock()
#         self._pool = None
#     def acquire(self):
#         with self._lock:
#             if self._pool is None:
#                 self._pool = ThreadPoolExecutor(max_workers=self._max_workers)
#             return self._pool
#
#     def release(self):
#         with self._lock:
#             if self._pool is not None:
#                 self._pool = None
#
#     def __enter__(self):
#         return self.acquire()
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.release()
#
#     def __aenter__(self):
#         return self.acquire()
#
#     def __aexit__(self, exc_type, exc_val, exc_tb):
#         pass
#
#     def __str__(self):
#         pass
#     def __repr__(self):
#         pass
#
