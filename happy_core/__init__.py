"""
Happy Core
~~~~~~~~~~

A comprehensive utility toolkit designed for Python developers
seeking clean, efficient, and maintainable solutions.
"""
from happy_core.toolkits import *

__title__ = "happy_core"
__version__ = "0.1.1"
__author__ = "alaamer12"
__author_email__ = "ahmedmuhmmed239@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024 alaamer12"
__description__ = "A boilerplate utility package"
__url__ = "https://github.com/alaamer12/happy"
__keywords__ = [
    "boilerplate",
    "utility",
    "package",
    "happy_core",
    "python",
    "python3",
    "time",
    "date",
    "datetime",
    "dummy",
    "profile",
    "debug",
    "log",
    "logging",
    "master",
    "re",
    "types",
    "hint",
]

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__description__",
    "__url__",
    "__keywords__",
    "get_version",
    "get_author",
    "get_description",
]

# Version information tuple
VERSION = tuple(map(int, __version__.split(".")))

# Package type hints
from typing import Tuple, List

__version_info__: Tuple[int, ...] = VERSION
__keywords_list__: List[str] = __keywords__


def get_version() -> str:
    """Return the version of happy_core."""
    return __version__


def get_author() -> str:
    """Return the author of happy_core."""
    return __author__


def get_description() -> str:
    """Return the description of happy_core."""
    return __description__
