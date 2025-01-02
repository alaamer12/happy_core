# True-Core Python Library

A sophisticated Python utility library providing advanced enum management, type validation, time handling, regular expressions, and file operations.

## Core Components

### 1. Collections (`true.collections`)

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

### 2. Time Management (`true.time`)

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

### 3. Regular Expressions (`true.re`)

- **Validation Patterns**:
  - Username validation patterns
  - Password complexity patterns
  - Email format validation
  - Phone number formats
  - Credit card validation
  - URL pattern matching
  - Date format validation
  - IP address validation

### 4. Exception Handling (`true.exceptions`)

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
from true.collections import OSUtils
from true.time import Time, Schedule, Event, TimeUnit
from enum import Enum

# Time Management Example
time = Time.now()
schedule = Schedule()
event = Event(name="Meeting", start_time=time, end_time=time.add(1, TimeUnit.HOURS))
schedule.add_event(event)

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
