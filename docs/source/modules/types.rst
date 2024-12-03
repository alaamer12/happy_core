Types Module
============

The types module provides a comprehensive set of classes and utilities for working with various data types, including version strings, numerical types, identifiers, and serialization formats. It focuses on enforcing validation rules and providing robust error handling.

Key Features
------------

* Version validation and parsing (SemVer, CalVer, Date Versioning)
* Validated numeric types with constraints
* UUID and ULID handling with versioning
* Scientific number validation
* Serialization support (JSON, YAML, TOML)
* Type hints and generic utilities

Version Types
-------------

Version Base Classes
~~~~~~~~~~~~~~~~~~~~

.. py:class:: VersionValidatorMixin

   A mixin that provides version validation functionality.

.. py:class:: Version

   Base class for version objects.

   .. py:attribute:: PATTERNS
      :type: ClassVar[set]

      Set of supported version patterns.

   .. py:attribute:: major
      :type: str

      Major version number.

   .. py:attribute:: minor
      :type: str

      Minor version number.

   .. py:attribute:: patch
      :type: str
      :value: Optional

      Patch version number.

   .. py:attribute:: tag
      :type: str
      :value: Optional

      Version tag (e.g., alpha, beta).

Version Implementation Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: SemVersion

   Semantic Versioning implementation (MAJOR.MINOR.PATCH[-TAG]).

.. py:class:: DateVersion

   Date-based versioning implementation (YYYY.MM.DD[-TAG]).

.. py:class:: CalVersion

   Calendar versioning implementation (YY.MM[-TAG]).

.. py:class:: MajorMinorVersion

   Simple major.minor versioning without patch numbers.

Numeric Types
-------------

Base Classes
~~~~~~~~~~~~

.. py:class:: ValidatedNumber(Generic[T])

   Base class for validated numeric types.

   .. py:classmethod:: validate(cls, value: Union[int, float]) -> bool

      Validate the input value.

   .. py:classmethod:: get_error_message(cls, value: Union[int, float]) -> str

      Get the error message for invalid values.

Integer Types
~~~~~~~~~~~~~

.. py:class:: ValidatedInt(ValidatedNumber[int])

   Base class for validated integer types.

.. py:class:: PositiveInt(ValidatedInt)

   Integer type that must be positive.

.. py:class:: NegativeInt(ValidatedInt)

   Integer type that must be negative.

.. py:class:: UnsignedInt(ValidatedInt)

   Integer type that must be non-negative.

.. py:class:: BigInt

   Class for handling large integers with architecture-aware bounds.

   :param value: Integer value
   :param strict: Enable strict validation
   :param context: Validation context ("Positive", "Negative", "Unsigned")

Float Types
~~~~~~~~~~~

.. py:class:: ValidatedFloat(ValidatedNumber[float])

   Base class for validated float types.

.. py:class:: PositiveFloat(ValidatedFloat)

   Float type that must be positive.

.. py:class:: NegativeFloat(ValidatedFloat)

   Float type that must be negative.

.. py:class:: UnsignedFloat(ValidatedFloat)

   Float type that must be non-negative.

.. py:class:: BigDecimal

   Class for handling large decimal numbers.

   :param value: Decimal value
   :param strict: Enable strict validation
   :param context: Validation context ("Positive", "Negative", "Unsigned")
   :param stop_warnings: Suppress warnings

Scientific Numbers
~~~~~~~~~~~~~~~~~~

.. py:class:: ScientificNumber

   Class for handling numbers in scientific notation.

   .. py:classmethod:: is_scientific_notation(num_str: str) -> bool

      Check if a string represents scientific notation.

Special Number Types
~~~~~~~~~~~~~~~~~~~~

.. py:class:: NaN

   Not-a-Number type with validation.

.. py:data:: Infinity
   :type: NewType("Infinity", float)

   Type for representing infinity.

.. py:data:: PositiveInfinity
   :value: Infinity(float("inf"))

.. py:data:: NegativeInfinity
   :value: Infinity(float("-inf"))

Identifier Types
----------------

UUID Types
~~~~~~~~~~

.. py:class:: UUIDType

   Base class for UUID handling.

.. py:class:: StrUUIDType(UUIDType)

   String-based UUID with validation.

.. py:class:: IntUUIDType(UUIDType)

   Integer-based UUID with validation.

Versioned UUID Types
~~~~~~~~~~~~~~~~~~~~

.. py:class:: UUIDVersionMixin

   Mixin for versioned UUID support.

.. py:class:: UUIDV1

   UUID version 1 implementation (time-based).

.. py:class:: UUIDV2

   UUID version 2 implementation (DCE Security).

.. py:class:: UUIDV3

   UUID version 3 implementation (MD5 hash-based).

.. py:class:: UUIDV4

   UUID version 4 implementation (random).

.. py:class:: UUIDV5

   UUID version 5 implementation (SHA-1 hash-based).

.. py:class:: StrUUIDV1

   String-based UUID version 1.

.. py:class:: StrUUIDV2

   String-based UUID version 2.

.. py:class:: StrUUIDV3

   String-based UUID version 3.

.. py:class:: StrUUIDV4

   String-based UUID version 4.

.. py:class:: StrUUIDV5

   String-based UUID version 5.

.. py:class:: IntUUIDV1

   Integer-based UUID version 1.

.. py:class:: IntUUIDV2

   Integer-based UUID version 2.

.. py:class:: IntUUIDV3

   Integer-based UUID version 3.

.. py:class:: IntUUIDV4

   Integer-based UUID version 4.

.. py:class:: IntUUIDV5

   Integer-based UUID version 5.

ULID Types
~~~~~~~~~~

.. py:class:: ULIDType

   Base class for ULID handling.

.. py:class:: StrULIDType(ULIDType)

   String-based ULID with validation.

.. py:class:: IntULIDType(ULIDType)

   Integer-based ULID with validation.

Serialization Types
-------------------

.. py:class:: JsonMixin

   Mixin for JSON serialization support.

   .. py:classmethod:: to_json(cls, value)
   .. py:classmethod:: from_json(cls, value)

.. py:class:: YamlMixin

   Mixin for YAML serialization support.

   .. py:classmethod:: to_yaml(cls, value)
   .. py:classmethod:: from_yaml(cls, value)

.. py:class:: TomlMixin

   Mixin for TOML serialization support.

   .. py:classmethod:: to_toml(cls, value)
   .. py:classmethod:: from_toml(cls, value)

Type Aliases
------------

.. py:data:: JsonType
   :type: NewType('JsonType', dict)

.. py:data:: XmlType
   :type: NewType('XmlType', dict)

.. py:data:: YamlType
   :type: NewType('YamlType', dict)

.. py:data:: TomlType
   :type: NewType('TomlType', dict)

Examples
--------

Version Handling::

    # Create a semantic version
    version = SemVersion("1.2.3-beta")
    
    # Create a calendar version
    cal_version = CalVersion("23.04")

Numeric Validation::

    # Create a positive integer
    pos_int = PositiveInt(42)
    
    # Create a big integer with constraints
    big_int = BigInt(1000000, strict=True, context="Positive")
    
    # Create a scientific number
    sci_num = ScientificNumber("1.23e-4")

UUID Handling::

    # Create a string UUID
    uuid_str = StrUUIDType("550e8400-e29b-41d4-a716-446655440000")
    
    # Create a version 4 UUID
    uuid_v4 = UUIDV4("550e8400-e29b-41d4-a716-446655440000")

ULID Handling::

    # Create a string ULID
    ulid_str = StrULIDType("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    
    # Create an integer ULID
    ulid_int = IntULIDType(1234567890)

Serialization::

    class MyType(JsonMixin):
        def __init__(self, data):
            self.data = data
    
    # Convert to/from JSON
    obj = MyType({"key": "value"})
    json_data = obj.to_json()
    new_obj = MyType.from_json(json_data)

Notes
-----

- All numeric types include validation to ensure values meet specified constraints.
- UUID and ULID implementations support both string and integer representations.
- Version classes support various versioning schemes with proper validation.
- Serialization mixins provide consistent interfaces for different formats.
- All classes include proper type hints for better IDE support.