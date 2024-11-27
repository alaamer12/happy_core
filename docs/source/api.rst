API Reference
=============

.. toctree::
   :maxdepth: 2

   modules/collections
   modules/enum_registry
   modules/time
   modules/types
   modules/toolkits
   modules/re

Collections
-----------

The collections module provides enhanced file system operations.

.. module:: happy_core.collections

Key Classes:

- :class:`File`: Enhanced file operations
- :class:`Directory`: Directory management
- :class:`RecycleBin`: Recycling bin functionality
- :class:`FileMetadata`: File metadata tracking
- :class:`FileCreator`: Base class for file creators
- :class:`OSUtils`: Operating system utilities

Enum Registry
-------------

The enum registry module provides enumeration validation and registration.

.. module:: happy_core.enum_registry

Key Classes:

- :class:`EnumRegistry`: Main registry class

Time
----

The time module provides time manipulation and scheduling utilities.

.. module:: happy_core.time

Key Classes:

- :class:`TimeUtils`: Time manipulation utilities
- :class:`Timer`: Performance timing
- :class:`Scheduler`: Task scheduling

Types
-----

The types module provides custom type definitions and checking.

.. module:: happy_core.types

Key Classes:

- :class:`PathLike`: Path-like type definition
- :class:`JsonDict`: JSON dictionary type
- :class:`Callback`: Callback function type
- :class:`TypeChecker`: Type checking utilities

Toolkits
--------

The toolkits module provides various utility functions and decorators.

.. module:: happy_core.toolkits

Key Functions:

- :func:`retry`: Retry decorator
- :func:`monitor`: Performance monitoring decorator
- :func:`cache`: Caching decorator
- :func:`hash_file`: File hashing
- :func:`compress_file`: File compression
- :func:`encrypt_file`: File encryption

Exceptions
----------

The exceptions module provides custom exceptions.

.. module:: happy_core.exceptions

Key Exceptions:

- :exc:`HappyCoreError`: Base exception
- :exc:`ValidationError`: Validation errors
- :exc:`FileSystemError`: File system errors
- :exc:`EnumValidationError`: Enum validation errors
- :exc:`TimeError`: Time-related errors
