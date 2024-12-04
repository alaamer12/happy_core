# True-Core Python Library

A sophisticated Python utility library providing advanced enum management, type validation, time handling, regular expressions, and file operations.

## Core Components

### 1. Enum Management (`true.enum_registry`)
- **EnumRegistry**: Advanced enum combination and management
  - Merge multiple enum classes into a single registry
  - Type-safe operations and validation
  - Metadata support with descriptions, tags, and timestamps
  - Comprehensive filtering capabilities
  - Statistical analysis and serialization

### 2. Enum Toolkits (`true.enums_toolkits`)
- **Specialized Enum Classes**:
  - `DynamicEnum`: Runtime-modifiable enums
  - Type-safe enums: `ByteEnum`, `FloatEnum`, `ComplexNumberEnum`
  - Collection enums: `DictEnum`, `SetEnum`, `ListEnum`, `TupleEnum`
  - Iterator enums: `IterableEnum`, `IteratorEnum`, `GeneratorEnum`
- **Metadata Support**:
  - Custom attribute configuration
  - Type information tracking
  - Serialization capabilities

### 3. Collections (`true.collections`)
- **File System Operations**:
  - Secure file deletion and creation
  - Advanced file metadata handling
  - Cross-platform compatibility
  - File type-specific operations
- **File Management**:
  - RecycleBin with metadata tracking
  - Batch file operations
  - Directory watching
  - File statistics and analysis

### 4. Time Management (`true.time`)
- **Time Handling**:
  - Advanced timezone support
  - Time arithmetic and comparisons
  - Duration calculations
  - Event scheduling
- **Time Features**:
  - Time rounding and formatting
  - Timezone conversions
  - Performance timing decorators
  - Schedule management with conflict detection

### 5. Regular Expressions (`true.re`)
- **Validation Patterns**:
  - Username validation patterns
  - Password complexity patterns
  - Email format validation
  - Phone number formats
  - Credit card validation
  - URL pattern matching
  - Date format validation
  - IP address validation

### 6. Type System (`true.types`)
- **Version Types**:
  - SemVer, CalVer, DateVersion support
  - Version validation and comparison
- **Numeric Types**:
  - `BigInt` and `BigDecimal` with validation
  - Scientific number handling
  - Validated numeric types
- **ID Types**:
  - UUID/ULID support with versions
  - String and integer-based IDs
- **Serialization**:
  - JSON, YAML, TOML support
  - Type conversion utilities

### 7. Exception Handling (`true.exceptions`)
- **Specialized Exceptions**:
  - Enum-related exceptions
  - Type validation errors
  - Schedule management errors
  - File operation errors
  - Access control exceptions
  - Configuration errors

## Installation

```bash
pip install true-core
```

## Quick Start

```python
from true.enum_registry import EnumRegistry
from true.collections import OSUtils
from true.time import Time, Schedule, Event, TimeUnit
from true.types import BigInt, Version
from enum import Enum

# Enum Registry Example
class ColorEnum(Enum):
    RED = 1
    BLUE = 2

registry = EnumRegistry([ColorEnum])
int_values = registry.filter.by_value_type(int)

# Time Management Example
time = Time.now()
schedule = Schedule()
event = Event(name="Meeting", start_time=time, end_time=time.add(1, TimeUnit.HOURS))
schedule.add_event(event)

# Type Validation Example
version = Version("1.2.3")
big_num = BigInt(1000000, context="Positive")

# File Operations Example
utils = OSUtils()
utils.force_delete("path/to/file")  # Secure deletion
utils.watch_directory("path/to/dir", callback=lambda event: print(f"Change: {event.src_path}"))
```

## Requirements

- Python 3.8+
- Platform-specific dependencies:
  - Windows: `pywin32` for advanced file operations
  - Unix: Standard Python libraries
- Optional dependencies:
  - `pytz` for timezone support
  - `pydub` for audio file handling
  - `Pillow` for image processing

## Documentation

For detailed documentation, see [docs](https://true-core.readthedocs.io/en/latest/).

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Author

Alaamer - https://github.com/alaamer12

## Acknowledgments

- [PyPI](https://pypi.org/project/true-core/)
- [GitHub](https://github.com/alaamer12/true-core)
- [Python](https://www.python.org/)