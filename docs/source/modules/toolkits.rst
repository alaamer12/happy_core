Toolkits Module
===============

The toolkits module provides a comprehensive collection of utility functions, decorators, and context managers designed to enhance Python applications with robust functionality for debugging, profiling, caching, logging, multithreading, and more.

Key Features
------------

* Console Output Control
* Type Checking Utilities
* Decorators for Various Purposes
* Context Managers
* Multithreading Utilities
* Network Connectivity Tools
* Singleton Pattern Implementation
* Pointer and Memory Management
* Constants Management
* Deferred Value Processing

Console Output Control
----------------------

.. py:function:: stop_console_printing(include_stderr: bool = False) -> None

   Redirects standard output (and optionally standard error) to null device.

   :param include_stderr: If True, also redirects stderr to null device
   :type include_stderr: bool
   :raises UserWarning: If include_stderr is True

.. py:function:: start_console_printing() -> None

   Restores standard output and standard error to their original values.

.. py:function:: stop_print() -> None

   Replaces the built-in print function with an empty function.

.. py:function:: start_print() -> None

   Restores the built-in print function to its original state.

Type Checking Utilities
-----------------------

.. py:function:: is_iterable(x: Any) -> bool

   Checks if an object is iterable.

.. py:function:: is_iterator(x: Any) -> bool

   Checks if an object is an iterator.

.. py:function:: is_generator(x: Any) -> bool

   Checks if an object is a generator.

.. py:function:: is_hashable(value: T) -> bool

   Checks if a value is hashable.

.. py:function:: is_mutable(value: T) -> bool

   Checks if a value is mutable.

Decorators
----------

.. py:function:: trace(func: Callable[..., T]) -> Callable[..., T]

   A decorator that traces function calls and their results.

.. py:function:: profile(func: Callable) -> Callable

   Simple profiling wrapper using 'cProfile'.

.. py:function:: simple_debugger(func: Callable) -> Callable

   A decorator that provides simple debugging capabilities.

.. py:function:: retry(exception: Type[Exception] = Exception, max_attempts: int = 5, delay: float = 1.0) -> Callable
  :no-index:

   A decorator that retries a function execution upon specified exception.

   :param exception: The exception type to catch and retry on
   :param max_attempts: Maximum number of retry attempts
   :param delay: Delay in seconds between retries

.. py:function:: simple_exception(func: Callable) -> Callable

   A decorator that provides simple exception handling and logging.

.. py:function:: memoize(func: Callable[P, T]) -> Callable[P, T]

   Caches the results of function calls based on input arguments.

.. py:function:: run_once(func: Callable) -> Callable

   Ensures a function is executed only once.

.. py:function:: monitor(func: Callable) -> Callable
  :no-index:

   Monitors and logs function execution time and status.

.. py:function:: multithreaded(max_workers: int = 5) -> Callable

   Executes a function in multiple threads.

   :param max_workers: Maximum number of worker threads

.. py:function:: singleton(cls: Type[T]) -> Type[T]

   Decorator that implements the singleton pattern.

Context Managers
----------------

.. py:function:: log_level(level: int, name: str) -> ContextManager[logging.Logger]

   Temporarily changes the logging level of a logger within a context.

   :param level: The logging level to set
   :param name: The name of the logger
   :yields: The logger with the temporarily changed level

.. py:function:: ignore_warnings() -> ContextManager[None]

   Context manager to temporarily suppress all warnings.

Utility Functions
-----------------

.. py:function:: get_module_size(module: Any) -> int

   Calculates the approximate memory size of a module.

.. py:function:: find_path(node: str, cwd: str = ".") -> Optional[str]

   Search for a file 'node' starting from the directory 'cwd'.

.. py:function:: check_internet_connectivity(url: str) -> None

   Checks if there is an active internet connection to the specified URL.

   :param url: The URL to check connectivity against
   :raises URLError: If connection cannot be established

Classes
-------

Constants
~~~~~~~~~

.. py:class:: Constants

   A class for creating immutable constant objects.

   .. py:method:: from_dict(**kwargs) -> Constants
      :classmethod:

      Create a Constants instance from a dictionary.

   .. py:method:: from_nonmapping_iterable(iterable: Iterable[Tuple[str, Any]]) -> Constants
      :classmethod:

      Create a Constants instance from an iterable of key-value pairs.

DeferredValue
~~~~~~~~~~~~~

.. py:class:: DeferredValue

   A class that defers the evaluation of a value and provides a way to access the deferred value.
   The update interval is dynamically calculated based on CPU frequency.

   .. py:method:: set(value: Any) -> None

      Sets the value to be deferred.

   .. py:method:: get() -> Any

      Returns the deferred value.

UnifiedOperation
~~~~~~~~~~~~~~~~

.. py:class:: UnifiedOperation

   A descriptor that handles both sync and async operations transparently.
   The actual implementation is chosen based on the caller's context.

   .. py:method:: create_unified_operation(sync_fn: Callable[P, R], async_fn: Callable[P, Awaitable[R]]) -> UnifiedOperation
      :staticmethod:

      Helper method to create unified operations with proper type hints.

Examples
--------

Console Output Control::

    # Suppress all console output
    stop_console_printing()
    print("This won't be displayed")
    start_console_printing()
    print("This will be displayed")

Type Checking::

    assert is_iterable([1, 2, 3]) == True
    assert is_iterator(iter([1, 2, 3])) == True
    assert is_generator((x for x in range(3))) == True

Decorators::

    @retry(exception=ValueError, max_attempts=3)
    def may_fail():
        # Function that might raise ValueError

    @memoize
    def expensive_computation(x):
        # Results will be cached based on input x

    @singleton
    class DatabaseConnection:
        # Only one instance will ever be created

Context Managers::

    with log_level(logging.DEBUG, "my_logger"):
        # Temporarily increase logging detail
        logger.debug("Detailed information")

    with ignore_warnings():
        # Warnings will be suppressed in this block
        warnings.warn("This warning is suppressed")

Constants and Pointers::

    # Create immutable constants
    config = Constants.from_dict(
        HOST="localhost",
        PORT=8080,
        DEBUG=True
    )

Deferred Values::

    # Create a deferred value that updates based on CPU frequency
    dv = DeferredValue(initial_value=100)
    dv.set(200)  # Update will be deferred
    current_value = dv.get()  # Get the current value

Notes
-----

- All decorators can be used with or without arguments thanks to the :func:`make_decorator` utility.
- The module is designed with type safety in mind and includes comprehensive type hints.
- Memory management utilities like :class:`DeferredValue` provide fine-grained control when needed.
- Thread safety is ensured in relevant components through proper locking mechanisms.