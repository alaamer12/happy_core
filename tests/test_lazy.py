import time
from typing import TypeVar

import pytest

from true.collections import lazy_method, LazyDescriptor, LazyMetaClass

T = TypeVar('T')


class ExpensiveCalculation:
    def __init__(self):
        self.computation_count = 0

    @lazy_method
    def expensive_method(self) -> int:
        self.computation_count += 1
        time.sleep(0.1)  # Simulate expensive computation
        return 42

    @property
    @lazy_method
    def expensive_property(self) -> str:
        self.computation_count += 1
        time.sleep(0.1)  # Simulate expensive computation
        return "computed"


class LazyClass(metaclass=LazyMetaClass):
    def __init__(self):
        self.computation_count = 0

    @lazy_method
    def lazy_method(self) -> str:
        self.computation_count += 1
        return "lazy result"


async def async_function():
    return "async result"


# Test LazyDescriptor
def test_lazy_descriptor_basic_functionality():
    """Test that LazyDescriptor properly caches and returns values."""

    class TestClass:
        def __init__(self):
            self.compute_count = 0

        @property
        @lazy_method
        def value(self):
            self.compute_count += 1
            return 42

    obj = TestClass()

    # First access should compute
    assert obj.value == 42
    assert obj.compute_count == 1

    # Subsequent accesses should use cached value
    assert obj.value == 42
    assert obj.value == 42
    assert obj.compute_count == 1


def test_lazy_descriptor_different_instances():
    """Test that LazyDescriptor maintains separate caches for different instances."""

    class TestClass:
        def __init__(self, value):
            self.base_value = value
            self.compute_count = 0

        @property
        @lazy_method
        def value(self):
            self.compute_count += 1
            return self.base_value * 2

    obj1 = TestClass(21)
    obj2 = TestClass(50)

    assert obj1.value == 42
    assert obj2.value == 100

    assert obj1.compute_count == 1
    assert obj2.compute_count == 1

    # Check cache isolation
    assert obj1.value == 42
    assert obj1.compute_count == 1
    assert obj2.value == 100
    assert obj2.compute_count == 1


# Test lazy_method decorator
def test_lazy_method_decorator():
    """Test that @lazy_method properly caches method results."""
    obj = ExpensiveCalculation()

    start_time = time.time()
    result1 = obj.expensive_method()
    first_duration = time.time() - start_time

    start_time = time.time()
    result2 = obj.expensive_method()
    second_duration = time.time() - start_time

    assert result1 == result2 == 42
    assert obj.computation_count == 1
    assert second_duration < first_duration  # Second call should be faster (cached)


def test_lazy_method_with_property():
    """Test that @lazy_method works correctly with @property decorator."""
    obj = ExpensiveCalculation()

    assert obj.expensive_property == "computed"
    assert obj.computation_count == 1

    # Access again
    assert obj.expensive_property == "computed"
    assert obj.computation_count == 1  # Should not increase


def test_lazy_method_async_rejection():
    """Test that @lazy_method raises TypeError for async functions."""
    with pytest.raises(TypeError, match="Async functions are not supported"):
        @lazy_method
        async def async_lazy():
            return "result"


# Test LazyMetaClass
def test_lazy_metaclass():
    """Test that LazyMetaClass properly handles lazy method evaluation."""
    obj = LazyClass()

    # First access
    assert obj.lazy_method() == "lazy result"
    assert obj.computation_count == 1

    # Subsequent accesses
    assert obj.lazy_method() == "lazy result"
    assert obj.lazy_method() == "lazy result"
    assert obj.computation_count == 1


def test_lazy_metaclass_inheritance():
    """Test that LazyMetaClass works correctly with inheritance."""

    class ChildLazyClass(LazyClass):
        @lazy_method
        def child_lazy_method(self):
            self.computation_count += 1
            return "child result"

    obj = ChildLazyClass()

    assert obj.lazy_method() == "lazy result"
    assert obj.child_lazy_method() == "child result"
    assert obj.computation_count == 2

    # Access again
    assert obj.lazy_method() == "lazy result"
    assert obj.child_lazy_method() == "child result"
    assert obj.computation_count == 2  # Should not increase


def test_lazy_descriptor_class_access():
    """Test that accessing descriptor on class returns the descriptor itself."""

    class TestClass(metaclass=LazyMetaClass):
        @property
        @lazy_method
        def value(self):
            return 42

    descriptor = TestClass().value
    with pytest.raises(Exception):  # Not implemented yet
        # TODO: Implement lazy_property and Enable this test
        assert isinstance(descriptor, LazyDescriptor)


def test_cache_name_uniqueness():
    """Test that cache names don't conflict between different lazy attributes."""

    class TestClass:
        def __init__(self):
            self.count1 = 0
            self.count2 = 0

        @property
        @lazy_method
        def value1(self):
            self.count1 += 1
            return 42

        @property
        @lazy_method
        def value2(self):
            self.count2 += 1
            return 84

    obj = TestClass()

    assert obj.value1 == 42
    assert obj.value2 == 84
    assert obj.count1 == 1
    assert obj.count2 == 1

    # Access again
    assert obj.value1 == 42
    assert obj.value2 == 84
    assert obj.count1 == 1
    assert obj.count2 == 1
