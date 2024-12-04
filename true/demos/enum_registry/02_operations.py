"""
Examples of performing operations on EnumRegistry instances.
"""

from enum import Enum
from true.enum_registry import EnumRegistry

# Define example enums
class Colors(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

class ExtendedColors(Enum):
    RED = "red"  # Duplicate value
    YELLOW = "yellow"
    PURPLE = "purple"

class Numbers(Enum):
    ONE = 1
    TWO = 2
    THREE = 3

def demo_arithmetic():
    """Demonstrate arithmetic operations between registries."""
    print("=== Arithmetic Operations ===")
    
    # Create base registries
    colors = EnumRegistry([Colors, ExtendedColors], duplication=True)
    print(colors)
    numbers = EnumRegistry([Numbers])
#
    # Addition
    print("Addition:")
    combined = colors + numbers
    print(combined)
    print("Colors + Extended Colors members:")
    for member, metadata in combined:
        print(f"- {member} = {metadata}")
#
    # Subtraction
    print("\nSubtraction:")
    difference = combined - numbers
    print("Combined - Colors members:")
    for member, metadata in difference:
        print(f"- {member} = {metadata}")
#

#
def demo_value_analysis():
    """Demonstrate value analysis features."""
    print("\n=== Value Analysis ===")
#
    registry = EnumRegistry([Colors, ExtendedColors, Numbers], duplication=True)
#
#     # Find duplicates
    print("Duplicate values:")
    duplicates = registry.values.duplicates()
    for value, members in duplicates.items():
        print(f"Value '{value}' is used by:")
        for member in members:
            print(f"- {member.name} from {member.__class__.__name__}")
#
    # Value statistics
    print("\nValue statistics:")
    stats = registry.statistics()
    print(f"Total members: {stats.total_members}")
    print(f"Unique values: {stats.unique_values}")
    print(f"Name conflicts: {stats.name_conflicts}")
#
#     # Value grouping
    print("\nMembers grouped by value type:")
    by_type = registry.types.group()
    for type_name, members in by_type.items():
        print(f"\n{type_name}:")
        for member in members:
            print(f"- {member.name} = {member.value}")

if __name__ == "__main__":
    demo_arithmetic()
    demo_value_analysis()
