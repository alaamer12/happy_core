Collections Module
==================

.. module:: true.collections
   :no-index:

The collections module provides advanced file system operations and enhanced data structures with comprehensive functionality
for file management, recycling bin operations, and file system monitoring.

Key Components
--------------

- :class:`FileStats`: Enhanced data class for file statistics
- :class:`File`: Enhanced file class with additional capabilities
- :class:`Directory`: Enhanced directory class with advanced operations
- :class:`RecycleBin`: Advanced recycling bin implementation
- :class:`OSUtils`: Comprehensive OS utility class
- :class:`DummyFile`: Template-based dummy file creator

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

Recycling Bin
-------------

RecycleBin
~~~~~~~~~~

.. autoclass:: true.collections.RecycleBin
   :members:
   :special-members: __init__

RecycleBinManager
~~~~~~~~~~~~~~~~~

.. autoclass:: true.collections.RecycleBinManager
   :members:
   :special-members: __init__

OS Utilities
------------

OSUtils
~~~~~~~

.. autoclass:: true.collections.OSUtils
   :members:
   :special-members: __init__

File Creation
-------------

DummyFile
~~~~~~~~~

.. autoclass:: true.collections.DummyFile
   :members:
   :special-members: __init__

FileCreator
~~~~~~~~~~~

.. autoclass:: true.collections.FileCreator
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

Recycling Bin Usage
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from true.collections import RecycleBin

   # Initialize recycle bin
   recycle_bin = RecycleBin("./trash", max_size=1024*1024*1024)  # 1GB max

   # Delete with move to recycle bin
   item_id = recycle_bin.delete("old_file.txt")

   # Restore from recycle bin
   recycle_bin.restore(item_id)

   # List items with pattern
   items = recycle_bin.list_items("*.txt")

   # Cleanup old items
   recycle_bin.cleanup(days=30)

   # Use as context manager for batch operations
   with recycle_bin:
       recycle_bin.delete("file1.txt")
       recycle_bin.delete("file2.txt")

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

Dummy File Creation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from true.collections import DummyFile

   # Create dummy files of various types
   dummy = DummyFile()

   # Create PDF dummy file
   dummy.create_file(".pdf", "test.pdf", size=1024*1024)  # 1MB file

   # Create image file
   dummy.create_image("test.png")

   # Create video file
   dummy.create_video("output.mp4", fps=30)

   # Create audio file
   dummy.create_audio("test.wav", duration=5000)