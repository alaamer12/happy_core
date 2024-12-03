API Documentation
=================

True-Core is a comprehensive Python utility library providing advanced functionality for enum management, type validation, time handling, regular expressions, and file operations.

Core Components
---------------

.. toctree::
   :maxdepth: 2

   modules/enum_registry
   modules/enums_toolkits
   modules/collections
   modules/time
   modules/re
   modules/types

Enum Management
---------------

The enum management components provide sophisticated tools for handling enums:

- :mod:`true.enum_registry`: Advanced enum combination and registry management
- :mod:`true.enums_toolkits`: Specialized enum classes and metadata support

File System Operations
----------------------

The file system components offer comprehensive file handling capabilities:

- :mod:`true.collections`: Advanced file system operations and recycling bin management
- File creation and manipulation utilities
- Cross-platform compatibility
- Secure file deletion

Time Management
---------------

Time handling utilities with extensive features:

- :mod:`true.time`: Advanced timezone support and time manipulation
- Event scheduling and management
- Time formatting and conversion
- Performance timing utilities

Regular Expressions
-------------------

Pre-compiled regex patterns for common validation tasks:

- :mod:`true.re`: Comprehensive pattern library
- Username and password validation
- Email and URL validation
- Phone number and credit card validation
- Date format validation

Type System
-----------

Advanced type validation and handling:

- :mod:`true.types`: Version handling (SemVer, CalVer)
- Numeric types (BigInt, BigDecimal)
- UUID/ULID support
- Serialization utilities

Exception Handling
------------------

Specialized exceptions for better error management:

- :mod:`true.exceptions`: Custom exception hierarchy
- Type-specific error handling
- Operation-specific exceptions
- Validation error handling