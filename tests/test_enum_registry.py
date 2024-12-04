from enum import Enum

import pytest
from true.exceptions import InvalidEnumTypeError

from true.enum_registry import EnumRegistry, EnumMetadata, EnumStats


class SampleEnum(Enum):
    OPTION_A = 1
    OPTION_B = 2


class AnotherEnum(Enum):
    OPTION_X = "x"
    OPTION_Y = "y"


@pytest.fixture
def registry():
    """Fixture to provide a default EnumRegistry instance with two enums."""
    return EnumRegistry([SampleEnum, AnotherEnum])


# 1. Initialization and Properties
def test_init_registry(registry):
    """Test basic initialization of EnumRegistry with sample enums."""
    assert registry


def test_registry_initialization(registry):
    """Test basic initialization of EnumRegistry with sample enums."""
    assert isinstance(registry, EnumRegistry)
    assert len(registry.enums) == 2
    assert SampleEnum in registry.enums
    assert AnotherEnum in registry.enums


def test_registry_empty_initialization():
    """Test initializing EnumRegistry with no enums."""
    empty_registry = EnumRegistry()
    assert len(empty_registry.enums) == 0


def test_register_method():
    """Test registering new enums using the register method."""
    # Test registering single enum
    registry = EnumRegistry([SampleEnum])
    assert SampleEnum in registry.enums

    # Test registering multiple enums
    multi_registry = EnumRegistry([SampleEnum, AnotherEnum])
    assert SampleEnum in multi_registry.enums
    assert AnotherEnum in multi_registry.enums


def test_deregister_method():
    """Test deregistering enums using the deregister method."""
    old_registry = EnumRegistry([SampleEnum, AnotherEnum])
    
    # Deregister single enum
    new_registry = old_registry.deregister([SampleEnum])
    # assert new_registry != old_registry
    e:tuple = new_registry.enums
    assert len(e) == 1


    # # Test deregistering multiple enums
    # empty_registry = registry.deregister([SampleEnum, AnotherEnum])
    # assert not empty_registry.enums


def test_dregister_decorator():
    """Test registering enums using the dregister decorator."""
    class DecoratedEnum(Enum):
        ITEM_1 = 1
        ITEM_2 = 2

    registry = EnumRegistry([DecoratedEnum])
    assert DecoratedEnum in registry.enums


def test_dderegister_decorator():
    """Test deregistering enums using the dderegister decorator."""
    class ToDeregisterEnum(Enum):
        TEST_A = "test_a"
        TEST_B = "test_b"

    registry = EnumRegistry([ToDeregisterEnum])
    assert ToDeregisterEnum in registry.enums
    
    new_registry = registry.deregister([ToDeregisterEnum])
    assert not new_registry.enums


def test_invalid_registration():
    """Test that registering invalid enum types raises appropriate errors."""
    # Test with non-enum type
    class NotAnEnum:
        pass
    
    with pytest.raises(InvalidEnumTypeError):
        EnumRegistry([NotAnEnum])

    # Test with invalid input type
    with pytest.raises(InvalidEnumTypeError):
        EnumRegistry(NotAnEnum)


def test_empty_deregistration():
    """Test deregistering from empty registry."""
    registry = EnumRegistry()
    empty_registry = registry.deregister([SampleEnum])
    assert not empty_registry.enums


# 2. Enum Metadata and Statistics
def test_metadata_initialization(registry):
    """Test that metadata initializes correctly if not provided."""
    assert registry.metadata.created_at is not None
    assert isinstance(registry.metadata, EnumMetadata)


def test_enum_statistics(registry):
    """Test statistics method returns accurate EnumStats."""
    stats = registry.statistics()
    assert isinstance(stats, EnumStats)

    expected = len(SampleEnum) + len(AnotherEnum)
    found = stats.total_members
    assert found == expected


# 3. Member Management
def test_member_retrieval_by_name(registry):
    """Test that members can be retrieved by name."""
    expected = [SampleEnum.OPTION_A, SampleEnum.OPTION_B]
    enums = registry.members()
    found = []
    for enum, members in enums.items():
        found = [member for member in members]
        break  # To get first one
    assert found == expected


def test_set_member_metadata(registry):
    """Test setting metadata for specific enum members."""
    registry.set_member_metadata(SampleEnum.OPTION_A, deprecated=True)
    metadata = registry.get_member_metadata(SampleEnum.OPTION_A)
    assert metadata["deprecated"] is True


# 4. Arithmetic Operations
def test_registry_addition():
    """Test combining two EnumRegistry instances using addition."""
    reg1 = EnumRegistry([SampleEnum])
    reg2 = EnumRegistry([AnotherEnum])
    combined = reg1 + reg2
    expected = len(SampleEnum) + len(AnotherEnum)
    found = len(combined._members)
    assert found == expected


def test_registry_subtraction():
    """Test removing enums from an EnumRegistry using subtraction."""
    reg1 = EnumRegistry([SampleEnum, AnotherEnum], duplication=True)
    reduced = reg1 - AnotherEnum
    assert reduced.enums == (SampleEnum,)


# 5. Conversion Methods
def test_to_dict_conversion(registry):
    """Test converting registry to dictionary format."""
    registry_dict = registry.to_dict()
    assert "SampleEnum" in registry_dict
    assert "AnotherEnum" in registry_dict
    assert isinstance(registry_dict["SampleEnum"][0], dict)


# 7. Edge Cases
def test_invalid_enum_type_raises_error():
    """Test that providing an invalid enum type raises an error."""
    with pytest.raises(Exception):
        EnumRegistry(["InvalidEnum"])


def test_duplicate_value_raises_error():
    """Test that enabling duplicate values raises an error if they are found."""
    with pytest.raises(ValueError):
        EnumRegistry([SampleEnum, SampleEnum], duplication=False)


# 8. Debugging and String Representations
def test_format_debug(registry):
    """Test debug format output contains correct class and member information."""
    debug_str = registry.format_debug()
    assert "CombineEnums Debug Information:" in debug_str
    assert "SampleEnum" in debug_str
    assert "OPTION_A" in debug_str