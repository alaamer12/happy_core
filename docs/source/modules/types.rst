Types Module
============

.. module:: happy_core.types

A comprehensive type system providing robust type safety and validation for Python applications.

Key Features
-----------

- **Type safety** with runtime validation
- **Custom type definitions**
- **Type conversion** utilities
- **Performance optimized** validation
- **Rich type metadata**

Core Types
---------

JsonDict
~~~~~~~

.. py:class:: JsonDict

   Type-safe dictionary for JSON-compatible data.

   **Features:**
   
   - Runtime validation
   - Schema enforcement
   - Nested structure support
   - Serialization helpers
   
   .. code-block:: python

      from happy_core.types import JsonDict, validate_json
      
      @validate_json
      def process_config(config: JsonDict) -> JsonDict:
          """Process configuration with type validation."""
          return {
              "processed": True,
              "values": config.get("values", []),
              "timestamp": time.time()
          }

DataFrameType
~~~~~~~~~~~

.. py:class:: DataFrameType

   Type-safe pandas DataFrame with schema validation.

   **Capabilities:**
   
   - Column type validation
   - Missing value handling
   - Schema evolution
   - Performance optimization
   
   .. code-block:: python

      from happy_core.types import DataFrameType, validate_schema
      
      @validate_schema
      def process_data(df: DataFrameType) -> DataFrameType:
          """Process DataFrame with schema validation."""
          return df.transform({
              "numeric_col": "float64",
              "date_col": "datetime64[ns]"
          })

Type Validators
-------------

validate_json
~~~~~~~~~~~

.. py:decorator:: validate_json

   JSON schema validation decorator.

   **Features:**
   
   - Schema validation
   - Custom error messages
   - Performance caching
   - Partial validation
   
   .. code-block:: python

      from happy_core.types import validate_json
      
      schema = {
          "type": "object",
          "properties": {
              "name": {"type": "string"},
              "age": {"type": "integer", "minimum": 0}
          }
      }
      
      @validate_json(schema)
      def create_user(user_data: JsonDict) -> JsonDict:
          return user_data

validate_schema
~~~~~~~~~~~~~

.. py:decorator:: validate_schema

   DataFrame schema validation decorator.

   **Capabilities:**
   
   - Column type checking
   - Missing value validation
   - Custom validation rules
   - Performance optimization
   
   .. code-block:: python

      from happy_core.types import validate_schema
      
      schema = {
          "columns": {
              "user_id": "int64",
              "name": "string",
              "signup_date": "datetime64[ns]"
          },
          "index": {"name": "user_id", "unique": True}
      }
      
      @validate_schema(schema)
      def process_users(df: DataFrameType) -> DataFrameType:
          return df.sort_values("signup_date")

Type Conversion
-------------

TypeConverter
~~~~~~~~~~~

.. py:class:: TypeConverter

   Flexible type conversion utility.

   **Features:**
   
   - Safe type conversion
   - Custom conversion rules
   - Batch conversion
   - Error handling
   
   .. code-block:: python

      from happy_core.types import TypeConverter
      
      converter = TypeConverter()
      
      # Register custom conversion
      @converter.register(source=str, target=datetime)
      def str_to_datetime(value: str) -> datetime:
          return datetime.strptime(value, "%Y-%m-%d")
      
      # Use conversion
      date = converter.convert("2024-01-01", target=datetime)

Best Practices
------------

1. **Type Validation**

   Always validate input data:

   .. code-block:: python

      # Good - explicit validation
      @validate_json(schema)
      def process_data(data: JsonDict) -> JsonDict:
          return transform_data(data)
      
      # Bad - no validation
      def process_data(data: dict) -> dict:
          return transform_data(data)

2. **Schema Definition**

   Define clear and specific schemas:

   .. code-block:: python

      # Good - specific schema
      schema = {
          "type": "object",
          "required": ["name", "age"],
          "properties": {
              "name": {"type": "string", "minLength": 1},
              "age": {"type": "integer", "minimum": 0}
          }
      }
      
      # Bad - too permissive
      schema = {"type": "object"}

3. **Type Conversion**

   Use safe type conversion:

   .. code-block:: python

      # Good - safe conversion
      try:
          value = TypeConverter.safe_convert(input_value, target_type)
      except ConversionError:
          handle_error()
      
      # Bad - unsafe conversion
      value = target_type(input_value)

Advanced Usage
------------

1. **Custom Type Definitions**

   Create domain-specific types:

   .. code-block:: python

      from happy_core.types import CustomType, validate_type
      
      class EmailType(CustomType):
          def validate(self, value: str) -> bool:
              return bool(re.match(r"[^@]+@[^@]+\.[^@]+", value))
          
          def clean(self, value: str) -> str:
              return value.lower().strip()
      
      @validate_type(email=EmailType())
      def create_user(email: str) -> dict:
          return {"email": email}

2. **Complex Validation**

   Implement advanced validation rules:

   .. code-block:: python

      class DataValidator:
          def __init__(self, schema: dict):
              self.schema = schema
              self.validators = []
          
          def add_rule(self, rule_func):
              self.validators.append(rule_func)
              return self
          
          def validate(self, data: Any) -> bool:
              return all(v(data) for v in self.validators)

3. **Type Introspection**

   Utilize type information:

   .. code-block:: python

      class TypeInspector:
          @classmethod
          def get_type_info(cls, obj: Any) -> dict:
              """Extract type information."""
              return {
                  "type": type(obj).__name__,
                  "attributes": cls._get_attributes(obj),
                  "methods": cls._get_methods(obj)
              }
          
          @classmethod
          def _get_attributes(cls, obj: Any) -> dict:
              return {
                  name: type(value).__name__
                  for name, value in vars(obj).items()
              }
          
          @classmethod
          def _get_methods(cls, obj: Any) -> list:
              return [
                  name for name, value in vars(type(obj)).items()
                  if callable(value)
              ]
