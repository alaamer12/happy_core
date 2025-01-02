Installation
============

Prerequisites
-------------

- Python 3.7 or higher
- pip or poetry (recommended)

Using pip
---------

.. code-block:: bash

   pip install true-core

Using poetry
------------

.. code-block:: bash

   poetry add true-core

From source
-----------

.. code-block:: bash

   git clone https://github.com/alaamer12/true-core.git
   cd true-core
   pip install -r requirements/dev.txt

Package Split Notice
--------------------

.. important::
   As of version 0.2.0, several components have been moved to separate packages.
   Depending on your needs, you may need to install additional packages:

   .. code-block:: bash

      # For enumeration functionality
      pip install true-enumeration

      # For type system
      pip install true-types

      # For DummyFile and blob handling
      pip install true-blobs

   See :doc:`releases/0.2.0` for detailed migration instructions.

Development Installation
------------------------

For development, you might want to install additional dependencies:

.. code-block:: bash

   pip install -r requirements/dev.txt

This will install development dependencies like:

- pytest for testing
- pylint for code quality
- mypy for type checking
- black for code formatting
