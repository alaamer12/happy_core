Enums Toolkits Module
=====================

.. module:: true.enums_toolkits
   :no-index:

The enums toolkits module provides a sophisticated framework for defining specialized Enum classes in Python,
extending the native Enum capabilities with advanced features like metadata handling, serialization, and
type-specific validation.

Key Components
--------------

- :class:`MetadataConfig`: Configuration class for enum metadata
- :class:`SerializedEnumMeta`: Metaclass for JSON/dict serialization
- :class:`DynamicEnum`: Runtime-modifiable enum class
- Type-specific enum classes for various data types

Classes
-------

MetadataConfig
~~~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.MetadataConfig
   :members:
   :special-members: __init__

SerializedEnumMeta
~~~~~~~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.SerializedEnumMeta
   :members:
   :special-members: __new__

DynamicEnum
~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.DynamicEnum
   :members:
   :special-members: __init__

DynamicEnumMember
~~~~~~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.DynamicEnumMember
   :members:
   :special-members: __init__

Type-Specific Enums
-------------------

IterableEnum
~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.IterableEnum
   :members:
   :special-members: __init__

IteratorEnum
~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.IteratorEnum
   :members:
   :special-members: __init__

GeneratorEnum
~~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.GeneratorEnum
   :members:
   :special-members: __init__

ByteEnum
~~~~~~~~

.. autoclass:: true.enums_toolkits.ByteEnum
   :members:
   :special-members: __init__

FloatEnum
~~~~~~~~~

.. autoclass:: true.enums_toolkits.FloatEnum
   :members:
   :special-members: __init__

ComplexNumberEnum
~~~~~~~~~~~~~~~~~

.. autoclass:: true.enums_toolkits.ComplexNumberEnum
   :members:
   :special-members: __init__

DictEnum
~~~~~~~~

.. autoclass:: true.enums_toolkits.DictEnum
   :members:
   :special-members: __init__

SetEnum
~~~~~~~

.. autoclass:: true.enums_toolkits.SetEnum
   :members:
   :special-members: __init__

ListEnum
~~~~~~~~

.. autoclass:: true.enums_toolkits.ListEnum
   :members:
   :special-members: __init__

TupleEnum
~~~~~~~~~

.. autoclass:: true.enums_toolkits.TupleEnum
   :members:
   :special-members: __init__

Decorators
----------

metadata
~~~~~~~~

.. autofunction:: true.enums_toolkits.metadata

Examples
--------

Basic Usage with DynamicEnum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from true.enums_toolkits import DynamicEnum

   # Create a dynamic enum
   colors = DynamicEnum(RED="red", GREEN="green", BLUE="blue")

   # Access members
   print(colors.RED.value)  # "red"
   print(colors.RED.name)   # "RED"

   # Add new members at runtime
   colors.add_member("YELLOW", "yellow")
   
   # Remove members
   colors.remove_member("BLUE")

Type-Safe Enums
~~~~~~~~~~~~~~~

.. code-block:: python

   from true.enums_toolkits import FloatEnum, DictEnum, SetEnum

   class Temperatures(FloatEnum):
       FREEZING = 0.0
       BOILING = 100.0

   class Config(DictEnum):
       DEFAULT = {"host": "localhost", "port": 8080}
       PRODUCTION = {"host": "example.com", "port": 443}

   class Permissions(SetEnum):
       READ = {"read"}
       WRITE = {"read", "write"}
       ADMIN = {"read", "write", "admin"}

Metadata and Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from true.enums_toolkits import metadata, MetadataConfig, SerializedEnumMeta
   from enum import Enum

   config = MetadataConfig(
       include_bit_length=True,
       include_type_info=True,
       custom_attributes={"category": "status"}
   )

   @metadata(config)
   class Status(Enum):
       ACTIVE = 1
       INACTIVE = 0

   # Get detailed description
   print(Status.ACTIVE.get_description())

   # Serialization
   class Colors(metaclass=SerializedEnumMeta):
       RED = "#FF0000"
       GREEN = "#00FF00"
       BLUE = "#0000FF"

   # Convert to dict/json
   colors_dict = Colors.to_dict()
   colors_json = Colors.to_json()

   # Create from dict/json
   new_colors = Colors.from_dict("NewColors", {"PURPLE": "#800080"})
