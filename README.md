# Happy Core

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![PyPI version](https://badge.fury.io/py/happy-core.svg)](https://badge.fury.io/py/happy-core)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/build/html/index.html)

<p align="center">
  <img src="https://raw.githubusercontent.com/alaamer12/happy/main/docs/source/_static/logo.png" alt="Happy Core Logo" width="200"/>
</p>

A comprehensive utility toolkit designed for Python developers seeking clean, efficient, and maintainable solutions.

[Documentation](docs/build/html/index.html) |
[PyPI Package](https://pypi.org/project/happy-core/) |
[Issue Tracker](https://github.com/alaamer12/happy/issues)

</div>

---

## 🚀 Quick Start

```bash
pip install happy_core
```

```python
from happy_core.toolkits import simple_debugger
from happy_core.collections import Directory

# Quick example
simple_debugger("Starting application...")
work_dir = Directory("./workspace")
```

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Documentation](#-documentation)
- [Module Overview](#-module-overview)
- [Usage Examples](#-usage-examples)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🛡 Robust Error Handling**
  - Comprehensive exception hierarchy
  - Custom exception classes
  - Error recovery mechanisms

- **📝 Advanced Logging**
  - Built on top of `loguru`
  - Configurable logging strategies
  - Console and file logging support

- **🔧 Developer Tools**
  - Performance profiling
  - Debugging utilities
  - Type checking helpers
  - Retry mechanisms

- **⚡ High Performance**
  - Optimized collections
  - Efficient file operations
  - Smart caching capabilities

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip or poetry (recommended)

```bash
# Using pip
pip install happy_core

# Using poetry
poetry add happy_core

# From source
git clone https://github.com/alaamer12/happy.git
cd happy_core
pip install -r requirements.txt
```

## 📚 Documentation

Comprehensive documentation is available in multiple formats:

- [Online Documentation](docs/build/html/index.html)
- [API Reference](docs/build/html/api_reference.html)
- [Module Documentation](docs/build/html/modules.html)
- [Examples](docs/build/html/examples.html)

## 🔍 Module Overview

### Core Components

```python
# Logging
from happy_core.log import ConsoleLogger
logger = ConsoleLogger.get_logger()

# File Operations
from happy_core.collections import File, Directory
workspace = Directory("./workspace")

# Error Handling
from happy_core.exceptions import ValidationError
try:
    # Your code here
except ValidationError as e:
    logger.error(f"Validation failed: {e}")

# Performance Monitoring
from happy_core.toolkits import profile, monitor
@profile
def expensive_operation():
    pass
```

### Available Modules

- **collections**: File system operations and data structures
- **exceptions**: Comprehensive error handling
- **log**: Advanced logging capabilities
- **toolkits**: Developer utilities and helpers
- **types**: Type definitions and validation
- **time**: Time manipulation utilities

## 🚀 Usage Examples

### Error Handling

```python
from happy_core.exceptions import FileNotFoundError
from happy_core.collections import File

def read_secure_file(path: str) -> str:
    try:
        file = File(path)
        return file.read_text()
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return ""
```

### Performance Monitoring

```python
from happy_core.toolkits import monitor

@monitor
def process_data(items: list):
    for item in items:
        # Processing logic here
        pass
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/alaamer12/happy.git
cd happy_core

# Install dependencies with poetry
poetry install

# Run tests
poetry run pytest
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

<div align="center">

Made with ❤️ by [Happy Core Team](https://github.com/alaamer12)

</div>
