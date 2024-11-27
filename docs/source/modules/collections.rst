Collections Module
==================

.. module:: happy_core.collections
  :no-index:

The Collections module provides powerful, type-safe abstractions for handling files, directories, and data structures.

Key Features
------------

- 🛡️ **Type-safe operations** with comprehensive error handling
- 🚀 **High-performance implementations** optimized for large-scale operations
- 🔄 **Chainable API** for fluent programming style
- 📊 **Built-in monitoring** capabilities
- 🗄️ **Automatic resource management**

File Operations
---------------

File Class
~~~~~~~~~~

.. py:class:: File

   A robust file handling class with built-in error handling and type safety.

   **Key Benefits:**
   
   - Automatic resource cleanup
   - Built-in retry mechanisms
   - Type-safe operations
   - Performance monitoring
   
   .. code-block:: python

      from happy_core.collections import File
      
      # Type-safe file operations
      config_file = File("config.json")
      config = config_file.read_json()  # Automatically validates JSON
      
      # Automatic resource management
      with config_file.open() as f:
          content = f.read()
   
   .. py:method:: __init__(path: str)
      
      Initialize a new File instance.

      :param path: Path to the file
      :raises FileError: If path is invalid

   .. py:method:: read_text(encoding: str = 'utf-8', retry_count: int = 3) -> str
      
      Read file contents with automatic retry.

      :param encoding: Text encoding
      :param retry_count: Number of retry attempts
      :return: File contents
      :raises FileError: On read failure

   .. py:method:: write_text(content: str, encoding: str = 'utf-8', backup: bool = True) -> None
      
      Write content with automatic backup.

      :param content: Content to write
      :param encoding: Text encoding
      :param backup: Create backup before writing
      :raises FileError: On write failure

   .. py:method:: read_json() -> JsonDict
      
      Read and validate JSON content.

      :return: Parsed JSON data
      :raises ValidationError: On invalid JSON

Directory Operations
--------------------

Directory Class
~~~~~~~~~~~~~~~

.. py:class:: Directory

   A powerful directory management class with recursive operations support.

   **Key Features:**
   
   - Recursive operations
   - Pattern matching
   - Progress monitoring
   - Concurrent operations
   
   .. code-block:: python

      from happy_core.collections import Directory
      
      # Create directory tree
      project_dir = Directory("my_project")
      project_dir.create_tree({
          "src": {"main.py", "utils.py"},
          "tests": {"test_main.py"},
          "docs": {}
      })
      
      # Find files by pattern
      python_files = project_dir.glob("**/*.py")
   
   .. py:method:: __init__(path: str)
      
      Initialize directory handler.

      :param path: Directory path
      :raises DirectoryError: If path is invalid

   .. py:method:: create(exist_ok: bool = True, mode: int = 0o755) -> None
      
      Create directory with permissions.

      :param exist_ok: Allow existing directory
      :param mode: Directory permissions
      :raises DirectoryError: On creation failure

   .. py:method:: glob(pattern: str) -> List[File]
      
      Find files by pattern.

      :param pattern: Glob pattern
      :return: List of matching files

RecycleBin Operations
---------------------

RecycleBin Class
~~~~~~~~~~~~~~~~

.. py:class:: RecycleBin

   Safe file deletion with recovery capabilities.

   **Features:**
   
   - Soft delete support
   - File recovery
   - Automatic cleanup
   - Version tracking
   
   .. code-block:: python

      from happy_core.collections import RecycleBin
      
      # Initialize recycle bin
      bin = RecycleBin(".trash")
      
      # Safely delete file
      deleted_id = bin.delete("old_config.json")
      
      # Recover if needed
      bin.recover(deleted_id)

Best Practices
--------------

1. **Resource Management**

   Always use context managers for file operations:

   .. code-block:: python

      with File("large_file.txt").open() as f:
          for line in f:
              process_line(line)

2. **Error Handling**

   Implement comprehensive error handling:

   .. code-block:: python

      try:
          file = File("config.json")
          config = file.read_json()
      except FileError as e:
          logger.error(f"File error: {e}")
          config = default_config()
      except ValidationError as e:
          logger.error(f"Invalid JSON: {e}")
          config = default_config()

3. **Performance Optimization**

   Use appropriate methods for large files:

   .. code-block:: python

      # Good - memory efficient
      for line in File("large.txt").iter_lines():
          process_line(line)
      
      # Bad - loads entire file
      lines = File("large.txt").read_text().splitlines()

Advanced Usage
--------------

1. **Concurrent Operations**

   Process multiple files concurrently:

   .. code-block:: python

      from happy_core.collections import Directory
      from concurrent.futures import ThreadPoolExecutor
      
      def process_file(file: File):
          return file.read_json()
      
      dir = Directory("data")
      with ThreadPoolExecutor() as executor:
          results = executor.map(process_file, dir.glob("*.json"))

2. **Custom File Types**

   Extend File class for specific formats:

   .. code-block:: python

      class ConfigFile(File):
          def read_config(self) -> Dict[str, Any]:
              data = self.read_json()
              return self.validate_config(data)
          
          def validate_config(self, data: JsonDict) -> Dict[str, Any]:
              # Custom validation logic
              pass

3. **Monitoring and Metrics**

   Track file operations:

   .. code-block:: python

      from happy_core.toolkits import monitor
      
      @monitor
      def process_files(directory: Directory):
          for file in directory.glob("*.dat"):
              process_data(file.read_bytes())

See Also
--------

* :doc:`../api` - Complete API reference
* :doc:`../examples` - More usage examples
* :doc:`types` - Type definitions used in this module
