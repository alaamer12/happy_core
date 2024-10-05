import cProfile
import contextlib
import functools
import inspect
import logging
import pstats
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Any, List, Dict, ParamSpec, Type, TypeVar, Optional
from urllib.error import URLError
from urllib.request import urlopen
from multiprocessing import Pool
from functools import wraps
import os

T = TypeVar("T")

P = ParamSpec("P")


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
            with Pool(processes=num_processes) as pool:
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
    return isinstance(value, (list, dict, set, bytearray))  # Common mutable types


###############################

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


def timer(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs)

        execution_time = time.time() - start_time
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


def create_exception(message: str, config: dict) -> Type[Exception]:
    # Extract details from the config
    exception_name = config.get("name", "CustomException")
    base_classes = (Exception,)  # Base class for the exception (can be modified if needed)

    # Define any custom attributes (default to None if not provided)
    custom_attributes = config.get("attributes", {})

    # Define a custom __init__ method to initialize the exception with dynamic attributes
    def custom_init(self, _message):
        super().__init__(_message)
        # Dynamically add attributes to the exception
        for attr_name, attr_value in custom_attributes.items():
            setattr(self, attr_name, attr_value)

    # Define a custom __str__ method if provided in the config, else fallback to default behavior
    if "custom_str" in config:
        custom_str_method = lambda self: config["custom_str"].format(**custom_attributes)
    else:
        custom_str_method = Exception.__str__

    # Dynamically create the exception class
    exception_class = type(
        exception_name,  # Name of the class
        base_classes,  # Base class (can be more than one)
        {
            "__init__": custom_init,
            "__str__": custom_str_method
        }
    )

    # Return an instance of the dynamically created exception class
    return exception_class(message)


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


def multithreaded(max_workers: int = 5) -> Callable:
    def decorator(func: Callable) -> Callable:
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
    """Context manager to ignore warning within the with statement."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


d_ignore_warnings = make_decorator(ignore_warnings)


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

