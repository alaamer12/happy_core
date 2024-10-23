"""
Module that provides decorators and utility functions for enhanced function behavior,
such as timing, debugging, retrying, and handling exceptions.
It also includes utilities for validating complex types, managing constants, and
monitoring execution in multithreaded environments.
"""

import contextlib
from datetime import datetime
from enum import StrEnum
from typing import Callable, Dict, TypeVar, ParamSpec, Optional, Any, Generator, Type, Literal, Protocol, List, Tuple, \
    OrderedDict, Iterable, Union

from happy.types import PathLike, EnvPath

T = TypeVar("T")
P = ParamSpec("P")

Time = Union[float, datetime]


def is_iterable(x: Any) -> bool:
    ...


def is_iterator(x: Any) -> bool:
    ...


def is_generator(x: Any) -> bool:
    ...

def run_once(func: Callable) -> Callable:
    ...

def stop_console_printing(include_stderr: bool = False) -> None:
    """
    Stop printing to the console.
    :param include_stderr:
    :return: None
    """


def start_console_printing() -> None:
    """
    Start printing to the console.
    :return:
    """


def stop_print() -> None:
    """
    Stop Print Statement from printing into the console.
    :return: None
    """


def start_print():
    """
    Start Print Statement to print back again into the console.
    :return:
    """


def to_utc(_time: Time) -> datetime:
    """Convert a time input to UTC datetime."""


def time_to_12oclock(_time: Time) -> str:
    """Convert time to a 12-hour format."""


def time_to_24oclock(_time: Time) -> str:
    """Convert time to a 24-hour format."""


def time_difference(start: Time, end: Time) -> str:
    """Calculate the difference between two time inputs and return it as a string."""


def current_time_utc() -> str:
    """Return the current time in UTC in 24-hour format."""


def current_time_local() -> str:
    """Return the current local time in 12-hour format."""


def convert_sec_to(convertion_type: Literal["Minutes", "Hours", "Days", "Weeks", "Months", "Years", "Milliseconds"],
                   seconds: int) -> float:
    """Return the number of 'convertion_type' that corresponds to 'seconds'."""


def timer(func: Callable, per_counter: bool = False) -> Callable[P, T]:
    """
    Decorator that measures the execution time of a function.

    Args:
        func (Callable[P, T]): The function is to be wrapped by the timer.

    Returns:
        Callable[P, T]: A wrapper function that prints the execution time.
        :param func: The `function` is to be wrapped by the timer.
        :param per_counter: If True, the execution time is printed per counter.
    """


def is_hashable(value: T) -> bool:
    """Check if a value is hashable."""


def is_mutable(value: T) -> bool:
    """Check if a value is mutable."""


def profile(func: Callable) -> Callable:
    """Simple profiling wrapper using 'cProfile'."""


def debugger(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that logs function calls and their results.

    Args:
        func (Callable[P, T]): The function to be wrapped by the debugger.

    Returns:
        Callable[P, T]: A wrapper function that logs the function name, arguments, and return value.
    """


def retry(max_attempts: int, delay: int = 1) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator that retries a function call upon failure.

    Args:
        max_attempts (int): The maximum number of retry attempts.
        delay (int): The delay in seconds between attempts.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: A decorator function that wraps the target function.
    """


def simple_exception(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that catches and logs exceptions for a function.

    Args:
        func (Callable[P, T]): The function to be wrapped by the exception handler.

    Returns:
        Callable[P, T]: A wrapper function that logs exceptions.
    """


def create_exception(message: str, config: Any) -> Type[Exception]:
    """
    Placeholder function for creating custom exceptions.

    Args:
        message (str): The message for the exception.
        config (Any): Configuration data for the exception.

    Returns:
        Type[Exception]: A custom exception class.
    """
    pass


def make_decorator(func: Callable) -> Callable:
    """
    Utility function to create decorators.

    Args:
        func (Callable): The decorator function to be wrapped.

    Returns:
        Callable: A wrapper function that behaves like a decorator.
    """


def memoize(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that caches the results of a function to optimize performance.

    Args:
        func (Callable[P, T]): The function to be wrapped by the memoizer.

    Returns:
        Callable[P, T]: A wrapper function that caches results.
    """


def is_str_regex(_str: str) -> bool:
    """
    Check if a string is a valid regex.
    :param _str:
    :return:
    """


def singleton(cls) -> Callable:
    """
    A thread-safe decorator implementation of Singleton.
    :param cls:
    :return:
    """


def copy_dir(src, dst, **kwargs) -> None:
    """
    Copy a directory (src) to destination (dst).
    :param src:
    :param dst:
    :param kwargs:
    :return:
    """


def copy_file(src, dst) -> None:
    """
    Copy a file (src) to destination (dst).
    :param src:
    :param dst:
    :return:
    """


# src A/B/c , # dst X -> X/A/B/c
def copy_dir_to_same_depth(src: PathLike, dst: PathLike, **kwargs) -> None:
    """
    Copy a directory to the same depth as another directory.
    :param src:
    :param dst:
    :param kwargs:
    :return:
    """


class SingletonMeta(type):
    """
    A thread-safe implementation of Singleton using metaclasses.
    """


def is_decorator(func: Any) -> bool:
    """
    Checks if a function is a decorator.

    Args:
        func (Any): The function to check.

    Returns:
        bool: True if the function is a decorator; otherwise, False.
    """


def monitor(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that logs the execution time and result of a function.

    Args:
        func (Callable[P, T]): The function to be monitored.

    Returns:
        Callable[P, T]: A wrapper function that logs execution details.
    """


def multithreaded(max_workers: int = 5) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator that runs a function in a multithreaded environment.

    Args:
        max_workers (int): The maximum number of threads to use.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: A decorator function that runs the target function in multiple threads.
    """


def _collect_multithreaded_results(future_to_args: Dict[Any, Any]) -> list:
    """
    Collects results from multithreaded function execution.

    Args:
        future_to_args (Dict[Any, Any]): Mapping of futures to their corresponding arguments.

    Returns:
        list: A list of results collected from the executed futures.
    """


@contextlib.contextmanager
def ignore_warnings() -> Generator[None, None, None]:
    """
    Context manager to temporarily suppress warnings.

    Yields:
        None: Suppresses warnings within the context.
    """


def check_internet_connectivity(url: str) -> None:
    """
    Checks if the specified URL is reachable.

    Args:
        url (str): The URL to check for connectivity.

    Raises:
        URLError: If the URL is not reachable.
    """


def find_path(node: str, cwd: str = ".") -> Optional[str]:
    """Search for a file 'node' starting from the directory 'cwd'."""


def multiprocessing(num_processes: int = 4) -> Callable:
    """
    A decorator to parallelize the execution of a function using multiprocessing.

    Args:
        num_processes (int): Number of processes to use.

    Returns:
        Callable: A decorated function that will be executed in parallel.
    """


class FilteredDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        """
        Initialize the FilteredDict with optional initial data and filters.
        """
        self._filters: List[Callable[[Tuple[Any, Any]], bool]] = []
        self._filtered_cache: Optional[OrderedDict] = None

    def add_filter(self, filter_func: Callable) -> None:
        """
        Add a filter function to the list of filters.

        Args:
            filter_func (Callable): A function that takes a key-value tuple and returns a boolean.
        """

    def remove_filter(self, filter_func: Callable[[Tuple[Any, Any]], bool]) -> None:
        """
        Remove a specific filter function from the list of filters.

        Args:
            filter_func (Callable): The filter function to remove.

        Raises:
            ValueError: If the filter_func is not found in the filters list.
        """

    def clear_filters(self) -> None:
        """
        Clear all filters.
        """

    def list_filters(self) -> List[Callable[[Tuple[Any, Any]], bool]]:
        """
        List all current filter functions.

        Returns:
            List[Callable]: A list of filter functions.
        """

    def apply_filters(self) -> 'FilteredDict':
        """
        Apply all filters and return a new FilteredDict containing the filtered items.

        Returns:
            FilteredDict: A new FilteredDict with filtered items.
        """

    @classmethod
    def from_dict(cls, d: dict) -> 'FilteredDict':
        """
        Create a FilteredDict instance from a regular dictionary.

        Args:
            d (dict): The dictionary to convert.

        Returns:
            FilteredDict: A new FilteredDict instance.
        """

    def __getitem__(self, key: Any) -> Any:
        """
        Get an item by key, applying filters if any exist.

        Args:
            key (Any): The key to retrieve.

        Returns:
            Any: The value associated with the key after applying filters.

        Raises:
            KeyError: If the key is not found after filtering.
        """

    def get_filtered_items(self) -> List[Tuple[Any, Any]]:
        """
        Return filtered items as a list of tuples.

        Returns:
            List[Tuple[Any, Any]]: A list of key-value tuples after applying filters.
        """

    def add_regex_filter(self, pattern: str, search_in: str = 'key') -> None:
        """
        Add a filter based on a regex pattern.

        Args:
            pattern (str): The regex pattern to match.
            search_in (str): 'key' to search in keys, 'value' to search in values.

        Raises:
            ValueError: If search_in is not 'key' or 'value'.
        """

    def add_key_filter(self, key_predicate: Callable[[Any], bool]) -> None:
        """
        Add a filter based on a predicate applied to keys.

        Args:
            key_predicate (Callable): A function that takes a key and returns a boolean.
        """

    def add_value_filter(self, value_predicate: Callable[[Any], bool]) -> None:
        """
        Add a filter based on a predicate applied to values.

        Args:
            value_predicate (Callable): A function that takes a value and returns a boolean.
        """

    def update_filters(self, filters: Iterable[Callable[[Tuple[Any, Any]], bool]]) -> None:
        """
        Replace the current filters with a new set of filters.

        Args:
            filters (Iterable[Callable]): An iterable of filter functions.
        """

    def __repr__(self) -> str:
        """
        Return a string representation of the FilteredDict.

        Returns:
            str: The string representation.
        """

    def _invalidate_cache(self) -> None:
        """
        Invalidate the cached filtered results.
        """

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the item and invalidate cache.

        Args:
            key (Any): The key to set.
            value (Any): The value to associate with the key.
        """

    def __delitem__(self, key: Any) -> None:
        """
        Delete the item and invalidate cache.

        Args:
            key (Any): The key to delete.

        Raises:
            KeyError: If the key is not found.
        """


class MODES(StrEnum):
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


# noinspection PyUnusedName
class Environment:
    _mode = MODES.DEV

    def __init__(self, env_data: EnvPath = ".env", **kwargs: object) -> object:
        self._env_data: EnvPath = None
        self.load_env()

    def load_env(self) -> None:
        """Load environment variables from the .env file."""

    def read_env(self) -> Dict[str, str]:
        """Read environment variables from the .env file."""

    def set_env(self, key: str, value: Any) -> None:
        """Set an environment variable programmatically."""

    def get_env(self, key: str) -> Optional[str]:
        """Get the value of an environment variable."""

    def override_env(self, key: str, value: Any) -> Dict[str, str]:
        """
        Override an environment variable without saving it into .env files.

        Args:
            key (str): The environment variable key.
            value (Any): The new value for the environment variable.

        Returns:
            Dict[str, str]: The updated environment variables dictionary.
        """

    def filter_env(
            self, search_value: str, search_in: Literal["key", "value"] = "key"
    ) -> List[Tuple[str, str]]:
        """
        Filter environment variables based on search criteria.

        Args:
            search_value (str): The value to search for.
            search_in (Literal["key", "value"]): Specify whether to search in keys or values.

        Returns:
            List[Tuple[str, str]]: A list of matching key-value pairs.
        """

    def filter_with_predicate(
            self, predicate: Callable[[str, str], bool]
    ) -> List[Tuple[str, str]]:
        """
        Filter environment variables using a custom predicate.

        Args:
            predicate (Callable[[str, str], bool]): A function that takes key and value and returns a boolean.

        Returns:
            List[Tuple[str, str]]: A list of key-value pairs that satisfy the predicate.
        """

    def mode(self, func_mode: MODES = MODES.TEST):
        """
        Decorator to execute a function only in the specified mode.

        Args:
            func_mode (MODES): The mode in which to execute the function.

        Returns:
            Callable: The decorated function.
        """

    @classmethod
    def from_json(cls, json_path: PathLike) -> 'Environment':
        """
        Load environment variables from a JSON file.

        Args:
            json_path (Union[str, Path]): Path to the JSON file.

        Returns:
            Environment: An instance of Environment with variables loaded.
        """

    @classmethod
    def from_dict(cls, env_dict: Dict[str, Any]) -> 'Environment':
        """
        Load environment variables from a dictionary.

        Args:
            env_dict (Dict[str, Any]): Dictionary containing environment variables.

        Returns:
            Environment: An instance of Environment with variables loaded.
        """

    @classmethod
    def from_config(cls, config_path: PathLike) -> 'Environment':
        """
        Load environment variables from a configuration (.ini) file.

        Args:
            config_path (Union[str, Path]): Path to the configuration file.

        Returns:
            Environment: An instance of Environment with variables loaded.
        """

    def __handle_env_path(self, env_path):
        pass


class LoggingProtocol(Protocol):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        ...


class NullLogging(LoggingProtocol):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        ...

    def error(self, msg: str, *args, **kwargs) -> None:
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        ...
