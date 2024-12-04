Enum Registry Module
====================

.. module:: true.enum_registry
   :no-index:

The enum registry module provides a sophisticated framework for managing and combining multiple Enum classes with advanced functionality.

Key Components
--------------

.. warning::
   When defining enum values, always use ``true.enum_registry.auto()`` instead of ``enum.auto()``. 
   Using ``enum.auto()`` from the standard library can cause crashes and unexpected behavior.
   
   **Correct usage:**
   
   .. code-block:: python
   
       from true.enum_registry import auto
       
       class MyEnum(Enum):
           VALUE_1 = auto()  # Correct
           VALUE_2 = auto()  # Correct
   
   **Incorrect usage:**
   
   .. code-block:: python
   
       from enum import auto  # Do not use this!
       
       class MyEnum(Enum):
           VALUE_1 = auto()  # Will cause crashes
           VALUE_2 = auto()  # Will cause crashes

- :class:`EnumRegistry`: Main registry class for managing multiple Enum classes
- :class:`EnumMapping`: Base class for enum mappings with caching support
- :class:`EnumData`: TypedDict for enum metadata
- :class:`EnumStats`: Statistics about the enum registry
- :class:`BaseMetadata`: Base class for metadata
- :class:`EnumMetadata`: Enhanced metadata for enum members

Classes
-------

EnumRegistry
~~~~~~~~~~~~

.. autoclass:: true.enum_registry.EnumRegistry
   :members:
   :special-members: __init__

EnumMapping
~~~~~~~~~~~

.. autoclass:: true.enum_registry.EnumMapping
   :members:
   :special-members: __init__

EnumStats
~~~~~~~~~

.. autoclass:: true.enum_registry.EnumStats
   :members:
   :special-members: __init__

EnumMetadata
~~~~~~~~~~~~

.. autoclass:: true.enum_registry.EnumMetadata
   :members:
   :special-members: __init__

Exceptions
----------

.. autoclass:: true.exceptions.InvalidEnumTypeError
   :members:
   :show-inheritance:

.. autoclass:: true.exceptions.IncompatibleTypesError
   :members:
   :show-inheritance:

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from true.enum_registry import EnumRegistry
   from enum import Enum

   # Define enums
   class UserStatus(Enum):
       ACTIVE = "active"
       INACTIVE = "inactive"
       SUSPENDED = "suspended"

   class OrderStatus(Enum):
       PENDING = "pending"
       PROCESSING = "processing"
       SHIPPED = "shipped"

   # Register enums
   registry = EnumRegistry([UserStatus, OrderStatus])

   # Or use decorator
   @registry.dregister
   class Priority(Enum):
       LOW = 1
       MEDIUM = 2
       HIGH = 3

Advanced Features
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Arithmetic operations
   combined = registry + another_registry
   filtered = registry - excluded_registry
   common = registry.intersect(other_registry)

   # Filtering and querying
   high_priority = registry.by_value_type(int)
   active_states = registry.by_prefix("ACTIVE")
   custom_filter = registry.by_predicate(lambda x: x.value > 1)

   # Metadata management
   registry.set_member_metadata(UserStatus.ACTIVE, 
                              description="Active user state",
                              tags={"user", "state"})

   # Statistics and debug info
   stats = registry.statistics()
   debug_info = registry.format_debug()

   # Serialization
   data = registry.to_dict()

Type Checking
~~~~~~~~~~~~~

.. code-block:: python

   def process_task(priority: int) -> None:
       if priority not in registry:
           raise ValueError(f"Invalid priority: {priority}")
       
       if priority == Priority.HIGH:
           print("Processing high priority task")
       elif priority == Priority.MEDIUM:
           print("Processing medium priority task")
       else:
           print("Processing low priority task")