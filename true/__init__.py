"""
True Core
~~~~~~~~~~

A comprehensive utility toolkit designed for Python developers
seeking clean, efficient, and maintainable solutions.
"""

__title__ = "true"
__version__ = "0.2.0"
__author__ = "alaamer12"
__author_email__ = "ahmedmuhmmed239@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025 alaamer12"
__description__ = "A boilerplate utility package"
__url__ = "https://github.com/alaamer12/true"
__keywords__ = [
    "boilerplate",
    "utility",
    "package",
    "true",
    "python",
    "python3",
    "time",
    "date",
    "datetime",
    "dummy",
    "profile",
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


def get_version() -> str:
    """Return the version of true."""
    return __version__


def get_author() -> str:
    """Return the author of true."""
    return __author__


def get_description() -> str:
    """Return the description of true."""
    return __description__


def __dir__():
    """Return a sorted list of names in this module."""
    return sorted(__all__)
