Troubleshooting Guide
===================

This guide covers common issues you might encounter while using True-Core and their solutions.

Missing Dependencies
------------------

ModuleNotFoundError: No module named 'tomlkit'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
.. code-block:: python

    ModuleNotFoundError: No module named 'tomlkit'

**Solution:**
Install the missing dependency:

.. code-block:: bash

    pip install tomlkit

ModuleNotFoundError: No module named 'yaml'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
.. code-block:: python

    ModuleNotFoundError: No module named 'yaml'

**Solution:**
Install PyYAML:

.. code-block:: bash

    pip install pyyaml

ModuleNotFoundError: No module named 'watchdog'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
.. code-block:: python

    ModuleNotFoundError: No module named 'watchdog'

**Solution:**
Install watchdog:

.. code-block:: bash

    pip install watchdog

Enum Registry Issues
------------------

Using enum.auto() Instead of true.enum_registry.auto()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
Using ``enum.auto()`` from the standard library causes crashes:

.. code-block:: python

    from enum import auto  # Wrong import!
    
    class MyEnum(Enum):
        VALUE = auto()  # This will cause issues

**Solution:**
Always use ``true.enum_registry.auto()``:

.. code-block:: python

    from true.enum_registry import auto  # Correct import
    
    class MyEnum(Enum):
        VALUE = auto()  # This works correctly

Type System Issues
----------------

BigDecimal Validation Errors
~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
Unexpected validation errors with BigDecimal:

.. code-block:: python

    from true.types import BigDecimal
    
    value = BigDecimal("123.456789123456789")  # Validation error

**Solution:**
Ensure proper decimal string format and consider precision limits:

.. code-block:: python

    # Correct usage with proper precision
    value = BigDecimal("123.456789", precision=6)

File Operations
-------------

FileNotFoundError with Directory Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
Errors when trying to access directories:

.. code-block:: python

    FileNotFoundError: [Errno 2] No such file or directory: 'path/to/dir'

**Solution:**
Ensure directory exists before operations:

.. code-block:: python

    from true.collections import Directory
    
    # Create directory if it doesn't exist
    dir = Directory("path/to/dir")
    dir.create(parents=True)  # Creates parent directories if needed

MoviePy Video Creation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
Video creation fails without fps parameter:

.. code-block:: python

    # This might fail
    create_static_video("input.jpg", "output.mp4")

**Solution:**
Always specify the fps parameter:

.. code-block:: python

    # This works correctly
    create_static_video("input.jpg", "output.mp4", fps=24)

Installation Issues
----------------

Poetry Installation Failures
~~~~~~~~~~~~~~~~~~~~~~~~
**Problem:**
Poetry fails to install dependencies.

**Solution:**
Try these steps:

1. Update poetry:
   
   .. code-block:: bash

       poetry self update

2. Clear poetry cache:
   
   .. code-block:: bash

       poetry cache clear . --all

3. Install with specific groups:
   
   .. code-block:: bash

       poetry install --with dev,docs

Development Environment
--------------------

Missing Type Hints
~~~~~~~~~~~~~~
**Problem:**
Type checking errors or missing type hints.

**Solution:**
Install type checking dependencies:

.. code-block:: bash

    poetry install --with dev
    # or
    pip install mypy types-PyYAML types-tomlkit

Then run type checking:

.. code-block:: bash

    mypy true

Still Having Issues?
-----------------
If you're still experiencing problems:

1. Check the :doc:`changelog` for known issues in your version
2. Ensure all dependencies are properly installed
3. Update to the latest version of True-Core
4. Open an issue on our `GitHub repository <https://github.com/alaamer12/true-core>`_
