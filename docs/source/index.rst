Welcome to Happy Core's documentation!
======================================

.. image:: https://img.shields.io/badge/python-3.7%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://choosealicense.com/licenses/mit/


Happy Core is a comprehensive utility toolkit designed for Python developers seeking clean, efficient, and maintainable solutions.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api
   api_reference
   modules/collections
   modules/enum_registry
   modules/time
   modules/re
   modules/types
   modules/toolkits

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   examples
   
.. toctree::
   :maxdepth: 2
   :caption: Project Info

   changelog
   releases

Features
--------

- **📝 Enhanced File System Operations**
    - Advanced file and directory management
    - Recycling bin functionality
    - File metadata tracking

- **🔧 Developer Tools**
    - Type checking and hints
    - Performance monitoring
    - Debugging utilities

- **📚 Rich Module Collection**
    - Regular expression patterns
    - Time utilities
    - Collection helpers
    - Type definitions

Quick Start
-----------

.. code-block:: python

   from happy_core.collections import File, Directory, RecycleBin
   from happy_core.enum_registry import EnumRegistry
   from happy_core.toolkits import retry, monitor

   # File operations
   file = File("document.txt")
   file.write_text("Hello, World!")
   
   # Directory operations
   docs = Directory("documents")
   docs.create()
   
   # Use RecycleBin
   with RecycleBin("./recyclebin") as bin:
       file_id = bin.delete("old_file.txt")
       bin.add_tag(file_id, "archived")

   # Create and validate enums
   registry = EnumRegistry()
   
   @registry.register
   class Status:
       ACTIVE = "active"
       INACTIVE = "inactive"

   # Use decorators
   @retry(max_attempts=3)
   @monitor
   def process_data():
       pass

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
