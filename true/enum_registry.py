"""
This module provides a robust framework for managing and combining multiple Enum classes into a single entity, supporting advanced operations like merging, filtering, and value manipulation. It also includes mechanisms for managing metadata, performing statistical analysis, and serializing Enum data. The key components of the module include various classes for defining metadata, performing operations on Enum members, and managing the relationships between Enum classes.

Classes:
    - EnumMapping: A base class for handling enum mappings, with support for caching and clearing cache.
    - EnumData: A TypedDict that defines metadata for individual Enum members.
    - EnumStats: A data class for storing statistics about the Enum registry, including counts of unique values, enum members, and value types.
    - BaseMetadata: A base class for metadata associated with enum members, including descriptions, tags, and modification timestamps.
    - EnumMetadata: A subclass of BaseMetadata for additional metadata specifically related to enum members, such as aliases and categories.
    - EnumRegistry: A class for managing multiple Enum classes, supporting various operations like addition, subtraction, merging, filtering, and serialization. It provides functionality for working with Enum members, metadata, and statistics.

Functions:
    - The module supports a variety of helper methods, including:
        - `to_dict`: Converts the registry to a dictionary format.
        - `to_json`: Serializes the registry to a JSON string.
        - `statistics`: Provides detailed statistics about the registry.
        - `format_debug`: A method for debugging, showing detailed internal state.
        - Arithmetic operations for combining, subtracting, and intersecting Enum registries.

Type Aliases:
    - NoneMappingEnumTypes: A Union type for representing Enum types that do not have associated metadata.
    - MappedEnumTypes: A dictionary type for mapping Enum classes to their associated metadata.
    - ValidEnumType: A Union type representing valid enum inputs, including both NoneMappingEnumTypes and MappedEnumTypes.

This module is designed to provide powerful features for working with Enums, ideal for use cases involving complex data models and advanced enum manipulation.
"""

from abc import ABC
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from functools import total_ordering
from typing import Generic, Iterable, Iterator, List, Callable, Set, Type, Any, Dict, Optional, Union, NoReturn, Tuple, \
    TypeVar, TypedDict

from true.exceptions import InvalidEnumTypeError, IncompatibleTypesError

class EnumMapping(ABC):
    """Base class for enum mappings"""

    def __init__(self, registry: 'EnumRegistry'):
        self.registry = registry
        self._cache: Dict[Any, Any] = {}

    def clear_cache(self) -> None:
        """Clear the mapping cache"""
        self._cache.clear()

    def all(self) -> List[str]:
        """Get all enum member names"""
        return list(self.registry._members.keys())

    def count(self) -> int:
        """Get total count of enum members"""
        return len(self.registry._members)


class EnumData(TypedDict):
    """Type definition for enum metadata"""
    name: str
    value: Any
    enum_class: str
    metadata: 'EnumMetadata'


@dataclass
class EnumStats:
    total_members: int = 0
    unique_values: int = 0
    enum_counts: int = 0
    value_counts: int = 0
    # value_types: list = field(default_factory=list)
    name_conflicts: int = 0
    created_at: datetime = None

    def __post_init__(self):
        self.created_at = self.created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BaseMetadata(ABC):
    description: str = ""
    tags: Set[str] = None
    deprecated: bool = False
    created_at: datetime = None
    modified_at: datetime = None


@dataclass(kw_only=True)
class EnumMetadata(BaseMetadata):
    """Metadata for enum members"""
    aliases: List[str] = None
    category: str = ""

    def __post_init__(self):
        self.tags = self.tags or set()
        self.aliases = self.aliases or []
        self.created_at = self.created_at or datetime.now()
        self.modified_at = self.modified_at or self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


NoneMappingEnumTypes = Union[Tuple[Type[Enum]], List[Type[Enum]], Set[Type[Enum]]]

MappedEnumTypes = Dict[Type[Enum], EnumMetadata]

ValidEnumType = Union[MappedEnumTypes, NoneMappingEnumTypes]

T = TypeVar('T')


# noinspection PyTypeChecker,PyUnresolvedReferences,PyUnusedName
@total_ordering
class EnumRegistry(Generic[T]):
    """
     A sophisticated class for combining and managing multiple Enum classes with advanced functionality.
     Supports arithmetic operations between CombineEnums instances and Enum classes.

     Features:
     - Combines multiple Enum classes into a single manageable entity
     - Supports arithmetic operations (addition, subtraction, etc.)
     - Supports iteration, comparison, and membership testing
     - Provides value validation and duplicate detection
     - Includes serialization/deserialization capabilities
     - Implements custom string representations
     - Supports advanced filtering and query operations

     Args:
         enums (Iterable[Type[Enum]]): Collection of Enum classes to combine
         duplication (bool, optional): Whether to allow duplicate values. Defaults to False.
     """

    def __init__(self, enums: Optional[ValidEnumType] = None, duplication: bool = False) -> None:
        self.enums, self._metadata = self._validate_enums(enums)
        self._members: Dict[str, Tuple[Enum, Dict]] = OrderedDict()
        self._value_map: Dict[Any, List[Enum]] = defaultdict(list)
        self._created_at = datetime.now().isoformat()

        # Initialize mappings
        self._initialize_instances()

        # Initialize members
        self._initialize_members(duplication)

        # Initialize metadata
        if self._metadata is None:
            self._initialize_metadata()

    @property
    def enum_classes(self) -> Set[Type[Enum]]:
        """Get set of registered enum classes"""
        return {enum_class for enum_class in self.enums}

    @property
    def metadata(self) -> EnumMetadata:
        """Returns the metadata associated with the enum registry."""
        return self._metadata

    def _validate_enums(self, enums: ValidEnumType) -> Union[Tuple[Type[Enum], Optional[EnumMetadata]], NoReturn]:
        if enums is None:
            return (), None
        if isinstance(enums, (list, set, tuple)):  # Checking if enums is any of these collections
            if all(issubclass(item, Enum) for item in enums):  # Ensuring all items are Enum instances
                return self._validate_none_mapping_enums(enums), None  # None for no metadata
            else:
                raise InvalidEnumTypeError(f"All items in the collection must be Enum instances.")
        elif isinstance(enums, dict):
            if all(isinstance(value, Enum) for value in enums.values()):  # Ensure dictionary values are Enum instances
                return self._validate_mapped_enums(enums)
            else:
                raise InvalidEnumTypeError(f"All dictionary values must be Enum instances.")

        raise InvalidEnumTypeError(
            f"Invalid type {type(enums)} for EnumRegistry. Expected NoneMappingEnumTypes or MappedEnumTypes."
        )

    @staticmethod
    def _validate_none_mapping_enums(enums: NoneMappingEnumTypes) -> Tuple[Type[Enum]]:
        return tuple(enum for enum in enums if issubclass(enum, Enum))

    @staticmethod
    def _validate_mapped_enums(enums: MappedEnumTypes) -> Tuple[Type[Enum], EnumMetadata]:
        for enum_type, metadata in enums.items():
            if not issubclass(enum_type, Enum) and isinstance(metadata, EnumMetadata):
                raise InvalidEnumTypeError(f"Enum type {enum_type} is not a valid Enum subclass.")  # noqa: F821
            return enum_type, metadata

    def _initialize_instances(self):
        self.values = self._ValueMapping(self)
        self.types = self._TypeMapping(self)
        self.names = self._NameMapping(self)
        self.filter = self._Filter(self)

    def _initialize_members(self, allow_duplicates: bool) -> None:
        """Initialize internal member mappings"""
        for enum_class in self.enums:
            for member in enum_class:
                if not allow_duplicates and member.value in self._value_map:
                    raise ValueError(
                        f"Duplicate value {member.value} found in {enum_class.__name__}"
                    )
                self._members[member.name] = (member, {})  # Placeholder for member metadata
                self._value_map[member.value].append(member)

    def _initialize_metadata(self) -> 'EnumMetadata':
        # Initialize metadata
        self._metadata = EnumMetadata(
            created_at=self._created_at,
            modified_at=self._created_at,
            description="",
            tags=set(),
            aliases=[],
            category="",
            deprecated=False
        )
        return self._metadata

    @classmethod
    def register(cls, enums: ValidEnumType) -> "EnumRegistry":
        """Register new enums to the registry."""
        instance = cls()
        instance.enums, instance._metadata = instance._validate_enums(enums)
        instance._initialize_members(False)
        return instance

    @classmethod
    def deregister(cls, enums: ValidEnumType) -> "EnumRegistry":
        """Deregister enums from the registry."""
        instance = cls()
        to_remove, _ = instance._validate_enums(enums)
        instance.enums = tuple(enum for enum in instance.enums if enum not in to_remove)
        instance._initialize_members(False)
        return instance

    @classmethod
    def dregister(cls):
        """Decorator to register an enum class."""

        def wrapper(enum_class):
            if not isinstance(enum_class, Iterable):
                enum_class = (enum_class,)
            for ec in enum_class:
                if not issubclass(ec, Enum):
                    raise InvalidEnumTypeError(f"Enum type {ec} is not a valid Enum subclass.")
            cls.register(enum_class)
            return enum_class

        return wrapper

    @classmethod
    def dderegister(cls):
        """Decorator to deregister an enum class."""

        def wrapper(enum_class):
            if not isinstance(enum_class, Iterable):
                enum_class = (enum_class,)
            for ec in enum_class:
                if not issubclass(ec, Enum):
                    raise InvalidEnumTypeError(f"Enum type {ec} is not a valid Enum subclass.")
            cls.deregister(enum_class)
            return enum_class

        return wrapper

    def get_enum_metadata(self, member: Enum) -> Dict[str, Any]:
        """Get metadata for an enum member"""
        return self._metadata.get(member, {})

    def members_of(self, enum_class: str) -> List[Enum]:
        """Get all enum members from a specific enum class."""
        return [member for member in self._members.values() if member.__class__.__name__ == enum_class]

    def set_member_metadata(self, member: Enum, **kwargs) -> None:
        """Set metadata for an enum member"""
        member, metadata = self._members[member.name]
        metadata.update(kwargs)
        self._members[member.name] = (member, metadata)

    def get_member_metadata(self, member: Enum) -> Dict[str, Any]:
        """Get metadata for an enum member"""
        return self._members.get(member.name, None)[1]

    @staticmethod
    def _create_filtered_instance(members: Iterable[Enum]) -> 'EnumRegistry':
        """Helper method to create new instance from filtered members."""
        unique_enum_classes = {member.__class__ for member in members}
        return EnumRegistry(unique_enum_classes)

    def to_dict(self) -> Dict[str, List[EnumData]]:
        """Convert registry to dictionary format"""
        result: Dict[str, List[EnumData]] = {}
        for enum_class in self.enums:
            result[enum_class.__name__] = [
                {
                    'name': member.name,
                    'value': member.value,
                    'enum_class': enum_class.__name__,
                    'metadata': self._metadata
                }
                for member in enum_class
            ]
        return result

    def statistics(self) -> 'EnumStats':
        """Get comprehensive statistics about the registry
        :returns: An EnumStats dataclass instance
        :rtype: EnumStats
        """
        return EnumStats(
            total_members=len(self._members),
            unique_values=len(self._value_map),
            # value_types=[t.__name__ for t in self.types.values()], #
            enum_counts={enum.__name__: len(list(enum)) for enum in self.enums},
            value_counts=self.values.count(),
            name_conflicts=self.names.conflicts_with(),
            created_at=self._created_at
        )

    def members(self) -> Dict[Type[Enum], List[Enum]]:
        """Group members by their original enum class."""
        grouped: Dict[Type[Enum], List[Enum]] = {
            enum_class: [] for enum_class in self.enums
        }
        for member in self._members.values():
            grouped[member[0].__class__].append(member[0])
        return grouped

    def merge(self, *combine_enums: 'EnumRegistry') -> 'EnumRegistry':
        """Merge multiple CombineEnums instances into a new instance."""
        all_enums = [self.enums + tuple(e) for e in combine_enums]
        unique_enums = EnumRegistry(all_enums).unique()
        return unique_enums

    def subset(self, names: Iterable[str]) -> 'EnumRegistry':
        """Create a new EnumRegistry instance with only specified members."""
        valid_names = set(names) & set(self._members.keys())
        if not valid_names:
            raise ValueError("No valid enum names provided")

        filtered_members = {name: self._members[name] for name in valid_names}
        new_registry = EnumRegistry()
        new_registry._members = filtered_members
        new_registry._value_map = {member[0].value: [member[0]] for member in filtered_members.values()}
        new_registry._created_at = datetime.now().isoformat()
        new_registry.enums = tuple({member[0].__class__ for member in filtered_members.values()})
        return new_registry

    def __add__(self, other: Union['EnumRegistry', Type[Enum]]) -> 'EnumRegistry':
        """
        Add another CombineEnums instance or Enum class to this instance.
        Returns a new CombineEnums instance containing members from both operands.

        Args:
            other: Another CombineEnums instance or Enum class

        Returns:
            EnumRegistry: A new instance containing combined members

        Raises:
            IncompatibleTypesError: If other is not a CombineEnums instance or Enum class
        """
        if isinstance(other, EnumRegistry):
            return EnumRegistry(self.enums + tuple(other.enums))
        elif self.is_enum(other):
            return EnumRegistry(self.enums, tuple(other))
        raise IncompatibleTypesError(f"Cannot add {type(other)} to CombineEnums")

    def __sub__(self, other: Union['EnumRegistry', Type[Enum]]) -> 'EnumRegistry':
        """
        Subtract another CombineEnums instance or Enum class from this instance.
        Returns a new CombineEnums instance containing members only from this instance.

        Args:
            other: Another CombineEnums instance or Enum class

        Returns:
            EnumRegistry: A new instance containing remaining members

        Raises:
            IncompatibleTypesError: If other is not a CombineEnums instance or Enum class
        """
        if isinstance(other, EnumRegistry):
            remaining_enums = [enum for enum in self.enums if enum not in other.enums]
        elif self.is_enum(other):
            remaining_enums = [enum for enum in self.enums if enum != other]
        else:
            raise IncompatibleTypesError(f"Cannot subtract {type(other)} from CombineEnums")

        return EnumRegistry(remaining_enums) if remaining_enums else EnumRegistry([])

    @staticmethod
    def is_enum(other: Any) -> bool:
        return isinstance(other, type) and issubclass(other, Enum)

    def intersect(self, other: Union['EnumRegistry', Type[Enum]]) -> 'EnumRegistry':
        """
        Multiply with another CombineEnums instance or Enum class.
        Returns a new CombineEnums instance containing only common members.

        Args:
            other: Another CombineEnums instance or Enum class

        Returns:
            EnumRegistry: A new instance containing common members

        Raises:
            IncompatibleTypesError: If other is not a CombineEnums instance or Enum class
        """
        if isinstance(other, EnumRegistry):
            common_enums = [enum for enum in self.enums if enum in other.enums]
        elif isinstance(other, type) and issubclass(other, Enum):
            common_enums = [enum for enum in self.enums if enum == other]
        else:
            raise IncompatibleTypesError(f"Cannot multiply CombineEnums with {type(other)}")

        return EnumRegistry(common_enums) if common_enums else EnumRegistry([])

    def unique(self) -> 'EnumRegistry':
        """
        Return a new CombineEnums instance with only unique members.
        """
        return self - self.intersect(self)

    def format_debug(self) -> str:
        """
        Comprehensive debug representation showing all internal state.

        Returns a detailed multi-line string showing:
        - All enum classes
        - All members with their values
        - Value mappings
        - Statistics
        """
        lines = ["CombineEnums Debug Information:", "=" * 30, "\nEnum Classes:"]

        # Enum classes
        lines.extend(f"  {i + 1}. {enum.__name__}" for i, enum in enumerate(self.enums))

        # Members
        lines.append("\nMembers:")
        for name, (member, metadata) in self._members.items():
            lines.append(f"  {name}: {member.__class__.__name__}.{member.name} = {member.value}")
            lines.append(f"  {name}: {metadata}")

        # Value mappings
        lines.append("\nValue Mappings:")
        for value, members in self._value_map.items():
            member_str = ", ".join(f"{m.__class__.__name__}.{m.name}" for m in members)
            lines.append(f"  {value}: [{member_str}]")

        # Statistics
        stats = self.statistics()
        lines.append("\nStatistics:")
        for key, value in stats.to_dict().items():
            if isinstance(value, dict):
                lines.append(f"  {key}:")
                lines.extend(f"    {k}: {v}" for k, v in value.items())
            else:
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

    __radd__ = __add__
    __rsub__ = __sub__

    # Inplace operations
    def __iadd__(self, other: Union['EnumRegistry', Type[Enum]]) -> 'EnumRegistry':
        """Inplace addition."""
        return self.__add__(other)

    def __isub__(self, other: Union['EnumRegistry', Type[Enum]]) -> 'EnumRegistry':
        """Inplace subtraction."""
        return self.__sub__(other)

    def __iter__(self) -> Iterator[Enum]:
        """Iterate over all enum members."""
        return iter(self._members.values())

    def __next__(self) -> Enum:
        """Get the next enum member."""
        return next(iter(self))

    def __len__(self) -> int:
        """Get the total number of enum members."""
        return len(self._members)

    def __str__(self) -> str:
        if not self.enums:
            return f"{self.__class__.__name__}(empty)"

        # Group members by their enum class
        grouped_members = self.members()

        # Format each enum class and its members
        enum_lines = []
        for enum_class, members in grouped_members.items():
            member_str = ", ".join(member.name for member in members)
            enum_lines.append(f"  {enum_class.__name__}: {member_str}")

        # Combine all lines
        return "{self.__class__.__name__}(\n" + "\n".join(enum_lines) + "\n)"

    def __repr__(self) -> str:
        if not self.enums:
            return "{self.__class__.__name__}<empty>"

        unique_types = {type(member.value).__name__ for member in self._members.values()}
        duplicates = len(self._members) - len(set(member.value for member in self._members.values()))

        # Format the information
        details = [
            f"  classes=[{', '.join(enum.__name__ for enum in self.enums)}]",
            f"  members={len(self._members)}",
            f"  unique_values={len(self._value_map)}",
            f"  duplicates={duplicates}",
            f"  value_types=[{', '.join(sorted(unique_types))}]"
        ]

        return "{self.__class__.__name__}<\n" + "\n".join(details) + "\n>"

    def __hash__(self) -> int:
        """Generate hash based on enum members."""
        return hash((self.__class__, tuple(self.enums)))

    def __eq__(self, other: Any) -> bool:
        """Compare equality with another CombineEnums instance."""
        if not isinstance(other, EnumRegistry):
            return NotImplemented
        return self.enums == other.enums

    def __lt__(self, other: Any) -> bool:
        """Compare less than with another CombineEnums instance."""
        if not isinstance(other, EnumRegistry):
            return NotImplemented
        return len(self) < len(other)

    def __contains__(self, item: Union[str, Enum, Any]) -> bool:
        """
        Check if an item exists in the combined enums.
        Supports checking by name, enum member, or value.
        """
        if isinstance(item, str):
            return item in self._members
        elif isinstance(item, Enum):
            return item in self._members.values()
        return item in self._value_map

    class _Filter:
        """
        Nested Filter class for performing various filtering operations on EnumRegistry.
        Can be extended to add custom filtering capabilities.
        """

        def __init__(self, parent: 'EnumRegistry'):
            self.parent = parent

        def by_prefix(self, prefix: str) -> 'EnumRegistry':
            """Filter members by name prefix"""
            filtered = [
                member
                for name, (member, _) in self.parent._members.items()
                if name.startswith(prefix)
            ]
            return self.parent._create_filtered_instance(filtered)

        def by_suffix(self, suffix: str) -> 'EnumRegistry':
            """Filter members by name suffix"""
            filtered = [
                member
                for name, (member, _) in self.parent._members.items()
                if name.endswith(suffix)
            ]
            return self.parent._create_filtered_instance(filtered)

        def by_value_type(self, value_type: Type) -> 'EnumRegistry':
            """Filter members by value type"""
            filtered = [
                member
                for member, _ in self.parent._members.values()
                if isinstance(member.value, value_type)
            ]
            return self.parent._create_filtered_instance(filtered)

        def by_predicate(self, predicate: Callable[[Enum], bool]) -> 'EnumRegistry':
            """Filter members using a custom predicate"""
            filtered = [member for member, _ in self.parent._members.values() if predicate(member)]
            return self.parent._create_filtered_instance(filtered)

        def by_metadata(self, **kwargs) -> 'EnumRegistry':
            """Filter members by metadata attributes"""
            filtered = [
                member for member, metadata in self.parent._members.values()
                if all(getattr(metadata, k, None) == v for k, v in kwargs.items())
            ]
            return self.parent._create_filtered_instance(filtered)

        def by_value_range(self, start: Any, end: Any) -> 'EnumRegistry':
            """Filter members by value range (inclusive)"""
            filtered = [
                member
                for member, _ in self.parent._members.values()
                if start <= member.value <= end
            ]
            return self.parent._create_filtered_instance(filtered)

        def exclude(self, *members: Enum) -> 'EnumRegistry':
            """Exclude specific enum members"""
            filtered = [
                member
                for member, _ in self.parent._members.values()
                if member not in members
            ]
            return self.parent._create_filtered_instance(filtered)

    class _ValueMapping(EnumMapping):
        """Maps enum values to their corresponding members"""

        def by(self, value: Any) -> List[Enum]:
            """Get all enum members with a specific value"""
            if value not in self._cache:
                self._cache[value] = self.registry._value_map.get(value, [])
            return self._cache[value]

        def unique(self) -> Set[Any]:
            """Get set of all unique values across all enums"""
            return set(self.registry._value_map.keys())

        def group(self) -> Dict[Any, List[Enum]]:
            """Group enum members by their values"""
            return dict(self.registry._value_map)

        def count(self) -> Dict[Any, int]:
            """Count occurrences of each value"""
            return {value: len(members) for value, members in self.registry._value_map.items()}

        def most_common(self, n: int = 1) -> List[Tuple[Any, int]]:
            """Get the n most common values and their counts"""
            return sorted(self.count().items(), key=lambda x: x[1], reverse=True)[:n]

        def least_common(self, n: int = 1) -> List[Tuple[Any, int]]:
            """Get the n the least common values and their counts"""
            return sorted(self.count().items(), key=lambda x: x[1])[:n]

        def duplicates(self) -> Dict[Any, List[Enum]]:
            """Get all values that are associated with multiple enum members"""
            return {value: members for value, members in self.registry._value_map.items() if len(members) > 1}

    class _TypeMapping(EnumMapping):
        """Maps and analyzes enum value types"""

        def group(self) -> Dict[Type, List[Enum]]:
            """Group enum members by their value types"""
            grouped: Dict[Type, List[Enum]] = defaultdict(list)
            for member, _ in self.registry._members.values():
                grouped[type(member.value)].append(member)
            return dict(grouped)

        def values(self) -> Set[Type]:
            """Get all unique value types"""
            return set(type(member.value) for member, _ in self.registry._members.values())

        def filter(self, value_type: Type) -> List[Enum]:
            """Get all members with values of specified type"""
            return [member for member, _ in self.registry._members.values() if isinstance(member.value, value_type)]

        def count(self) -> Dict[Type, int]:
            """Count occurrences of each value type"""
            return {value_type: len(members) for value_type, members in self.group().items()}

        def most_common(self) -> Optional[Type]:
            """Get the most common value type"""
            type_counts = self.count()
            return max(type_counts, key=type_counts.get) if type_counts else None

    class _NameMapping(EnumMapping):
        """Maps and manages enum names"""

        def by(self, name: str) -> Optional[Enum]:
            """Get enum member by name"""
            member_tuple = self.registry._members.get(name)
            return member_tuple[0] if member_tuple else None

        def search(self, pattern: str) -> List[Enum]:
            """Search enum members by name pattern"""
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            return [
                member[0] for name, member in self.registry._members.items()
                if regex.search(name)
            ]

        def conflicts_with(self) -> Dict[str, List[Type[Enum]]]:
            """Find name conflicts between different enum classes"""
            conflicts: Dict[str, List[Type[Enum]]] = defaultdict(list)
            for enum_class in self.registry.enums:
                for name in enum_class.__members__:
                    conflicts[name].append(Type[Enum](enum_class))
            return {
                name: classes
                for name, classes in conflicts.items()
                if len(classes) > 1
            }
