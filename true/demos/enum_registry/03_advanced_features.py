"""
Examples of advanced features in EnumRegistry.
"""

from enum import Enum
from true.enum_registry import EnumRegistry, EnumMetadata, auto

# Define example enums
class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

class UserRole(Enum):
    ADMIN = auto()
    MODERATOR = auto()
    USER = auto()
    GUEST = auto()

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

def demo_decorators():
    """Demonstrate decorator usage for enum registration."""
    print("=== Decorator Usage ===")
    
    registry = EnumRegistry()
    
    # Register using decorator
    @registry.dregister
    class TempStatus(Enum):
        HOT = "hot"
        WARM = "warm"
        COLD = "cold"
    print(registry)
#
    print("Registry after decorator registration:")
    for enum_class in registry.enum_classes:
        print(f"- {enum_class.__name__}")
#
    # Deregister using decorator
    registry.deregister([TempStatus])
#
    print("\nRegistry after decorator deregistration:")
    for enum_class in registry.enum_classes:
        print(f"- {enum_class.__name__}")
#
def demo_serialization():
    """Demonstrate serialization features."""
    print("\n=== Serialization ===")
#
    # Create registry with metadata
    metadata = EnumMetadata(
        tags={"core", "valid"},
        category="active"
    )
#
    registry = EnumRegistry({Status: metadata})
    print(registry)
#
#     # Convert to dictionary
    print("Registry as dictionary:")
    dict_form = registry.to_dict()
    for key, value in dict_form.items():
        if key != "metadata":  # Skip metadata for brevity
            print(f"{key}: {value}")
#
    # Debug format
    print("\nDebug representation:")
    print(registry.format_debug())
#
def demo_advanced_filtering():
    """Demonstrate advanced filtering and analysis."""
    print("\n=== Advanced Filtering ===")
#
    registry = EnumRegistry([Status, UserRole, Priority], duplication=True)
#
#     # Filter by metadata

    registry.set_member_metadata(
        Status.ACTIVE,
        tags={"core", "valid"},
        category="active"
    )
    registry.set_member_metadata(
        Status.INACTIVE,
        tags={"core", "invalid"},
        category="inactive"
    )
#
    print("Members with 'core' tag:")
    core_members = registry.filter.by_metadata(tags={"core"})
    print(core_members)
    for member, metadata in core_members:
        print(f"- {member} = {metadata}")
#
    # Value range filtering
    print("\nPriorities in range 2-3:")
    mid_priorities = registry.filter.within_values_range(start=2, end=3, skip_non_numeric=True)
    for member, metadata in mid_priorities:
        print(f"- {member} = {metadata}")
#
    # Most/least common values
    print("\nMost common values:")
    most_common = registry.values.most_common(4)
    for value, count in most_common:
        print(f"Value '{value}' appears {count} times")
#
def demo_conflict_detection():
    """Demonstrate name conflict detection."""
    print("\n=== Conflict Detection ===")
#
    # Create enums with conflicting names
    class StatusA(Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
#
    class StatusB(Enum):
        ACTIVE = 1  # Conflicting name
        PENDING = 2
#
    registry = EnumRegistry([StatusA, StatusB], duplication=True)
#
    print("Name conflicts:")
    conflicts = registry.names.conflicts_with()
    for name, classes in conflicts.items():
        print(f"\nConflict for name '{name}':")
        for cls in classes:
            print(f"- Defined in {cls.__name__} with value: {cls[name].value}")

if __name__ == "__main__":
    demo_decorators()
    demo_serialization()
    demo_advanced_filtering()
    demo_conflict_detection()
