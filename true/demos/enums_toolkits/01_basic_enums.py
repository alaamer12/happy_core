"""
Examples of basic specialized enum types from the enums_toolkits module.
"""

from true.enums_toolkits import (
    ByteEnum, FloatEnum, ComplexNumberEnum,
    DictEnum, SetEnum, ListEnum, TupleEnum
)


def demo_numeric_enums():
    """Demonstrate numeric-based enum types."""
    print("=== Numeric Enum Types ===")

    # Float enum example
    class Temperature(FloatEnum):
        FREEZING = 0.0
        ROOM = 20.5
        BOILING = 100.0

    print("Temperature values:")
    for temp in Temperature:
        print(f"{temp.name}: {temp.value}°C")

    # Complex number enum example
    class ComplexPoints(ComplexNumberEnum):
        ORIGIN = 0 + 0j
        UNIT = 1 + 0j
        DIAGONAL = 1 + 1j

    print("\nComplex points:")
    for point in ComplexPoints:
        print(f"{point.name}: {point.value}")


def demo_byte_enum():
    """Demonstrate ByteEnum usage."""
    print("\n=== Byte Enum ===")

    class Flags(ByteEnum):
        EMPTY = b'\x00'
        START = b'\x01'
        STOP = b'\x02'
        RESET = b'\xFF'

    print("Flag values:")
    for flag in Flags:
        print(f"{flag.name}: {flag.value.hex()}")


def demo_collection_enums():
    """Demonstrate collection-based enum types."""
    print("\n=== Collection Enum Types ===")

    # Dict enum example
    class Config(DictEnum):
        DEFAULT = {"debug": False, "timeout": 30}
        DEVELOPMENT = {"debug": True, "timeout": 60}
        PRODUCTION = {"debug": False, "timeout": 10}

    print("Configuration options:")
    for config in Config:
        print(f"\n{config.name}:")
        for key, value in config.value.items():
            print(f"  {key}: {value}")

    # Set enum example
    class Categories(SetEnum):
        FRUITS = {"apple", "banana", "orange"}
        VEGETABLES = {"carrot", "potato", "tomato"}
        GRAINS = {"rice", "wheat", "oats"}

    print("\nFood categories:")
    for category in Categories:
        print(f"\n{category.name}:")
        for item in category.value:
            print(f"  - {item}")

    # List enum example
    class Sequences(ListEnum):
        FIBONACCI = [1, 1, 2, 3, 5, 8, 13]
        SQUARES = [1, 4, 9, 16, 25]
        PRIMES = [2, 3, 5, 7, 11, 13]

    print("\nNumber sequences:")
    for sequence in Sequences:
        print(f"{sequence.name}: {sequence.value}")

    # Tuple enum example
    class Points(TupleEnum):
        ORIGIN = (0, 0)
        UNIT_X = (1, 0)
        UNIT_Y = (0, 1)

    print("\nGeometric points:")
    for point in Points:
        print(f"{point.name}: {point.value}")


def demo_type_validation():
    """Demonstrate type validation of enum values."""
    print("\n=== Type Validation ===")

    try:
        class InvalidTemp(FloatEnum):
            INVALID = "20.5"  # Should be float, not string
    except Exception as e:
        print(f"FloatEnum validation error: {e}")

    try:
        class InvalidDict(DictEnum):
            INVALID = [1, 2, 3]  # Should be dict, not list
    except Exception as e:
        print(f"DictEnum validation error: {e}")


if __name__ == "__main__":
    demo_numeric_enums()
    demo_byte_enum()
    demo_collection_enums()
    demo_type_validation()
