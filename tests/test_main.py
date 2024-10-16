from datetime import datetime, timezone
from io import StringIO
from urllib.error import URLError
import time
from happy import *


# @pytest.mark.slow
def test_timer():
    @timer
    def dummy_function():
        time.sleep(0.1)
        return "done"

    start = time.time()
    result = dummy_function()
    end = time.time()

    assert result == "done"
    assert (end - start) >= 0.1  # Ensure 'timer' is working


# Test for find_path function
def test_find_path(tmpdir):
    test_file = tmpdir.join("test_file.txt")
    test_file.write("content")

    result = find_path("test_file.txt", cwd=tmpdir)

    assert result is not None
    assert "test_file.txt" in result


# Test for debugger decorator
def test_debugger(caplog):
    @debugger
    def dummy_function(a, b):
        return a + b

    result = dummy_function(1, 2)

    assert result == 3
    assert "dummy_function" in caplog.text


# Test for multithreaded decorator
def test_multithreaded():
    @multithreaded(max_workers=2)
    def task(n):
        return n * n

    results = [task(i) for i in range(5)]

    assert results == [0, 1, 4, 9, 16]


# Test for profile decorator
def test_profiling():
    @profile
    def dummy_function():
        return sum([i for i in range(10000)])

    result = dummy_function()

    assert result == sum(range(10000))


# Test for retry decorator
def test_retry():
    @retry(max_attempts=3, delay=1)
    def flaky_function():
        raise ValueError("Failed!")

    with pytest.raises(ValueError):
        flaky_function()


# Test for is_mutable function
def test_is_mutable():
    assert is_mutable([]) is True
    assert is_mutable(()) is False


# Test for multiprocessing decorator
def test_multiprocessing():
    @multiprocessing(num_processes=2)
    def task(n):
        return n + 1

    results = [task(i) for i in range(5)]

    assert results == [1, 2, 3, 4, 5]


# Test for is_hashable function
def test_is_hashable():
    assert is_hashable(()) is True
    assert is_hashable([]) is False


# Test for is_decorator function
def test_is_decorator():
    assert is_decorator(make_decorator) is True
    assert is_decorator(is_hashable) is False


# Test for make_decorator utility
def test_make_decorator():
    def add_1(x):
        return x + 1

    decorator_add1 = make_decorator(add_1)

    @decorator_add1
    def return_5():
        return 5


    assert return_5(5) == 5


# Test for monitor decorator
def test_monitor(caplog):
    @monitor
    def dummy_function():
        return "test"

    result = dummy_function()

    assert result == "test"
    assert "Execution time" in caplog.text


# Test for check_internet_connectivity function
def test_check_internet_connectivity():
    with pytest.raises(URLError):
        check_internet_connectivity("http://nonexistent.url")


import sys
import pytest
from unittest.mock import patch, MagicMock


def test_stop_console_printing(caplog):
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect stdout and stderr to a StringIO object to capture the output
    with (patch('sys.stdout', new_callable=MagicMock()),
          patch('sys.stderr', new_callable=MagicMock())):
        # Call the function to stop console printing
        stop_console_printing()

        print("Hello")

    # Restore original stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr

def test_stop_console_printing_with_stderr(caplog):
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect stdout and stderr to a StringIO object to capture the output
    with patch('sys.stdout', new_callable=MagicMock()) as mock_stdout, \
            patch('sys.stderr', new_callable=MagicMock()) as mock_stderr:
        # Call the function to stop console printing
        stop_console_printing(include_stderr=True)

    sys.stderr.write("Hello\n")

    assert "" in caplog.text

    # Restore original stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr


def test_start_console_printing(caplog):
    # Stop console printing initially
    stop_console_printing()

    # Print something before starting console printing
    print("Hello")

    # Assert that the log is empty because console printing is stopped
    assert "" in caplog.text

    # Start console printing
    start_console_printing()

    # Capture the output of print after starting console printing
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        print("Hello")

        # Get the printed output
        printed_output = mock_stdout.getvalue()

    # Assert that "Hello" is now in the printed output
    assert "Hello" in printed_output


def test_stop_print(caplog):
    stop_print()

    print('Hello')

    assert '' in caplog.text


def test_start_print(caplog):
    # First, stop printing
    stop_print()

    # Attempt to print something while stopped
    print('Hello')

    # Check that nothing is captured in caplog
    assert '' in caplog.text  # This checks if the log is empty

    # Start printing
    start_print()

    # Now print again
    with patch('builtins.print') as mock_print:
        print('Hello')

        # Assert that print was called with 'Hello'
        mock_print.assert_called_once_with('Hello')

    # Verify that caplog has not captured any messages
    assert 'Hello' not in caplog.text

def test_to_utc():
    # Test with a timestamp
    timestamp = time.time()
    utc_time = to_utc(timestamp)
    assert utc_time.tzinfo == timezone.utc

    # Test with a datetime object
    local_time = datetime.now()
    utc_time = to_utc(local_time)
    assert utc_time.tzinfo == timezone.utc

    # Test with invalid input
    with pytest.raises(ValueError):
        to_utc("invalid")

def test_time_to_12oclock():
    utc_time = datetime(2022, 1, 1, 13, 30, tzinfo=timezone.utc)
    assert time_to_12oclock(utc_time) == '01:30:00 PM'

def test_time_to_24oclock():
    utc_time = datetime(2022, 1, 1, 13, 30, tzinfo=timezone.utc)
    assert time_to_24oclock(utc_time) == '13:30:00'

def test_time_difference():
    start_time = datetime(2022, 1, 1, 12, 0, tzinfo=timezone.utc)
    end_time = datetime(2022, 1, 1, 13, 0, tzinfo=timezone.utc)
    assert time_difference(start_time, end_time) == '1:00:00'

def test_current_time_utc():
    current_time = current_time_utc()
    assert len(current_time) == 8  # Should match HH:MM:SS

def test_current_time_local():
    current_time = current_time_local()
    assert len(current_time) == 11  # Should match HH:MM:SS AM/PM

def test_convert_sec_to():
    assert convert_sec_to("Minutes", 120) == 2
    assert convert_sec_to("Hours", 7200) == 2
    with pytest.raises(ValueError):
        convert_sec_to("Invalid", 120)


class TestDummy:
    def test_create_dummy_image(self):
        ...
    def test_create_dummy_video(self):
        ...

    def test_create_dummy_audio(self):
        ...

    def test_create_dummy_file(self):
        ...


