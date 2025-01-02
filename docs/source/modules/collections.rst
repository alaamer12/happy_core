Collections Module
==================

.. module:: true.collections
   :no-index:

The collections module provides advanced file system operations and enhanced data structures with comprehensive functionality
for file management, and file system monitoring.

Key Components
--------------

- :class:`FileStats`: Enhanced data class for file statistics
- :class:`File`: Enhanced file class with additional capabilities
- :class:`Directory`: Enhanced directory class with advanced operations
- :class:`OSUtils`: Comprehensive OS utility class

File Management
---------------

FileStats
~~~~~~~~~

.. autoclass:: true.collections.FileStats
   :members:
   :special-members: __init__

File
~~~~

.. autoclass:: true.collections.File
   :members:
   :special-members: __init__

Directory
~~~~~~~~~

.. autoclass:: true.collections.Directory
   :members:
   :special-members: __init__

OS Utilities
------------

OSUtils
~~~~~~~

.. autoclass:: true.collections.OSUtils
   :members:
   :special-members: __init__


Examples
--------

File Operations
~~~~~~~~~~~~~~~

.. code-block:: python

   from true.collections import File, Directory, OSUtils

   # Enhanced file operations
   file = File("example.txt")
   print(file.size)  # Get file size
   print(file.md5)   # Get MD5 hash
   print(file.mime_type)  # Get MIME type

   # Copy with retry mechanism
   file.copy_to("backup/example.txt")

   # Create backup
   file.create_backup()  # Creates example.txt.bak

   # Directory operations
   directory = Directory("my_folder")
   directory.create()  # Create if not exists
   
   # Get directory tree
   tree = directory.get_tree(max_depth=2)
   
   # Create zip archive
   directory.zip_contents("archive.zip")


OS Utilities Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from true.collections import OSUtils
   from datetime import datetime, timedelta

   os_utils = OSUtils()

   # Watch directory for changes
   def on_change(event):
       print(f"Change detected: {event.src_path}")

   os_utils.watch_directory("watched_dir", on_change)

   # Find files by date
   yesterday = datetime.now() - timedelta(days=1)
   files = os_utils.find_files_by_date(
       "search_dir",
       start_date=yesterday,
       modified=True
   )

   # Safe delete with secure overwrite
   os_utils.safe_delete("sensitive.txt", secure=True)

   # Batch process files
   def process_file(file_path):
       # Process file
       pass

   os_utils.batch_process(
       ["file1.txt", "file2.txt"],
       process_file,
       parallel=True
   )