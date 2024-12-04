"""
Examples of iterable, iterator, and generator enum types.
"""

from typing import Iterator

from true.enums_toolkits import IterableEnum, IteratorEnum


def demo_iterable_enum():
    """Demonstrate IterableEnum usage."""
    print("=== Iterable Enum ===")

    class Sequences(IterableEnum):
        FIBONACCI = [1, 1, 2, 3, 5, 8, 13]
        SQUARES = [1, 4, 9, 16, 25]
        PRIMES = [2, 3, 5, 7, 11]

    print("Sequence values:")
    print(f"  {Sequences.FIBONACCI}: {Sequences.FIBONACCI}")
    print(f"  {Sequences.SQUARES}: {Sequences.SQUARES}")

    # Demonstrate type validation
    print("\nTrying to create invalid IterableEnum...")
    try:
        class Invalid(IterableEnum):
            NOT_ITERABLE = 42  # Not an iterable
    except Exception as e:
        print(f"Error: {e}")


#
def create_counter(start: int, end: int) -> Iterator[int]:
    """Create a simple counter iterator."""
    current = start
    while current <= end:
        yield current
        current += 1


#
def demo_iterator_enum():
    """Demonstrate IteratorEnum usage."""
    print("\n=== Iterator Enum ===")

    class Counters(IteratorEnum):
        SMALL = create_counter(1, 5)
        MEDIUM = create_counter(1, 10)
        LARGE = create_counter(1, 15)

    #
    # Note: Iterators can only be consumed once
    print("Counter ranges:")
    print(f"  {Counters.SMALL}: {list(Counters.SMALL)}")
    print(f"  {Counters.MEDIUM}: {list(Counters.MEDIUM)}")


if __name__ == "__main__":
    demo_iterable_enum()
    demo_iterator_enum()
    # demo_generator_enum()
    # demo_combined_usage()
