"""
Examples of dynamic enum creation and manipulation.
"""

from true.enums_toolkits import DynamicEnum, DynamicEnumMember

def demo_basic_dynamic_enum():
    """Demonstrate basic DynamicEnum creation and usage."""
    print("=== Basic Dynamic Enum ===")
    
    # Create dynamic enum with initial members
    status = DynamicEnum(
        PENDING="pending",
        ACTIVE="active",
        INACTIVE="inactive"
    )
    
    print("Initial members:")
    for member in status:
        print(f"{member.name}: {member.value}")
    
    # Add new member
    print("\nAdding new member 'DELETED'...")
    status.add_member("DELETED", "deleted")
    
    print("Updated members:")
    for member in status:
        print(f"{member.name}: {member.value}")
    
    # Remove member
    print("\nRemoving member 'INACTIVE'...")
    status.remove_member("INACTIVE")
    
    print("Final members:")
    for member in status:
        print(f"{member.name}: {member.value}")

def demo_dynamic_enum_operations():
    """Demonstrate operations with DynamicEnum."""
    print("\n=== Dynamic Enum Operations ===")
    
    # Create enum with numeric values
    levels = DynamicEnum(
        LOW=1,
        MEDIUM=2,
        HIGH=3
    )
    
    print("Available levels:")
    print(f"Names: {levels.names}")
    print(f"Values: {levels.values}")
    
    # Access members
    print("\nAccessing members:")
    high = levels["HIGH"]
    print(f"HIGH level: {high.name} = {high.value}")
    
    # Check membership
    print("\nMembership tests:")
    print(f"'HIGH' in levels: {'HIGH' in levels}")
    print(f"'CRITICAL' in levels: {'CRITICAL' in levels}")
    
    # Length
    print(f"\nTotal members: {len(levels)}")

def demo_conversion_from_enum():
    """Demonstrate converting regular Enum to DynamicEnum."""
    print("\n=== Converting from Regular Enum ===")
    
    from enum import Enum
    
    # Regular enum
    class Color(Enum):
        RED = "#FF0000"
        GREEN = "#00FF00"
        BLUE = "#0000FF"
    
    # Convert to dynamic enum
    dynamic_colors = DynamicEnum.from_enum(Color)
    
    print("Converted colors:")
    for member in dynamic_colors:
        print(f"{member.name}: {member.value}")
    
    # Add new color
    print("\nAdding new color...")
    dynamic_colors.add_member("YELLOW", "#FFFF00")
    
    print("Updated colors:")
    for member in dynamic_colors:
        print(f"{member.name}: {member.value}")

def demo_error_handling():
    """Demonstrate error handling in DynamicEnum."""
    print("\n=== Error Handling ===")
    
    numbers = DynamicEnum(ONE=1, TWO=2)
    
    # Try to add existing member
    print("Trying to add existing member...")
    try:
        numbers.add_member("ONE", 1)
    except ValueError as e:
        print(f"Error: {e}")
    
    # Try to remove non-existent member
    print("\nTrying to remove non-existent member...")
    try:
        numbers.remove_member("THREE")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Try to access non-existent member
    print("\nTrying to access non-existent member...")
    try:
        value = numbers["THREE"]
    except KeyError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    demo_basic_dynamic_enum()
    demo_dynamic_enum_operations()
    demo_conversion_from_enum()
    demo_error_handling()
