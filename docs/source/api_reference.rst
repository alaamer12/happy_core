API Reference
=============

This section provides detailed documentation for all public APIs in Happy Core.

Collections Module
----------------

File
~~~~

.. py:class:: File

   A high-level wrapper for file operations with built-in error handling and type safety.

   .. py:method:: __init__(path: str)
      
      Initialize a new File instance.

      :param path: Path to the file

   .. py:method:: read_text(encoding: str = 'utf-8') -> str
      
      Read the file contents as text.

      :param encoding: Text encoding to use
      :return: File contents as string

   .. py:method:: write_text(content: str, encoding: str = 'utf-8') -> None
      
      Write text content to the file.

      :param content: Text to write
      :param encoding: Text encoding to use

   .. py:method:: read_json() -> JsonDict
      
      Read and parse JSON file contents.

      :return: Parsed JSON data as dictionary

Directory
~~~~~~~~

.. py:class:: Directory

   A high-level wrapper for directory operations.

   .. py:method:: __init__(path: str)
      
      Initialize a new Directory instance.

      :param path: Path to the directory

   .. py:method:: create(exist_ok: bool = True) -> None
      
      Create the directory.

      :param exist_ok: If True, don't raise error if directory exists

Time Module
----------

TimeUtils
~~~~~~~~

.. py:class:: TimeUtils

   Utility class for time-related operations.

   .. py:classmethod:: now() -> datetime
      
      Get current timestamp.

      :return: Current datetime

   .. py:classmethod:: format_iso(dt: datetime) -> str
      
      Format datetime in ISO format.

      :param dt: Datetime to format
      :return: Formatted string

Scheduler
~~~~~~~~

.. py:class:: Scheduler

   Task scheduling utility.

   .. py:method:: schedule(task_func: Callable, run_at: datetime, **kwargs) -> str
      
      Schedule a task for future execution.

      :param task_func: Function to execute
      :param run_at: When to execute the task
      :return: Task ID

Toolkits Module
-------------

Decorators
~~~~~~~~~

.. py:decorator:: retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0)
   
   Retry a function on failure.

   :param max_attempts: Maximum number of retry attempts
   :param delay: Initial delay between retries in seconds
   :param backoff: Multiplier for delay after each retry

.. py:decorator:: monitor
   
   Monitor function execution time and resources.

.. py:decorator:: cache(ttl: int = 3600)
   
   Cache function results.

   :param ttl: Time to live for cached results in seconds

Types Module
----------

.. py:class:: JsonDict
   
   Type alias for JSON-compatible dictionary.

   .. code-block:: python

      JsonDict = Dict[str, Union[str, int, float, bool, None, List, Dict]]

Error Handling
------------

.. py:exception:: HappyCoreError
   
   Base exception class for Happy Core.

.. py:exception:: FileError
   
   Raised for file operation errors.

.. py:exception:: ValidationError
   
   Raised for data validation errors.

Best Practices
------------

When using Happy Core's API, consider these best practices:

1. **Error Handling**
   
   Always handle potential exceptions:

   .. code-block:: python

      try:
          file = File("data.txt")
          content = file.read_text()
      except FileError as e:
          logger.error(f"Failed to read file: {e}")

2. **Resource Management**
   
   Use context managers when appropriate:

   .. code-block:: python

      with File("large_file.txt").open() as f:
          content = f.read()

3. **Type Safety**
   
   Leverage type hints for better IDE support:

   .. code-block:: python

      from happy_core.types import JsonDict

      def process_data(data: JsonDict) -> List[str]:
          # Your code here
          pass
