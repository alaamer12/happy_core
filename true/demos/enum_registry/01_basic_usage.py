"""
Basic usage examples of the EnumRegistry class.
"""

from enum import Enum

from true.enum_registry import EnumRegistry, EnumMetadata, auto


# Define some example enums
class Colors(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Sizes(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()


class Priorities(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


def demo_basic_creation():
    """Demonstrate basic EnumRegistry creation and inspection."""
    print("=== Basic EnumRegistry Creation ===")

    # Create registry with multiple enums
    registry = EnumRegistry([Sizes, Priorities])

    print(f"Total members: {len(registry)}")
    print("\nRegistered enum classes:")
    for enum_class in registry.enum_classes:
        print(f"- {enum_class.__name__}")

    print("\nAll members:")
    for member, metadata in registry:
        print(f"- {member} = {metadata}")


def demo_metadata():
    """Demonstrate working with enum metadata."""
    print("\n=== Enum Metadata ===")

    # Create registry with metadata
    metadata = EnumMetadata(
        description="Color values",
        tags={"warm", "cool"}
    )

    registry = EnumRegistry({Colors: metadata})
    print(registry)
    # Add metadata for specific members
    registry.set_member_metadata(
        Colors.RED,
        description="Primary red color",
        tags={"primary", "warm"},
        aliases=["crimson", "scarlet"]
    )
    print()

    # # Display metadata
    print("Registry metadata:")
    print(f"Colors description: {registry.metadata[Colors].description}")
    print(f"Colors tags: {registry.metadata[Colors].tags}")

    print("\nRED member metadata:")
    red_metadata = registry.get_member_metadata(Colors.RED)
    print(f"Description: {red_metadata}")
    print(f"Tags: {red_metadata}")
    print(f"Aliases: {red_metadata}")


def demo_member_access():
    """Demonstrate different ways to access enum members."""
    print("\n=== Member Access ===")

    registry = EnumRegistry([Colors, Sizes, Priorities])

    # Access by name
    print("Access by name:")
    red = registry.values.by(value="red")
    print(red)
    print(f"Found member: {red[0].name} = {red[0].value}")

    # Search by pattern
    print("\nSearch by pattern:")
    medium_members = registry.names.search("MEDIUM")
    print(medium_members)
    for member in medium_members:
        print(f"Found member: {member.name} = {member.value}")
    #
    # # Filter by value type
    print("\nFilter by value type:")
    filtered_registry = registry.filter.by_predicate(lambda member: isinstance(member.value, str))
    print(filtered_registry)


if __name__ == "__main__":
    # demo_basic_creation()
    demo_metadata()
    demo_member_access()
