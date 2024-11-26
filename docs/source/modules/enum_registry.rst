Enum Registry Module
=================

.. module:: happy_core.enum_registry

The enum registry module provides enhanced enumeration capabilities with validation and registration.

Classes
-------

EnumRegistry
~~~~~~~~~~

.. autoclass:: happy_core.enum_registry.EnumRegistry
   :members:
   :special-members: __init__

Exceptions
---------

.. autoclass:: happy_core.exceptions.EnumValidationError
   :members:
   :show-inheritance:

.. autoclass:: happy_core.exceptions.EnumTypeError
   :members:
   :show-inheritance:

Examples
-------

Basic Usage
~~~~~~~~~

.. code-block:: python

   from happy_core.enum_registry import EnumRegistry

   # Create registry
   registry = EnumRegistry()

   # Define and register an enum
   @registry.register
   class UserStatus:
       ACTIVE = "active"
       INACTIVE = "inactive"
       SUSPENDED = "suspended"

   # Validate values
   is_valid = registry.validate("active", UserStatus)  # True
   is_valid = registry.validate("unknown", UserStatus)  # False

   # Get all choices
   choices = registry.get_choices(UserStatus)
   # Returns: [("active", "ACTIVE"), ("inactive", "INACTIVE"), ("suspended", "SUSPENDED")]

Advanced Usage
~~~~~~~~~~~~

.. code-block:: python

   from happy_core.enum_registry import EnumRegistry
   from dataclasses import dataclass
   from typing import Optional

   registry = EnumRegistry()

   @registry.register
   class OrderStatus:
       PENDING = "pending"
       PROCESSING = "processing"
       SHIPPED = "shipped"
       DELIVERED = "delivered"
       CANCELLED = "cancelled"

   @dataclass
   class Order:
       id: str
       status: str
       tracking_number: Optional[str] = None

       def __post_init__(self):
           # Validate status using registry
           if not registry.validate(self.status, OrderStatus):
               raise ValueError(f"Invalid order status: {self.status}")

   # Create orders with validation
   try:
       order = Order("123", "pending")  # Valid
       invalid_order = Order("456", "invalid_status")  # Raises ValueError
   except ValueError as e:
       print(f"Error: {e}")

Type Checking
~~~~~~~~~~~

.. code-block:: python

   from happy_core.enum_registry import EnumRegistry
   from typing import List, Dict

   registry = EnumRegistry()

   @registry.register
   class Priority:
       LOW = 1
       MEDIUM = 2
       HIGH = 3

   def process_task(priority: int) -> None:
       # Validate priority using registry
       if not registry.validate(priority, Priority):
           raise ValueError(f"Invalid priority level: {priority}")
       
       # Process task based on priority
       if priority == Priority.HIGH:
           print("Processing high priority task")
       elif priority == Priority.MEDIUM:
           print("Processing medium priority task")
       else:
           print("Processing low priority task")

   # Usage
   process_task(Priority.HIGH)  # Valid
   process_task(5)  # Raises ValueError
