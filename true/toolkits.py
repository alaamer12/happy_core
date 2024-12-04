"""
Module for utility functions, decorators, and context managers.

This module provides a variety of utility functions and decorators aimed at enhancing
the robustness, flexibility, and functionality of Python applications. It includes
tools for debugging, profiling, caching, managing logging levels, multithreading,
singleton pattern implementation, exception handling, and more.

Key functionalities:
- Console Output Control: Functions to enable or suppress console output.
- Type Checkers: Functions to check types such as iterables, iterators, and generators.
- Decorators: Includes decorators for retrying functions, exception handling,
  profiling, caching (memoization), singleton pattern, and execution limiting.
- Context Managers: Tools for temporarily changing log levels and suppressing warnings.
- Multithreading: Utilities for running functions concurrently with thread pools.
- Network Check: Function to verify internet connectivity by attempting to reach a URL.

The module also includes examples of custom exception classes for advanced error handling
and a Singleton metaclass for enforcing single-instance patterns.

Typical Use Cases:
- Utility for various data type checks and manipulations.
- Application performance profiling and debugging.
- Enhanced logging control for modules that require temporary or dynamic logging levels.
- Simplified multithreading operations with thread pool management.
- Network connectivity validation within the application.

Example:
    ```
    # Suppress console printing
    stop_console_printing()

    # Enable profiling on a function
    @profile
    def compute():
        pass
    ```

This module is especially useful for developers needing optimized control over
debugging, performance measurement, and singleton enforcement.
"""

from __future__ import annotations

import asyncio
import builtins
import cProfile
import contextlib
import functools
import importlib
import inspect
import logging
import os
import pstats
import sys
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import wraps
from operator import pow, add, sub, truediv, floordiv, mod, mul
from threading import Thread, Lock
from typing import Optional, Dict, Any, ContextManager, Tuple
from typing import ParamSpec
from typing import (Type, Iterable, Iterator, Generator, Never)
from typing import TypeVar, Generic, Callable, Awaitable, Union, Coroutine
from urllib.error import URLError
from urllib.request import urlopen

import psutil

from .exceptions import BreakerThresholdError, UnificationError

T = TypeVar("T")
R = TypeVar('R')
P = ParamSpec("P")

__all__ = [
    # Public Classes
    'SingletonMeta',  # Thread-safe singleton metaclass
    'UnifiedOperation',  # Descriptor for sync/async operations
    'DynamicUnifiedOperation',  # Dynamic unified operations holder
    'Constants',  # Constants container class
    'Pointer',  # Reference pointer implementation
    'DeferredValue',  # Deferred value evaluation
    'FixIDEComplain',  # IDE complaint fixer mixin

    # Public Functions
    # Console Control
    'stop_console_printing',
    'start_console_printing',
    'stop_print',
    'start_print',

    # Type Checking
    'is_iterable',
    'is_iterator',
    'is_generator',
    'is_hashable',
    'is_mutable',
    'is_decorator',

    # Utility Functions
    'safe_import',
    'find_path',
    'get_module_size',
    'check_internet_connectivity',
    'null_decorator',
    'make_decorator',

    # Decorators
    'trace',
    'profile',
    'retry',
    'monitor',
    'memoize',
    'singleton',
    'breaker',
    'safe_arithmetic',
    'multithreaded',
    'run_once',
    'simple_exception',
    'raised_exception',
    'arithmatic_total_ordering',

    # Context Managers
    'log_level',
    'ignore_warnings',

    # Operation Creation
    'create_unified_operation',
]


def __dir__():
    """Return a sorted list of names in this module."""
    return sorted(__all__)


def stop_console_printing(include_stderr: bool = False) -> None:
    """
    Redirects standard output (and optionally standard error) to null device.

    Args:
        include_stderr (bool): If True, also redirects stderr to null device. Defaults to False.

    Warns:
        UserWarning: If include_stderr is True, warns about potential risks.
    """
    if include_stderr:
        warnings.warn("This is not recommended. Please use this on your own risk.", stacklevel=2)
        sys.stderr = open(os.devnull, 'w')
    sys.stdout = open(os.devnull, 'w')


def start_console_printing() -> None:
    """
    Restores standard output and standard error to their original values.
    """
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def safe_import(module_name: str) -> Optional[Any]:
    """
    Safely imports a module without raising ImportError if the module doesn't exist.

    Args:
        module_name (str): Name of the module to import.
    Returns:
        Optional[Any]: The imported module if successful, None otherwise.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def is_iterable(x: Any) -> bool:
    """
    Checks if an object is iterable.

    Args:
        x (Any): Object to check.

    Returns:
        bool: True if object is iterable, False otherwise.
    """
    return isinstance(x, Iterable)


def is_iterator(x: Any) -> bool:
    """
    Checks if an object is an iterator.

    Args:
        x (Any): Object to check.

    Returns:
        bool: True if object is an iterator, False otherwise.
    """
    return isinstance(x, Iterator)


def is_generator(x: Any) -> bool:
    """
    Checks if an object is a generator.

    Args:
        x (Any): Object to check.

    Returns:
        bool: True if object is a generator, False otherwise.
    """
    return isinstance(x, Generator)


# noinspection PyUnusedLocal
def empty_function(func: Never) -> None:
    """
    A function that does nothing.
    """
    pass


def stop_print() -> None:
    """
    Replaces the built-in print function with an empty function.
    """
    builtins.print = empty_function


def start_print() -> None:
    """
    Restores the built-in print function to its original state.
    """
    builtins.print = print


def null_decorator() -> None:
    """
    A decorator that returns None.

    Returns:
        None
    """
    return None


@contextlib.contextmanager
def log_level(level: int, name: str) -> ContextManager[logging.Logger]:
    """
    Temporarily changes the logging level of a logger within a context.

    Args:
        level (int): The logging level to set.
        name (str): The name of the logger.
    Yields:
        logging.Logger: The logger with the temporarily changed level.
    """
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)


def trace(func: Callable[..., T]) -> Callable[..., T]:
    """
    A decorator that traces function calls and their results.

    Args:
        func (Callable): The function to trace.

    Returns:
        Callable: The wrapped function that prints trace information.
    """
    functools.wraps(func)

    def wrapper(*args: Any, **kwargs: Any) -> T:
        result = func(*args, **kwargs)
        print(f'{func.__name__}({args!r}, {kwargs!r}) ' f'-> {result!r}')
        return result

    return wrapper


def get_module_size(module: Any) -> int:
    """
    Calculates the approximate memory size of a module.

    Args:
        module (Any): The module to measure.

    Returns:
        int: The approximate size in bytes.
    """
    size = 0
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        size += sys.getsizeof(attr)
    return size


def raised_exception(exception: Type[Exception]) -> Callable:
    """
    A decorator that transforms any exception from the decorated function into the specified exception type.

    Args:
        exception: The exception type to raise

    Returns:
        Callable: A decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise exception from e

        return wrapper

    return decorator


def find_path(node: str, cwd: str = ".") -> Optional[str]:
    """Search for a file 'node' starting from the directory 'cwd'."""
    for root, dirs, files in os.walk(cwd):
        if node in files:
            return os.path.join(root, node)
    return None


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


# noinspection PySameParameterValue
def simple_debugger(func):
    def wrapper(*args, **kwargs):
        # print the function name and arguments
        print(f"Calling {func.__name__} with args: {args} kwargs: {kwargs}")
        # call the function
        result = func(*args, **kwargs)
        # print the results
        print(f"{func.__name__} returned: {result}")
        return result

    return wrapper


def retry(exception: Type[Exception] = Exception, max_attempts: int = 5, delay: float = 1.0) -> Callable:
    """
    A decorator that retries a function execution upon specified exception.

    Args:
        exception: The exception type to catch and retry on
        max_attempts: Maximum number of retry attempts
        delay: Delay in seconds between retries

    Returns:
        Callable: Decorated function that implements retry logic
    """

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


def simple_exception(func: Callable) -> Callable:
    """
    A decorator that provides simple exception handling and logging.

    Args:
        func: The function to be decorated

    Returns:
        Callable: Decorated function with exception handling
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An exception occurred: {e}")
            raise

    return wrapper


def make_decorator(func: Callable) -> Callable:
    """
    Creates a decorator that can be used both with and without arguments.

    Args:
        func: The function to be converted into a decorator

    Returns:
        Callable: A decorator that can handle both forms of decoration
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            def decorated(target_func):
                @functools.wraps(target_func)
                def new_func(*func_args, **func_kwargs):
                    return func(target_func, *func_args, **func_kwargs)

                return new_func

            return decorated(args[0])
        else:
            return func(*args, **kwargs)

    return wrapper


def memoize(func: Callable[P, T]) -> Callable[P, T]:
    """
    Caches the results of function calls based on input arguments.

    Args:
        func: The function whose results should be cached

    Returns:
        Callable: Decorated function with memoization
    """
    cache: Dict[str, T] = {}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = _generate_cache_key(func, args, kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    key = (
        f"{func.__name__}({', '.join(map(repr, args))}"
        f"{', ' if args and kwargs else ''}"
        f"{', '.join(f'{k}={v!r}' for k, v in kwargs.items())})"
    )
    return key


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


def is_decorator(func: Callable) -> bool:
    """
    Determines if a given function is a decorator.

    Args:
        func: The function to check

    Returns:
        bool: True if the function is a decorator, False otherwise
    """
    if not callable(func):
        return False

    sample_func = lambda: None
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())

    if len(parameters) != 1:
        return False

    param = parameters[0]
    if param.default != inspect.Parameter.empty:
        return False

    if param.annotation not in (inspect.Parameter.empty, callable):
        if param.annotation and not callable(param.annotation):
            return False

    with contextlib.suppress(Exception):
        result = func(sample_func)
        return callable(result)

    return False


def run_once(func: Callable) -> Callable:
    """
    Ensures a function is executed only once.

    Args:
        func: The function to be executed once

    Returns:
        Callable: Decorated function that runs only once
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
        return None

    wrapper.has_run = False
    return wrapper


def monitor(func: Callable) -> Callable:
    """
    Monitors and logs function execution time and status.

    Args:
        func: The function to be monitored

    Returns:
        Callable: Decorated function with monitoring capabilities
    """

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


def multithreaded(max_workers: int = 5) -> Callable:
    """
    Executes a function in multiple threads.

    Args:
        max_workers: Maximum number of worker threads

    Returns:
        Callable: Decorator that enables multithreaded execution
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_args = {executor.submit(func, arg): arg for arg in args[0]}
                return _collect_multithreaded_results(future_to_args)

        return wrapper

    return decorator


@contextlib.contextmanager
def ignore_warnings() -> None:
    """
    Context manager to temporarily suppress all warnings.

    Yields:
        None
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


def check_internet_connectivity(url: str) -> None:
    """
    Checks if there is an active internet connection to the specified URL.
    Args:
        url: The URL to check connectivity against

    Raises:
        URLError: If connection cannot be established
    """
    try:
        protocols = ["https://", "http://"]
        if not any(proto in url for proto in protocols):
            url = "https://" + url
        urlopen(url, timeout=2)
        print(f'Connection to "{url}" is working')
    except URLError as e:
        raise URLError(f"Connection error: {e.reason}")


def singleton(cls: Type[T]) -> Type[T]:
    """
    Decorator that implements the singleton pattern.

    Args:
        cls: The class to make singleton

    Returns:
        Type[T]: Singleton class
    """
    __instance = None
    __lock = threading.Lock()

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal __instance
        with __lock:
            if __instance is None:
                __instance = cls(*args, **kwargs)
        return __instance

    return wrapper


# Breaker Decorator
def breaker(threshold):
    """A decorator that breaks a function once a specified threshold is reached (e.g., number of calls)."""

    def decorator(func):
        func.counter = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            if func.counter >= threshold:
                raise BreakerThresholdError(f"Function '{func.__name__}' reached the threshold of {threshold} calls")

            result = func(*args, **kwargs)
            func.counter += 1
            return result

        return wrapper

    return decorator


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

    @property
    def instance(cls):
        return cls.__instances[cls]


def safe_arithmetic(func):
    """Simple decorator to handle ArithmeticError exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ArithmeticError:
            return NotImplemented

    return wrapper


@safe_arithmetic
def _do_arithmatic(self, other, op, derived_op):
    op_result = getattr(type(self), derived_op)(self, other)
    if op_result is NotImplemented:
        return op_result
    return op(self.value, other.value)


class FixIDEComplain:
    """A mixin class to fix IDE complaints about dynamically added methods, with on-demand generation."""

    def __getattr__(self, name):
        """Generate missing operators dynamically."""
        if name in _convert:
            # Generate the dynamic method on-the-fly using the _convert dictionary
            for opname, opfunc in _convert[name]:
                setattr(self, opname, opfunc)
            # Once generated, return the first operation function
            return getattr(self, name)
        raise AttributeError(f"{type(self).__name__} object has no attribute '{name}'")


def _sub_from_add(self, other):
    return _do_arithmatic(self, other, sub, '__add__')


def _floordiv_from_add(self, other):
    return _do_arithmatic(self, other, floordiv, '__add__')


def _truediv_from_add(self, other):
    return _do_arithmatic(self, other, truediv, '__add__')


def _mul_from_add(self, other):
    return _do_arithmatic(self, other, mul, '__add__')


def _mod_from_add(self, other):
    return _do_arithmatic(self, other, mod, '__add__')


def _pow_from_add(self, other):
    return _do_arithmatic(self, other, pow, '__add__')


def _iadd_from_add(self, other):
    result = self + other
    if result is NotImplemented:
        return NotImplemented
    self.value = result.value
    return self


def _radd_from_add(self, other):
    return type(self)(other + self.value)


def _floordiv_from_truediv(self, other):
    return _do_arithmatic(self, other, floordiv, '__truediv__')


def _add_from_truediv(self, other):
    return _do_arithmatic(self, other, add, '__truediv__')


def _mul_from_truediv(self, other):
    return _do_arithmatic(self, other, mul, '__truediv__')


def _mod_from_truediv(self, other):
    return _do_arithmatic(self, other, mod, '__truediv__')


def _pow_from_truediv(self, other):
    return _do_arithmatic(self, other, pow, '__truediv__')


def _sub_from_truediv(self, other):
    return _do_arithmatic(self, other, sub, '__truediv__')


def _itruediv_from_truediv(self, other):
    op_result = type(self).__truediv__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value /= op_result
    return self


def _rtruediv_from_truediv(self, other):
    return type(self)(other / self.value)


def _add_from_sub(self, other):
    return _do_arithmatic(self, other, add, '__sub__')


def _mul_from_sub(self, other):
    return _do_arithmatic(self, other, mul, '__sub__')


def _truediv_from_sub(self, other):
    return _do_arithmatic(self, other, truediv, '__sub__')


def _floordiv_from_sub(self, other):
    return _do_arithmatic(self, other, floordiv, '__sub__')


def _mod_from_sub(self, other):
    return _do_arithmatic(self, other, mod, '__sub__')


def _pow_from_sub(self, other):
    return _do_arithmatic(self, other, pow, '__sub__')


def _isub_from_sub(self, other):
    op_result = type(self).__sub__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value -= op_result
    return self


def _rsub_from_sub(self, other):
    return type(self)(other - self.value)


def _add_from_mul(self, other):
    return _do_arithmatic(self, other, add, '__mul__')


def _truediv_from_mul(self, other):
    return _do_arithmatic(self, other, truediv, '__mul__')


def _sub_from_mul(self, other):
    return _do_arithmatic(self, other, sub, '__mul__')


def _pow_from_mul(self, other):
    return _do_arithmatic(self, other, pow, '__mul__')


def _floordiv_from_mul(self, other):
    return _do_arithmatic(self, other, floordiv, '__mul__')


def _mod_from_mul(self, other):
    return _do_arithmatic(self, other, mod, '__mul__')


def _imul_from_mul(self, other):
    op_result = type(self).__mul__(self, other)
    if op_result is NotImplemented:
        return NotImplemented
    self.value *= op_result
    return self


def _rmul_from_mul(self, other):
    return type(self)(other + self.value)


_convert = {
    '__add__': [
        ('__sub__', _sub_from_add),
        ('__iadd__', _iadd_from_add),
        ('__radd__', _radd_from_add),
        ('__mul__', _mul_from_add),
        ('__truediv__', _truediv_from_add),
        ('__floordiv__', _floordiv_from_add),
        ('__mod__', _mod_from_add),
        ('__pow__', _pow_from_add)
    ],
    '__sub__': [
        ('__add__', _add_from_sub),
        ('__isub__', _isub_from_sub),
        ('__radd__', _rsub_from_sub),
        ('__mul__', _mul_from_sub),
        ('__truediv__', _truediv_from_sub),
        ('__floordiv__', _floordiv_from_sub),
        ('__mod__', _mod_from_sub),
        ('__pow__', _pow_from_sub)
    ],
    '__mul__': [
        ('__add__', _add_from_mul),
        ('__sub__', _sub_from_mul),
        ('__imul__', _imul_from_mul),
        ('__rmul__', _rmul_from_mul),
        ('__truediv__', _truediv_from_mul),
        ('__floordiv__', _floordiv_from_mul),
        ('__mod__', _mod_from_mul),
        ('__pow__', _pow_from_mul)
    ],
    '__truediv__': [
        ('__add__', _add_from_truediv),
        ('__sub__', _sub_from_truediv),
        ('__floordiv__', _floordiv_from_truediv),
        ('__mul__', _mul_from_truediv),
        ('__itruediv__', _itruediv_from_truediv),
        ('__rtruediv__', _rtruediv_from_truediv),
        ('__mod__', _mod_from_truediv),
        ('__pow__', _pow_from_truediv)
    ],
    # ...
}


def arithmatic_total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    # Find which ordering operation(s) are defined
    roots = {op for op in _convert if getattr(cls, op, None) is not getattr(object, op, None)}
    if not roots:
        raise ValueError('must define at least one ordering operation: + - * /')

    # Add all related operations based on defined ones
    for root in roots:
        for opname, opfunc in _convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                setattr(cls, opname, opfunc)
    return cls


class UnifiedOperation(Generic[P, R]):
    """
    A descriptor that handles both sync and async operations transparently.
    The actual implementation is chosen based on the caller's context.
    """

    def __init__(
            self,
            sync_impl: Callable[P, R],
            async_impl: Callable[P, Awaitable[R]]
    ):
        self.sync_impl = sync_impl
        self.async_impl = async_impl

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        @wraps(self.sync_impl)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[R, Awaitable[R]]:
            # Check if we're in an async context
            try:
                asyncio.get_running_loop()
                is_async = True
            except RuntimeError:
                is_async = False

            if is_async:
                return self.async_impl(*args, **kwargs)
            return self.sync_impl(*args, **kwargs)

        return wrapper

    def __call__(self, *args, **kwargs):
        raise UnificationError("Cant unify dynamic methods, have you inherited from 'DynamicUnifiedOperation'")

    def __await__(self):
        raise UnificationError("Cant unify dynamic methods, have you inherited from 'DynamicUnifiedOperation'")


class DynamicUnifiedOperation:
    """A class to hold dynamically created unified operations"""

    def __init__(self):
        self._operations = {}

    def __setattr__(self, name: str, value: UnifiedOperation):
        if isinstance(value, UnifiedOperation):
            # Store the operation's implementation
            self._operations[name] = value.__get__(self)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str):
        if name in getattr(self, '_operations', {}):
            return self._operations[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def create_unified_operation(
        sync_fn: Callable[P, R],
        async_fn: Callable[P, Awaitable[R]]
) -> UnifiedOperation[P, R]:
    """
    Helper method to create unified operations with proper type hints
    """
    if not (isinstance(sync_fn, Callable) and isinstance(async_fn, Callable)) or isinstance(async_fn, Coroutine):
        raise ValueError("Both sync_fn and async_fn must be callable, and async_fn must be a coroutine function")
    return UnifiedOperation(sync_fn, async_fn)


@functools.total_ordering
@dataclass(frozen=True, kw_only=True, order=False)
class Constants:
    def __init__(self, **kwargs):
        self.__initialize_constants(**kwargs)

    def __initialize_constants(self, **kwargs):
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Constants) and self.__dict__ == other.__dict__

    def __lt__(self, other):
        if not isinstance(other, Constants):
            return NotImplemented
        return tuple(sorted(self.__dict__.items())) < tuple(sorted(other.__dict__.items()))

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def from_nonmapping_iterable(cls, iterable: Iterable[Tuple[str, Any]]):
        if not isinstance(iterable, Iterable) or isinstance(iterable, dict):
            raise TypeError(f"Expected a non-mapping iterable, got {type(iterable)}")

        if not all(isinstance(item, tuple) for item in iterable):
            raise TypeError("All items in iterable must be tuples")

        return cls(**dict(iterable))


@functools.total_ordering
class Pointer:
    def __init__(self, value=None):
        """Initialize the pointer with a value."""
        self._value = [value]  # Use a list to hold the reference

    @property
    def value(self):
        return self.get()

    def get(self):
        """Dereference the pointer to access the value."""
        return self._value[0]

    def set(self, value):
        """Dereference the pointer and set the new value."""
        self._value[0] = value

    def address(self):
        """Return the 'address' of the pointer, which in this case is its own id."""
        return id(self._value)

    def point_to(self, other_pointer):
        """Point this pointer to the memory location of another pointer."""
        if isinstance(other_pointer, Pointer):
            self._value = other_pointer._value
        else:
            raise TypeError("point_to expects another Pointer instance")

    def is_null(self):
        """Check if the pointer is null (i.e., points to None)."""
        return self._value[0] is None

    def __str__(self):
        """String representation showing the value and the 'address'."""
        return f"{self.__class__.__name__}(value={self._value[0]}, address={self.address()})"

    def __repr__(self):
        return self.__str__()

    def __del__(self):
        self._value[0] = None

    def __lt__(self, other):
        if not isinstance(other, Pointer):
            return NotImplemented
        return self.get() < other.get()


class DeferredValue:
    """
    A class that defers the evaluation of a value and provides a way to access the deferred value.
    The update interval is dynamically calculated based on CPU frequency.
    """

    def __init__(self, value, bias=0.05, update_interval_func=None, final_return: bool = False):
        """
        Initializes the DeferredValue object.

        Args:
            value (any): The value to be deferred.
            update_interval_func (function, optional): A function to dynamically calculate the update interval.
                                                      Defaults to None, which uses a fixed interval.
        """
        self.final_return = final_return
        self.bias = bias
        self._value = value
        self._deferred_value = value
        self._lock = Lock()
        self._update_thread = None

        # Store the update_interval_func instead of the result
        self._update_interval_func: Callable[..., float] = update_interval_func or self._default_update_interval
        self._start_update_thread()

    def _default_update_interval(self):
        """
        Default method to return the update interval based on CPU power.
        You can modify this to return a different value or use a more complex calculation.
        """
        cpu_freq = psutil.cpu_freq(percpu=True)
        avg_freq = sum(core.current for core in cpu_freq) / len(cpu_freq) if cpu_freq else 0
        # Calculate interval and ensure it's not negative
        interval = max(0.1, 1 / (avg_freq / 1000) - self.bias)
        return interval

    def _start_update_thread(self):
        """
        Starts the thread responsible for updating the deferred value.
        """
        self._update_thread = Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

    def _update_loop(self):
        """
        The loop that updates the deferred value at the dynamically calculated interval.
        """
        while True:
            update_interval = self._update_interval_func()  # Get the update interval dynamically
            with self._lock:
                self._deferred_value = self._value
            time.sleep(update_interval)

    def set(self, value):
        """
        Sets the value to be deferred.

        Args:
            value (any): The new value to be deferred.
        """
        with self._lock:
            self._value = value

    def get(self):
        """
        Returns the deferred value.

        Returns:
            any: The deferred value.
        """
        with self._lock:
            # Return the deferred value without modifying the bias here
            return self._deferred_value

    def __repr__(self):
        """
        Returns a string representation of the DeferredValue object.
        """
        return f"DeferredValue(value={self._value}, deferred_value={self._deferred_value})"

    @staticmethod
    def _validate_interval(func: Union[Callable, float]):
        """
        Ensures the interval function is valid.
        """
        if callable(func):
            interval = func()  # Call the function to get the interval
        else:
            interval = func

        # Validate the interval
        if interval is None or interval <= 0 or interval > 2:
            return 0.1  # Default interval if invalid
        return interval

# if __name__ == "__main__":
#     # Create a DeferredValue instance with dynamic update interval based on CPU frequency
#     dv = DeferredValue(value=100)
#
#     # Set a new value
#     dv.set(200)
#     dv.set(300)
#     dv.set(400)
#     dv.set(500)
#     dv.set(600)
#
#     # Get the deferred value
#     print(dv.get())  # Output: 100 (initially, the deferred value is the same as the original value)
#
#     # Wait for a few update cycles
#     # time.sleep(1)
#
#     # Get the deferred value again
#     print(dv.get())  # Output: 200 (the deferred value has been updated)
