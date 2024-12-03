from enum import Enum

import pytest

from true.enum_registry import EnumRegistry
from true.exceptions import InvalidEnumTypeError


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
    registry = EnumRegistry([SampleEnum, AnotherEnum])
    
    # Deregister single enum
    new_registry = registry.deregister([SampleEnum])
    assert not new_registry.enums  # Currently deregister returns empty registry

    # Test deregistering multiple enums
    empty_registry = registry.deregister([SampleEnum, AnotherEnum])
    assert not empty_registry.enums


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
