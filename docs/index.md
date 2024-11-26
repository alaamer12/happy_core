# Happy Core Documentation

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![PyPI version](https://badge.fury.io/py/happy-core.svg)](https://badge.fury.io/py/happy-core)

A comprehensive utility toolkit designed for Python developers seeking clean, efficient, and maintainable solutions.

</div>

## 📚 Table of Contents

- [Overview](#-overview)
- [Installation](#-installation)
- [Core Components](#-core-components)
  - [File System Operations](#file-system-operations)
  - [Collections](#collections)
  - [Enums and Registry](#enums-and-registry)
  - [Time Utilities](#time-utilities)
  - [Regular Expressions](#regular-expressions)
  - [Types and Toolkits](#types-and-toolkits)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [Contributing](#-contributing)
- [License](#-license)

## 🌟 Overview

Happy Core is a feature-rich Python package that provides a collection of utilities and boilerplate code designed to solve common development challenges. Built with maintainability, extensibility, and clean code principles in mind, it offers a robust foundation for your Python projects.

### Key Benefits

- **🚀 Increased Productivity**: Eliminate repetitive boilerplate code with ready-to-use utilities
- **🛡️ Robust Error Handling**: Built-in retry mechanisms and comprehensive error handling
- **⚡ Performance Optimized**: Efficient implementations with optional caching capabilities
- **📊 Monitoring Ready**: Built-in monitoring decorators for performance tracking
- **🔄 Type Safe**: Full type hint support for better IDE integration
- **📝 Well Documented**: Comprehensive documentation with real-world examples

### Who Should Use Happy Core?

- **Application Developers**: Streamline common tasks like file operations and data processing
- **System Architects**: Build robust, maintainable systems with clean abstractions
- **Data Engineers**: Efficiently process and transform data with built-in utilities
- **DevOps Engineers**: Automate tasks with reliable, well-tested components

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip or poetry (recommended)

### Using pip
```bash
pip install happy-core
```

### Using poetry
```bash
poetry add happy-core
```

### From source
```bash
git clone https://github.com/yourusername/happy-core.git
cd happy-core
pip install -r requirements.txt
```

## 🔧 Core Components

### File System Operations

The file system operations module provides enhanced file and directory management capabilities through several key classes:

#### FileSystemObject
Base class providing common functionality for files and directories.

```python
from happy_core.collections import FileSystemObject

# Create a file system object
fs_obj = FileSystemObject("/path/to/item")

# Access common properties
print(fs_obj.path)
print(fs_obj.exists())
print(fs_obj.name)
```

#### File
Enhanced file operations with additional capabilities.

```python
from happy_core.collections import File

# Create a file object
file = File("/path/to/file.txt")

# File operations
content = file.read_text()
file.write_text("Hello, World!")
file.create_backup()
```

#### Directory
Advanced directory management with recursive operations.

```python
from happy_core.collections import Directory

# Create a directory object
directory = Directory("/path/to/dir")

# Directory operations
directory.create()
directory.zip_contents("output.zip")
tree = directory.get_tree()
```

### Collections

#### RecycleBin
Advanced file recycling system with metadata tracking.

```python
from happy_core.collections import RecycleBin

# Initialize recycle bin
recycler = RecycleBin("/path/to/bin")

# Delete and restore files
item_id = recycler.delete("/path/to/file.txt")
recycler.restore(item_id)

# Manage tags
recycler.add_tag(item_id, "important")
```

### Enums and Registry

The enum system provides enhanced enumeration capabilities with validation and registration.

```python
from happy_core.enum_registry import EnumRegistry

# Create an enum registry
registry = EnumRegistry()

# Register and validate enums
@registry.register
class Status:
    ACTIVE = "active"
    INACTIVE = "inactive"
```

### Time Utilities

Enhanced time manipulation and conversion utilities.

```python
from happy_core.time import TimeConverter

# Convert between time formats
unix_time = TimeConverter.to_unix("2023-01-01 12:00:00")
iso_time = TimeConverter.to_iso(unix_time)
```

### Regular Expressions

Extended regular expression patterns and utilities.

```python
from happy_core.re import RegexPattern

# Use predefined patterns
email_pattern = RegexPattern.EMAIL
is_valid = email_pattern.match("user@example.com")
```

### Types and Toolkits

Various utility functions and type definitions.

```python
from happy_core.toolkits import retry, monitor

# Use decorators
@retry(max_attempts=3)
@monitor
def process_data():
    pass
```

## 📖 API Reference

### File System Module

#### class FileSystemObject
Base class for file system operations.

**Properties:**
- `path`: Get the relative path
- `full_path`: Get the absolute path
- `exists`: Check if the item exists
- `name`: Get the item name
- `parent`: Get the parent directory

**Methods:**
- `clear_cache()`: Clear cached properties
- `get_owner_info()`: Get file owner information

#### class File(FileSystemObject)
Enhanced file operations.

**Properties:**
- `filename`: Get the file name
- `extension`: Get the file extension
- `size`: Get file size
- `md5`: Get MD5 hash
- `mime_type`: Get file MIME type

**Methods:**
- `get_stats()`: Get comprehensive file statistics
- `copy_to(destination, overwrite=False)`: Copy file with retry mechanism
- `create_backup(suffix='.bak')`: Create a backup copy
- `is_text_file()`: Check if file is text
- `read_text(encoding='utf-8')`: Read text content
- `write_text(content, encoding='utf-8')`: Write text content

#### class Directory(FileSystemObject)
Advanced directory management.

**Methods:**
- `size()`: Get cached directory size
- `glob(pattern)`: Pattern matching
- `rglob(pattern)`: Recursive pattern matching
- `create(exist_ok=True)`: Create directory
- `zip_contents(output_path)`: Create ZIP archive
- `get_tree(max_depth=None)`: Get directory structure

#### class RecycleBin
Advanced file recycling system.

**Methods:**
- `delete(path)`: Move item to recycle bin
- `restore(item_id)`: Restore item from recycle bin
- `list_items(pattern=None)`: List recycled items
- `add_tag(item_id, tag)`: Add tag to item
- `remove_tag(item_id, tag)`: Remove tag from item
- `cleanup(days=30)`: Remove old items

### Enum Registry Module

#### class EnumRegistry
Registry for enhanced enumerations.

**Methods:**
- `register(cls)`: Register an enum class
- `validate(value, enum_type)`: Validate enum value
- `get_choices(enum_type)`: Get enum choices

### Time Module

#### class TimeConverter
Time conversion utilities.

**Methods:**
- `to_unix(datetime_str)`: Convert to Unix timestamp
- `to_iso(unix_time)`: Convert to ISO format
- `to_local(utc_time)`: Convert to local time
- `to_utc(local_time)`: Convert to UTC

### Regular Expressions Module

#### class RegexPattern
Common regex patterns and utilities.

**Constants:**
- `EMAIL`: Email validation pattern
- `URL`: URL validation pattern
- `IP_ADDRESS`: IP address pattern
- `PHONE_NUMBER`: Phone number pattern

**Methods:**
- `match(pattern, text)`: Match pattern against text
- `find_all(pattern, text)`: Find all matches
- `replace(pattern, text, replacement)`: Replace matches

## 🎯 Examples

### Basic File Operations
```python
from happy_core.collections import File, Directory

# File operations
file = File("document.txt")
if not file.exists():
    file.write_text("Hello, World!")
    
backup = file.create_backup()
print(f"Backup created at: {backup.path}")

# Directory operations
docs = Directory("documents")
docs.create()
tree = docs.get_tree()
print("Directory structure:", tree)
```

### Using RecycleBin
```python
from happy_core.collections import RecycleBin

with RecycleBin("./recyclebin") as bin:
    # Delete files
    file_id = bin.delete("old_file.txt")
    
    # Add tags
    bin.add_tag(file_id, "archived")
    
    # List items
    items = bin.list_items(pattern="*.txt")
    
    # Restore specific item
    bin.restore(file_id)
```

### Working with Enums
```python
from happy_core.enum_registry import EnumRegistry

registry = EnumRegistry()

@registry.register
class UserStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Validate values
is_valid = registry.validate("active", UserStatus)
choices = registry.get_choices(UserStatus)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- **Report Bugs**: Open an issue describing the bug and how to reproduce it
- **Suggest Features**: Share your ideas for new features or improvements
- **Submit PRs**: Implement new features or fix existing issues
- **Improve Docs**: Help us make the documentation better

See our [Contributing Guide](CONTRIBUTING.md) for more details.

## 📚 References

- [Official Documentation](https://happy-core.readthedocs.io/)
- [GitHub Repository](https://github.com/yourusername/happy-core)
- [PyPI Package](https://pypi.org/project/happy-core/)
- [Change Log](CHANGELOG.md)

## 📄 License

Happy Core is released under the MIT License. See the [LICENSE](LICENSE) file for details.
