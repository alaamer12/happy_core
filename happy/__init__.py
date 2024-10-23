from __future__ import annotations

import asyncio
import builtins
import cProfile
import configparser
import contextlib
import functools
import inspect
import json
import logging
import multiprocessing as py_multiprocessing
import os
import pstats
import re
import shutil
import sys
import threading
import time
import warnings
import zlib
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from enum import StrEnum
from functools import wraps
from typing import (Callable, Any, List, Dict,
                    ParamSpec, Type, TypeVar,
                    Optional, Union, Literal,
                    Tuple, Iterable, NoReturn, Iterator, Generator)
from urllib.error import URLError
from urllib.request import urlopen
import dotenv

from happy.exceptions import (TrivialOperationError,
                              ComplexOperationError,
                              CriticalOperationError,
                              BrokenOperationError,
                              LongTimeRunningError,
                              SlowOperationError,
                              DebuggingOperationError,
                              MarkException,
                              EnvError)
from happy.types import PathLike, EnvPath
from happy.protocols import LoggerProtocol, StackProtocol

T = TypeVar("T")

P = ParamSpec("P")


def stop_console_printing(include_stderr: bool = False):
    if include_stderr:
        warnings.warn("This is not recommended. Please use this on your own risk.", stacklevel=2)
        sys.stderr = open(os.devnull, 'w')
    sys.stdout = open(os.devnull, 'w')


def start_console_printing():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def is_iterable(x: Any) -> bool:
    return isinstance(x, Iterable)


def is_iterator(x: Any) -> bool:
    return isinstance(x, Iterator)


def is_generator(x: Any) -> bool:
    return isinstance(x, Generator)

# noinspection PyUnusedLocal
def empty_function(func):
    pass


def stop_print():
    builtins.print = empty_function


def start_print():
    builtins.print = print


Time = Union[float, datetime]


# def handle_sync_async_methods(cls: Type):
#     # Iterate over all attributes in the class
#     for attr_name, attr_value in cls.__dict__.items():
#         # Check if the attribute is a callable (i.e., a method)
#         if callable(attr_value):
#             original_method = attr_value  # Store the original method
#
#             # Create a wrapper to handle sync/async methods
#             @functools.wraps(original_method)
#             def wrapper(self, *args, **kwargs):
#                 # Call the handle_sync_async only once when the method is invoked
#                 return handle_sync_async(original_method)(self, *args, **kwargs)
#
#             # Set the wrapper as the new attribute for the method
#             setattr(cls, attr_name, wrapper)
#
#     return cls

def null_decorator():
    """
    A decorator returns null
    :return:
    """
    return None


@contextlib.contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)


def trace(func: Callable) -> Callable:
    functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__}({args!r}, {kwargs!r}) ' f'-> {result!r}')
        return result
    return wrapper



def handle_sync_async(func: Callable) -> Callable:
    @functools.wraps(func)
    def decorator(*args, **kwargs) -> Any:
        if asyncio.iscoroutinefunction(func):
            # If the function is asynchronous, run it as a coroutine
            return asyncio.run(func(*args, **kwargs))
        else:
            # Otherwise, call the synchronous function directly
            return func(*args, **kwargs)

    return decorator


def raised_exception(func: Callable, exception: Type[Exception]) -> Union[Callable, NoReturn]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise exception from e

    return wrapper


def to_utc(_time: Time) -> datetime:
    """Convert a time input to UTC datetime."""
    if isinstance(_time, float):
        return datetime.fromtimestamp(_time, tz=timezone.utc)
    elif isinstance(_time, datetime):
        return _time.astimezone(timezone.utc)
    raise ValueError("Input must be a float (timestamp) or datetime object.")


def time_to_12oclock(_time: Time) -> str:
    """Convert time to a 12-hour format."""
    utc_time = to_utc(_time)
    return utc_time.strftime("%I:%M:%S %p")


def time_to_24oclock(_time: Time) -> str:
    """Convert time to a 24-hour format."""
    utc_time = to_utc(_time)
    return utc_time.strftime("%H:%M:%S")


def time_difference(start: Time, end: Time) -> str:
    """Calculate the difference between two time inputs and return it as a string."""
    start_utc = to_utc(start)
    end_utc = to_utc(end)
    delta = end_utc - start_utc
    return str(delta)


def current_time_utc() -> str:
    """Return the current time in UTC in 24-hour format."""
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def current_time_local() -> str:
    """Return the current local time in 12-hour format."""
    return datetime.now().strftime("%I:%M:%S %p")


def convert_sec_to(convertion_type: Literal["Minutes", "Hours", "Days", "Weeks", "Months", "Years", "Milliseconds"],
                   seconds: int) -> float:
    """Return the number of 'convertion_type' that corresponds to 'seconds'."""
    if convertion_type == "Minutes":
        return seconds / 60
    if convertion_type == "Hours":
        return seconds / 60 / 60
    if convertion_type == "Days":
        return seconds / 60 / 60 / 24
    if convertion_type == "Weeks":
        return seconds / 60 / 60 / 24 / 7
    if convertion_type == "Months":
        return seconds / 60 / 60 / 24 / 30
    if convertion_type == "Years":
        return seconds / 60 / 60 / 24 / 365
    if convertion_type == "Milliseconds":
        return seconds * 1000
    raise ValueError(f"Invalid conversion type: {convertion_type}")


def find_path(node: str, cwd: str = ".") -> Optional[str]:
    """Search for a file 'node' starting from the directory 'cwd'."""
    for root, dirs, files in os.walk(cwd):
        if node in files:
            return os.path.join(root, node)
    return None


def multiprocessing(num_processes: int = 4) -> Callable:
    """
    A decorator to parallelize the execution of a function using multiprocessing.

    Args:
        num_processes (int): Number of processes to use.

    Returns:
        Callable: A decorated function that will be executed in parallel.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: List[Any]) -> List[Any]:
            with py_multiprocessing.Pool(processes=num_processes) as pool:
                result = pool.map(func, args[0])  # 'args[0]' assumes it's iterable for the pool
            return result

        return wrapper

    return decorator


def is_hashable(value: T) -> bool:
    """Check if a value is hashable."""
    try:
        hash(value)
        return True
    except TypeError:
        return False


def is_mutable(value: T) -> bool:
    """Check if a value is mutable."""
    return isinstance(value, (list, dict, set, bytearray))


def profile(func: Callable) -> Callable:
    """Simple profiling wrapper using 'cProfile'."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumtime')
        stats.print_stats()  # You can print or save the stats
        return result

    return wrapper


def timer(func: Callable, per_counter: bool = False):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time_func = time.perf_counter if per_counter else time.time

        start_time = time_func()

        result = func(*args, **kwargs)

        end_time = time_func()

        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.4f} seconds")
        return result

    return wrapper


def debugger(func):
    def wrapper(*args, **kwargs):
        # print the function name and arguments
        print(f"Calling {func.__name__} with args: {args} kwargs: {kwargs}")
        # call the function
        result = func(*args, **kwargs)
        # print the results
        print(f"{func.__name__} returned: {result}")
        return result

    return wrapper


def retry(exception: Type[Exception] = Exception, max_attempts: int = 5, delay: int = 1) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if attempt == max_attempts:
                        print(f"Function failed after {max_attempts} attempts")
                        raise e
                    print(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
                    time.sleep(delay)

        return wrapper

    return decorator


# Exception Handler
def simple_exception(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An exception occurred: {e}")
            raise

    return wrapper


def make_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If the first argument is a function, assume we're being used as a decorator
        if len(args) == 1 and callable(args[0]):
            def decorated(target_func):
                @functools.wraps(target_func)
                def new_func(*func_args, **func_kwargs):
                    return func(target_func, *func_args, **func_kwargs)

                return new_func

            return decorated(args[0])
        else:
            # Otherwise, run the function normally
            return func(*args, **kwargs)

    return wrapper


def memoize(func: Callable[P, T]) -> Callable[P, T]:
    cache: Dict[str, T] = {}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = _generate_cache_key(func, args, kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


# Helper to generate a cache key for memoization
def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    key = (
        f"{func.__name__}({', '.join(map(repr, args))}"
        f"{', ' if args and kwargs else ''}"
        f"{', '.join(f'{k}={v!r}' for k, v in kwargs.items())})"
    )
    return key


def is_decorator(func):
    # Check if the function itself is callable
    if not callable(func):
        return False

    # Define a sample function to pass to the decorator
    sample_func = lambda: None

    # Use `inspect` to get the function signature
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())

    # Check if the function takes exactly one parameter
    if len(parameters) != 1:
        return False

    # The parameter should not have a default value (should always be passed)
    param = parameters[0]
    if param.default != inspect.Parameter.empty:
        return False

    # The parameter should accept a callable (function)
    if param.annotation not in (inspect.Parameter.empty, callable):
        if param.annotation and not callable(param.annotation):
            return False

    # Try calling the function with a sample callable to check if it acts as a decorator
    with contextlib.suppress(Exception):
        result = func(sample_func)
        # If the result is callable, it confirms the function is a decorator
        return callable(result)

    return False


def run_once(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
        return None

    wrapper.has_run = False
    return wrapper

def monitor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logging.info(f"Function {func.__name__} executed successfully in {elapsed_time:.4f} seconds.")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logging.error(f"Function {func.__name__} failed after {elapsed_time:.4f} seconds with error: {e}")
            raise

    return wrapper


def multithreaded(max_workers: int = 5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_args = {executor.submit(func, arg): arg for arg in args[0]}
                return _collect_multithreaded_results(future_to_args)

        return wrapper

    return decorator


# Helper to collect results from multithreaded execution
def _collect_multithreaded_results(future_to_args: dict) -> list:
    results = []
    for future in as_completed(future_to_args):
        arg = future_to_args[future]
        try:
            result = future.result()
        except Exception as exc:
            print(f'{arg} generated an exception: {exc}')
        else:
            results.append(result)
    return results


@contextlib.contextmanager
def ignore_warnings():
    """Context manager to ignore warning within the 'with' statement."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


# Check Internet Connectivity
def check_internet_connectivity(url: str) -> None:
    try:
        protocols = ["https://", "http://"]
        if not any(proto in url for proto in protocols):
            url = "https://" + url
        urlopen(url, timeout=2)
        print(f'Connection to "{url}" is working')
    except URLError as e:
        print(f"Connection error: {e.reason}")
        raise URLError


def is_str_regex(_str: str) -> bool:
    try:
        re.compile(_str)
        return True
    except re.error:
        return False


def singleton(cls):
    __instance = None
    __lock = threading.Lock()

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal __instance
        with __lock:
            if __instance is None:
                __instance = cls(*args, **kwargs)
        return __instance[cls]

    def get_instance():
        return __instance

    cls.get_instance = get_instance
    return wrapper


def copy_dir(src, dst, **kwargs):
    shutil.copytree(src, dst, symlinks=True, copy_function=shutil.copy2, **kwargs)


def copy_file(src, dst):
    shutil.copy(src, dst)


# src A/B/c , # dst X -> X/A/B/c
def copy_dir_to_same_depth(src: PathLike, dst: PathLike, **kwargs):
    _dst = os.path.join(dst, os.path.basename(src))
    os.makedirs(os.path.dirname(_dst), exist_ok=True)
    shutil.copytree(src, _dst, **kwargs)


class SingletonMeta(type):
    """
    A thread-safe implementation of Singleton using metaclasses.
    """
    __instances = {}
    __lock: threading.Lock = threading.Lock()
    __slots__ = ()

    def __call__(cls, *args, **kwargs):
        with cls.__lock:
            if cls not in cls.__instances:
                instance = super().__call__(*args, **kwargs)
                cls.__instances[cls] = instance
        return cls.__instances[cls]

    def get_instance(cls):
        return cls.__instances[cls]

class Singleton(metaclass=SingletonMeta):
    """
    A thread-safe implementation of Singleton class.
    """
    pass

class Password:
    pass

class S:
    def push(self):
        pass
    def __getitem__(self, item):
        pass
    def __contains__(self, item):
        pass
    def __setitem__(self, key, value):
        pass

class Stack:
    def __init__(self, container: Optional[StackProtocol] = None):
        self.__stack = container or deque

class Queue:
    pass

class Checksum:
    def __init__(self, data):
        self.data = data
    def crc32(self):
        zlib.crc32(self.data)
    def crc8(self):
        pass
    def md5(self):
        pass


class ApiChecksum:
    pass


class FilteredDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._filters: List[Callable[[Tuple[Any, Any]], bool]] = []
        self._filtered_cache: Optional[OrderedDict] = None

    def add_filter(self, filter_func: Callable) -> None:
        self._filters.append(filter_func)
        self._invalidate_cache()

    def remove_filter(self, filter_func: Callable[[Tuple[Any, Any]], bool]) -> None:
        try:
            self._filters.remove(filter_func)
            self._invalidate_cache()
        except ValueError:
            raise ValueError("Filter function not found in filters list.")

    def clear_filters(self) -> None:
        self._filters.clear()
        self._invalidate_cache()

    def list_filters(self) -> List[Callable[[Tuple[Any, Any]], bool]]:
        return self._filters.copy()

    def apply_filters(self) -> 'FilteredDict':
        if self._filtered_cache is not None:
            # noinspection PyTypeChecker
            return self._filtered_cache.copy()

        filtered_items: Iterable[Tuple[Any, Any]] = self.items()
        for filter_func in self._filters:
            filtered_items = filter(filter_func, filtered_items)
        self._filtered_cache = FilteredDict(filtered_items)
        return self._filtered_cache.copy()

    @classmethod
    def from_dict(cls, d: dict) -> 'FilteredDict':
        return cls(d)

    def __getitem__(self, key: Any) -> Any:
        if self._filters:
            filtered_dict = self.apply_filters()
            if key in filtered_dict:
                return filtered_dict[key]
            else:
                raise KeyError(key)
        return super().__getitem__(key)

    def get_filtered_items(self) -> List[Tuple[Any, Any]]:
        return list(self.apply_filters().items())

    # noinspection PySameParameterValue
    def add_regex_filter(self, pattern: str, search_in: str = 'key') -> None:
        regex = re.compile(pattern)

        if search_in == 'key':
            self.add_filter(lambda item: regex.search(str(item[0])) is not None)
        elif search_in == 'value':
            self.add_filter(lambda item: regex.search(str(item[1])) is not None)
        else:
            raise ValueError("search_in must be 'key' or 'value'")

    def add_key_filter(self, key_predicate: Callable[[Any], bool]) -> None:
        self.add_filter(lambda item: key_predicate(item[0]))

    def add_value_filter(self, value_predicate: Callable[[Any], bool]) -> None:
        self.add_filter(lambda item: value_predicate(item[1]))

    def update_filters(self, filters: Iterable[Callable[[Tuple[Any, Any]], bool]]) -> None:
        self._filters = list(filters)
        self._invalidate_cache()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()}, filters={self._filters})"

    def _invalidate_cache(self) -> None:
        self._filtered_cache = None

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        self._invalidate_cache()

    def __delitem__(self, key: Any) -> None:
        super().__delitem__(key)
        self._invalidate_cache()


# noinspection PyUnusedName
class MODES(StrEnum):
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


class Environment:
    _mode: MODES = MODES.DEV

    def __init__(self, env_data: EnvPath = ".env"):
        self._env_data = self.__handle_env_path(env_data)
        self.load_env()

    @staticmethod
    def __handle_env_path(env_path: str) -> Union[PathLike, NoReturn]:
        if env_path is None:
            raise EnvError("Invalid .env data.")

        return env_path

    def load_env(self) -> None:
        dotenv.load_dotenv(dotenv_path=self._env_data)

    def read_env(self) -> Dict[str, str]:
        return dotenv.dotenv_values(self._env_data)

    def set_env(self, key: str, value: Any) -> None:
        key.upper()
        dotenv.set_key(self._env_data, key, str(value))
        self.load_env()  # Reload to update the environment

    def get_env(self, key: str) -> Optional[str]:
        return self.read_env().get(key)

    def override_env(self, key: str, value: Any) -> Dict[str, str]:

        env_vars = self.read_env()
        env_vars[key] = str(value)
        return env_vars

    def filter_env(
            self, search_value: str, search_in: Literal["key", "value"] = "key"
    ) -> List[Tuple[str, str]]:
        env_vars = self.read_env()
        if search_in == "key":
            return [(k, v) for k, v in env_vars.items() if search_value in k]
        elif search_in == "value":
            return [(k, v) for k, v in env_vars.items() if search_value in v]
        else:
            raise ValueError("search_in must be either 'key' or 'value'")

    def filter_with_predicate(
            self, predicate: Callable[[str, str], bool]
    ) -> List[Tuple[str, str]]:
        env_vars = self.read_env()
        return [(k, v) for k, v in env_vars.items() if predicate(k, v)]

    def mode(self, func_mode: MODES = MODES.TEST):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self._mode == func_mode:
                    return func(*args, **kwargs)
                return None

            return wrapper

        return decorator

    @classmethod
    def from_json(cls, json_path: PathLike) -> 'Environment':
        with open(json_path, 'r') as f:
            data = json.load(f)

        env = cls(env_data=json_path)

        for key, value in data.items():
            env.set_env(key, value)

        return env

    @classmethod
    def from_dict(cls, env_dict: Dict[str, Any]) -> 'Environment':
        """Create an Environment instance from a dictionary of environment variables."""
        env = cls()  # Initialize with a default env path

        for key, value in env_dict.items():
            env.set_env(key, value)

        return env

    @classmethod
    def from_config(cls, config_path: PathLike) -> 'Environment':
        config = configparser.ConfigParser()
        config.read(config_path)
        env = cls(env_data=config_path)

        # Handle both the DEFAULT section and other sections
        for section in config.sections():
            for key, value in config.items(section):
                env.set_env(key.upper(), value)

        # Also, load the DEFAULT section explicitly
        for key, value in config['DEFAULT'].items():
            env.set_env(key.upper(), value)

        return env

    def __repr__(self) -> str:
        env_vars = self.read_env()
        return (
            f"{self.__class__.__name__}(mode={self._mode}, env_path={self._env_data}, "
            f"vars={env_vars})"
        )
