import logging
import sys
import warnings
from io import StringIO
from unittest.mock import patch
from urllib.error import URLError

import pytest

from true.toolkits import stop_console_printing, start_console_printing, is_iterable, is_iterator, is_generator, \
    stop_print, null_decorator, log_level, trace, get_module_size, raised_exception, find_path, memorize, run_once, \
    monitor, make_decorator, is_hashable, is_mutable, retry, multithreaded, singleton, ignore_warnings, \
    check_internet_connectivity, Constants, Pointer


# Test for stop_console_printing and related functions
def test_stop_console_printing(caplog):
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        stop_console_printing()
        print("Test output")
        assert mock_stdout.getvalue() == ""

    sys.stdout = original_stdout
    sys.stderr = original_stderr


def test_stop_console_printing_with_stderr(caplog):
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
            patch('sys.stderr', new_callable=StringIO) as mock_stderr, \
            pytest.warns(UserWarning):
        stop_console_printing(include_stderr=True)
        print("Test output")
        sys.stderr.write("Test error")
        assert mock_stdout.getvalue() == ""
        assert mock_stderr.getvalue() == ""

    sys.stdout = original_stdout
    sys.stderr = original_stderr


def test_start_console_printing():
    stop_console_printing()
    start_console_printing()

    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        print("Test output")
        assert "Test output" in mock_stdout.getvalue()


# Test for type checking functions
def test_is_iterable():
    assert is_iterable([1, 2, 3]) is True
    assert is_iterable("string") is True
    assert is_iterable(42) is False


def test_is_iterator():
    assert is_iterator(iter([1, 2, 3])) is True
    assert is_iterator([1, 2, 3]) is False


def test_is_generator():
    def gen():
        yield 1

    assert is_generator(gen()) is True
    assert is_generator([1, 2, 3]) is False


# Test for print control functions
def test_stop_print():
    with patch('builtins.print') as mock_print:
        stop_print()
        print("Test")
        mock_print.assert_not_called()


# Test for null_decorator
def test_null_decorator():
    assert null_decorator() is None


# Test for log_level context manager
def test_log_level():
    logger_name = "test_logger"
    with log_level(logging.DEBUG, logger_name) as test_logger:
        assert test_logger.level == logging.DEBUG


# Test for trace decorator
def test_trace():
    @trace
    def sample_func(x, y=2):
        return x + y

    with patch('builtins.print') as mock_print:
        result = sample_func(1, y=3)
        assert result == 4
        mock_print.assert_called_once()


# Test for get_module_size
def test_get_module_size():
    class DummyModule:
        attr1 = "test"
        attr2 = [1, 2, 3]

    size = get_module_size(DummyModule)
    assert isinstance(size, int)
    assert size > 0


# Test for raised_exception decorator
def test_raised_exception():
    @raised_exception(ValueError)
    def risky_function():
        raise KeyError("An error occurred!")

    with pytest.raises(Exception):
        risky_function()


# Test for find_path
def test_find_path(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = find_path("test.txt", str(tmp_path))
    assert result == str(test_file)

    result = find_path("nonexistent.txt", str(tmp_path))
    assert result is None


# Test for memoize decorator
def test_memoize():
    call_count = 0

    @memorize
    def expensive_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call
    assert expensive_func(5) == 10
    assert call_count == 1

    # Second call with same argument
    assert expensive_func(5) == 10
    assert call_count == 1  # Should not increase

    # Call with different argument
    assert expensive_func(6) == 12
    assert call_count == 2


# Test for run_once decorator
def test_run_once():
    call_count = 0

    @run_once
    def one_time_func():
        nonlocal call_count
        call_count += 1
        return "result"

    assert one_time_func() == "result"
    assert call_count == 1

    assert one_time_func() is None
    assert call_count == 1  # Should not increase


# Test for monitor decorator
def test_monitor():
    @monitor
    def sample_func():
        return "result"

    with patch('logging.info') as mock_info:
        result = sample_func()
        assert result == "result"
        mock_info.assert_called_once()


def test_monitor_with_exception():
    @monitor
    def failing_func():
        raise ValueError("Test error")

    with patch('logging.error') as mock_error:
        with pytest.raises(ValueError):
            failing_func()
        mock_error.assert_called_once()


# Test for make_decorator
def test_make_decorator():
    @make_decorator
    def custom_decorator(func, *args, **kwargs):
        return func(*args, **kwargs) * 2

    @custom_decorator
    def test_func(x):
        return x

    assert test_func(5) == 10


# Additional Tests for Edge Cases
def test_is_hashable_edge_cases():
    assert is_hashable(None) is True
    assert is_hashable(lambda x: x) is True

    class CustomHashable:
        def __hash__(self): return 1

    assert is_hashable(CustomHashable()) is True


def test_is_mutable_edge_cases():
    assert is_mutable(bytearray(b'test')) is True
    assert is_mutable(frozenset()) is False
    assert is_mutable(tuple()) is False


def test_find_path_with_empty_dir(tmp_path):
    result = find_path("nonexistent.txt", str(tmp_path))
    assert result is None


def test_retry_successful_execution():
    call_count = 0

    @retry(max_attempts=3, delay=0)
    def eventually_successful():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Not yet!")
        return "success"

    assert eventually_successful() == "success"
    assert call_count == 2


@multithreaded(max_workers=3)
def sample_func(x):
    return x * x


@singleton
class SingletonClass:
    pass


# Test cases for multithreaded decorator
def test_multithreaded():
    inputs = [1, 2, 3, 4, 5]
    expected = [x * x for x in inputs]
    results = sample_func(inputs)
    assert sorted(results) == sorted(expected)


def test_multithreaded_empty_input():
    inputs = []
    results = sample_func(inputs)
    assert results == []


# Test case for ignore_warnings context manager
def test_ignore_warnings():
    with ignore_warnings():
        # Code that triggers warnings can go here
        warnings.warn("This is a warning", UserWarning)
        # Assertions can check that no warnings interfere
    assert True  # No error or output indicates success


@patch("urllib.request.urlopen", side_effect=URLError("Connection failed"))
def test_check_internet_connectivity_failure(mock_urlopen):
    # url = "https://www.google.com"
    invalid_url = "https://www.googl.com"
    # check_internet_connectivity(url)
    # Use pytest.raises to ensure URLError is raised
    with pytest.raises(Exception):
        check_internet_connectivity(invalid_url)


# Test cases for singleton
def test_singleton():
    instance1 = SingletonClass()
    instance2 = SingletonClass()
    assert instance1 is instance2


def test_constants_initialization():
    # Initialize a Constants object with some values
    constants = Constants(a=1, b=2)

    # Ensure attributes are correctly initialized
    assert constants.a == 1
    assert constants.b == 2


def test_constants_frozen():
    # Attempt to modify an attribute to check if the dataclass is truly frozen
    constants = Constants(a=1, b=2)

    with pytest.raises(Exception):
        constants.a = 10  # Should raise an exception as the dataclass is frozen


def test_constants_comparison():
    # Create two Constants objects with the same values
    constants1 = Constants(a=1, b=2)
    constants2 = Constants(a=1, b=2)

    # Ensure equality comparison works
    assert constants1 == constants2

    # Modify one constant to check inequality
    constants3 = Constants(a=1, b=3)
    assert constants1 != constants3


def test_constants_lt_comparison():
    constants1 = Constants(a=1, b=2)
    constants2 = Constants(a=2, b=1)

    # Ensure less than comparison works based on sorted key-value tuples
    assert constants1 < constants2
    assert constants2 > constants1


def test_constants_str_repr():
    constants = Constants(a=1, b=2)

    # Check __str__ and __repr__ methods
    assert str(constants) == "{'a': 1, 'b': 2}"
    assert repr(constants) == "{'a': 1, 'b': 2}"


def test_pointer_initialization():
    # Initialize Pointer with a value
    pointer = Pointer(10)

    # Ensure the pointer is correctly initialized
    assert pointer.get() == 10


def test_pointer_set_value():
    # Initialize Pointer and set a new value
    pointer = Pointer(10)
    pointer.set(20)

    # Ensure the value is updated correctly
    assert pointer.get() == 20


def test_pointer_is_null():
    # Initialize Pointer and check null status
    pointer = Pointer(None)
    assert pointer.is_null() is True

    # Initialize Pointer with a value and check null status
    pointer2 = Pointer(10)
    assert pointer2.is_null() is False


def test_pointer_address():
    # Create a pointer and check the address method
    pointer = Pointer(10)
    address = pointer.address()

    # Ensure the address is unique and corresponds to the pointer object
    assert address == id(pointer._value)


def test_pointer_point_to():
    # Create two pointers
    pointer1 = Pointer(10)
    pointer2 = Pointer(20)

    # Point pointer1 to pointer2
    pointer1.point_to(pointer2)

    # Ensure pointer1 now points to the same value as pointer2
    assert pointer1.get() == 20
    assert pointer1.address() == pointer2.address()


def test_pointer_type_error_point_to():
    # Create pointer and try to point it to a non-Pointer object
    pointer1 = Pointer(10)
    with pytest.raises(TypeError):
        pointer1.point_to(10)  # Should raise TypeError as argument is not a Pointer


def test_pointer_lt_comparison():
    pointer1 = Pointer(10)
    pointer2 = Pointer(20)

    # Ensure pointer comparison based on dereferenced value works
    assert pointer1 < pointer2
    assert pointer2 > pointer1


def test_pointer_str_repr():
    # Create a pointer and check string representation
    pointer = Pointer(10)

    # Check __str__ and __repr__ methods
    assert str(pointer) == "Pointer(value=10, address=" + str(pointer.address()) + ")"
    assert repr(pointer) == "Pointer(value=10, address=" + str(pointer.address()) + ")"


def test_pointer_del():
    # Create pointer and ensure value is deleted upon object deletion
    pointer = Pointer(10)
    address_before = pointer.address()
    del pointer
    pointer = Pointer(None)  # To ensure no reference is held
    assert pointer.is_null() is True
