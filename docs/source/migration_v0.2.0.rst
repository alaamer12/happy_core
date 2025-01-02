Migration Guide to Version 0.2.0
================================

This guide helps you migrate your code from True-Core < 0.2.0 to the new package structure.

Component Migration Map
-----------------------

Enumeration Components
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Update enumeration imports
   :emphasize-lines: 1,2,4,5

   # Old imports
   from true.enum_registry import EnumRegistry
   from true.enum_toolkits import EnumToolkit
   
   # New imports
   from true_enumeration.registry import EnumRegistry
   from true_enumeration.toolkits import EnumToolkit

Type System
~~~~~~~~~~~

.. code-block:: python
   :caption: Update type system imports
   :emphasize-lines: 1,4

   # Old imports
   from true.types import CustomType, TypeValidator
   
   # New imports
   from true_types import CustomType, TypeValidator

File Handling
~~~~~~~~~~~~~

.. code-block:: python
   :caption: Update DummyFile imports
   :emphasize-lines: 1,4

   # Old imports
   from true.utils import DummyFile
   
   # New imports
   from true_blobs import DummyFile

Removed Components
------------------

Pointer Class
~~~~~~~~~~~~~

The ``Pointer`` class has been removed. Use Python's built-in reference system instead:

.. code-block:: python
   :caption: Replace Pointer usage
   :emphasize-lines: 1,2,5,8,9

   # Old code (no longer available)
   from true.utils import Pointer
   
   obj = SomeObject()
   ptr = Pointer(obj)
   
   # New code
   obj = SomeObject()  # Direct reference
   weak_ref = weakref.ref(obj)  # If weak reference is needed

Recyclebin
~~~~~~~~~~

The ``Recyclebin`` functionality has been temporarily removed. Implement a basic alternative if needed:

.. code-block:: python
   :caption: Temporary Recyclebin alternative
   :emphasize-lines: 1,7

   # Old code (no longer available)
   from true.utils import Recyclebin
   
   recycler = Recyclebin()
   
   # Temporary solution
   class SimpleRecycleBin:
       def __init__(self):
           self._items = []
       
       def add(self, item):
           self._items.append(item)
       
       def restore(self, item):
           if item in self._items:
               self._items.remove(item)
               return item
           return None

Installation Updates
--------------------

Update your dependencies to include the new packages:

.. code-block:: bash

   # Remove old version
   pip uninstall true-core
   
   # Install new version and required packages
   pip install true-core>=0.2.0
   pip install true-enumeration true-types true-blobs

Common Issues
-------------

1. Import Errors
   
   - Update all imports to use the new package names
   - Check for any missed imports in your codebase
   - Update your test imports as well

2. Missing Components
   
   - If you were using ``Pointer``, switch to Python's reference system
   - If you were using ``Recyclebin``, implement a temporary solution

3. Version Conflicts
   
   - Ensure all new packages are installed
   - Check version compatibility
   - Update all packages together

Need Help?
----------

- Check the full :doc:`releases/0.2.0` and :doc:`changelogs/0.2.0` notes
- Visit the new package documentation sites:
    - `true-enumeration <https://true-enumeration.readthedocs.io/>`_
    - `true-types <https://true-types.readthedocs.io/>`_
    - `true-blobs <https://true-blobs.readthedocs.io/>`_
- Report issues on the respective GitHub repositories
- Join our community discussions
