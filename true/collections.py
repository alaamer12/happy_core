"""
Utility module providing collection-related functionality including file creation, recycling bin management,
and enhanced data structures with operator support.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
# noinspection PyCompatibility
import imghdr
import inspect
import json
import logging
import logging.handlers
import mimetypes
import os
import pathlib
import platform
import queue
import shutil
import stat
import tempfile
import threading
import time
import zipfile
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from datetime import timedelta
from functools import lru_cache, wraps
from pathlib import Path
from typing import List, Dict, Union, Optional, Generator, Tuple, Any
from typing import TypeVar, Callable

import pydub.generators
from PIL import Image
from moviepy.editor import ImageSequenceClip, ImageClip
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from true.exceptions import (StorageFullError, RecycleBinError, ItemNotFoundError, RestoreError)
from true.toolkits import retry


T = TypeVar('T')

__all__ = [
    'FileStats', 'File', 'Directory', 'RecycleBin',
]


def _to_numeric(value: Any) -> Union[int, float]:
    """Convert value to a numeric type suitable for bitwise operations"""
    if isinstance(value, bool):
        return int(value)
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot convert string '{value}' to numeric type")
    raise ValueError(f"Cannot convert type {type(value)} to numeric type")


def is_image(path):
    return imghdr.what(path)


def copy_dir(src: Union[str, Path], dst: Union[str, Path], **kwargs: Any) -> None:
    """
    Copy a directory and its contents to a destination.

    Args:
        src: Source directory path
        dst: Destination directory path
        **kwargs: Additional arguments passed to shutil.copytree
    """
    shutil.copytree(src, dst, symlinks=True, copy_function=shutil.copy2, **kwargs)


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """
    Copy a single file to a destination.

    Args:
        src: Source file path
        dst: Destination file path
    """
    shutil.copy(src, dst)


def copy_dir_to_same_depth(src: Union[str, Path], dst: Union[str, Path], **kwargs: Any) -> None:
    """
    Copy a directory to a destination while maintaining the same directory depth structure.

    Args:
        src: Source directory path
        dst: Destination directory path
        **kwargs: Additional arguments passed to shutil.copytree
    """
    _dst = os.path.join(dst, os.path.basename(src))
    os.makedirs(os.path.dirname(_dst), exist_ok=True)
    shutil.copytree(src, _dst, **kwargs)


def _random_color() -> tuple[int, int, int]:
    import random
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def _create_file(filename, header, size, content):
    """
    Internal method to create a dummy file with specified header and size.

    :param filename: Name of the file to create.
    :param header: Header bytes of the file.
    :param size: Total size of the file in bytes.
    :param content: Content to fill the file.
    """
    try:
        with open(filename, 'wb') as f:
            f.write(header)
            remaining_size = size - len(header)
            if remaining_size > 0:
                f.write(content * (remaining_size // len(content)) +
                        content[:remaining_size % len(content)])
    except Exception as e:
        print(f"Failed to create file {filename}: {e}")


class FileCreator(ABC):
    """
    Abstract base class that defines the template for creating a dummy file.
    """

    FILE_HEADERS = {
        '.pdf': b'%PDF-1.4\n%',
        '.epub': b'PK\x03\x04',
        '.docx': b'PK\x03\x04',
        '.xlsx': b'PK\x03\x04',
        '.txt': b'',
        '.jpg': b'\xFF\xD8\xFF',
        '.png': b'\x89PNG\r\n\x1a\n',
        '.gif': b'GIF89a',
        '.zip': b'PK\x03\x04',
        '.mp3': b'ID3',  # MP3 audio file
        '.wav': b'RIFF',  # WAV audio file
        '.mp4': b'ftyp',  # MP4 video file
        '.avi': b'RIFF',  # AVI video file
        '.mkv': b'\x1A\x45\xDF\xA3',  # MKV video file
        '.svg': b'<?xml version="1.0"?>',  # SVG file
        '.bmp': b'BM',  # BMP image file
        '.tiff': b'II*\x00',  # TIFF image file
        '.tar': b'ustar',  # TAR file
        '.rar': b'Rar!',  # RAR file
        '.7z': b'7z\xBC\xAF\x27\x1C',  # 7z file
    }

    def __init__(self, extension, default_size=1024, default_content=None):
        """
        Initialize the FileCreator instance.

        :param extension: File extension including dot (e.g., '.pdf')
        :param default_size: Default size of the dummy file in bytes.
        :param default_content: Default content to fill the dummy file.
        """
        self.extension = extension
        self.default_size = default_size
        self.default_content = default_content or b'0'
        self.created_files = []

    def create_file(self, filename=None, size=None, content=None):
        """
        Template method to create a dummy file.

        :param filename: Name of the file to create.
        :param size: Size of the file in bytes.
        :param content: Content to fill the file.
        """
        filename = filename or self.default_filename
        size = size or self.default_size

        header = self.header
        if callable(header):  # A bug where sometimes returns callable for custom files
            header = header()

        content = content.encode() if isinstance(content, str) else content or self.default_content
        _create_file(filename, header, size, content)
        self.created_files.append(filename)
        print(f"Created dummy file: {filename} ({size} bytes)")

    @property
    def header(self):
        """Get the header bytes for the file type."""
        return self.FILE_HEADERS[self.extension]

    @property
    def default_filename(self):
        """Get the default filename for the file type."""
        return f'dummy{self.extension}'

    def list_created_files(self):
        """
        List all created dummy files.

        :return: List of filenames.
        """
        return self.created_files.copy()

    def reset(self):
        """Reset the list of created files."""
        self.created_files = []

    def __repr__(self):
        return f"<{self.__class__.__name__} created: {len(self.created_files)} files>"

    def __str__(self):
        return f"{self.__class__.__name__} Utility - {len(self.created_files)} files created."


class PDFFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.pdf', default_size, default_content)

    def __repr__(self):
        return f"PDFFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class EPUBFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.epub', default_size, default_content)

    def __repr__(self):
        return f"EPUBFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class DOCXFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.docx', default_size, default_content)

    def __repr__(self):
        return f"DOCXFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class XLSXFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.xlsx', default_size, default_content)

    def __repr__(self):
        return f"XLSXFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class TXTFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.txt', default_size, default_content)

    def create_file(self, filename=None, size=None, content=None):
        """
        Override to handle text content encoding.
        """
        content = content.encode() if isinstance(content, str) else content or self.default_content
        super().create_file(filename, size, content)

    def __repr__(self):
        return f"TXTFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class JPGFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.jpg', default_size, default_content)

    def __repr__(self):
        return f"JPGFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class PNGFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.png', default_size, default_content)

    def __repr__(self):
        return f"PNGFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class GIFFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.gif', default_size, default_content)

    def __repr__(self):
        return f"GIFFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class ZIPFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.zip', default_size, default_content)

    def __repr__(self):
        return f"ZIPFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class TarFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.tar', default_size, default_content)

    def __repr__(self):
        return f"TarFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class Mp3FileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.mp3', default_size, default_content)

    def __repr__(self):
        return f"Mp3FileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class WavFileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.wav', default_size, default_content)

    def __repr__(self):
        return f"WavFileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class Mp4FileCreator(FileCreator):
    def __init__(self, default_size=1024, default_content=None):
        super().__init__('.mp4', default_size, default_content)

    def __repr__(self):
        return f"Mp4FileCreator(default_size={self.default_size}, files_created={len(self.created_files)})"


class DummyFile:
    """
    A class to manage the creation out for various types of dummy files using the Template Pattern.
    """

    def __init__(self, default_size=1024, default_content=None):
        self.default_size = default_size
        self.default_content = default_content or b'0'
        self.created_files = []

        # Mapping extensions to their respective creators
        self.creators = {
            '.pdf': PDFFileCreator(default_size, default_content),
            '.epub': EPUBFileCreator(default_size, default_content),
            '.docx': DOCXFileCreator(default_size, default_content),
            '.xlsx': XLSXFileCreator(default_size, default_content),
            '.txt': TXTFileCreator(default_size, default_content),
            '.jpg': JPGFileCreator(default_size, default_content),
            '.png': PNGFileCreator(default_size, default_content),
            '.gif': GIFFileCreator(default_size, default_content),
            '.zip': ZIPFileCreator(default_size, default_content),
            # Add more creators as needed
        }

    def create_file(self, extension, filename=None, size=None, content=None):
        """
        Generic method to create a dummy file based on the extension.

        :param extension: File extension (e.g., '.pdf').
        :param filename: Name of the file to create.
        :param size: Size of the file in bytes.
        :param content: Content to fill the file.
        """
        creator = self.creators.get(extension)
        if not creator:
            print(f"No creator available for extension '{extension}'.")
            return
        creator.create_file(filename, size, content)
        self.created_files.extend(creator.created_files)

    def custom_file(self, filename, extension, header=None, size=None, content=None):
        """
        Create a custom dummy file.

        :param filename: Name of the file.
        :param extension: File extension (e.g., '.custom').
        :param header: Custom header bytes.
        :param size: Size of the file in bytes.
        :param content: Custom content to fill the file.
        """

        class CustomFileCreator(FileCreator):
            def get_header_inner(self):
                return header or self.FILE_HEADERS.get(extension, b'')

            def header(self):
                return self.get_header_inner()

            def default_filename(self):
                return filename

        custom_creator = CustomFileCreator(self.default_size, self.default_content)
        custom_creator.FILE_HEADERS[extension] = header or b''
        custom_creator.create_file(filename, size, content)
        self.created_files.extend(custom_creator.created_files)

    def reset(self):
        """
        Reset the list of created files.
        """
        self.created_files = []
        for creator in self.creators.values():
            creator.reset()
        print("Reset the list of created files.")

    @staticmethod
    def create_image(output_path):
        color = _random_color()
        img = Image.new('RGB', (100, 100), color=color)  # Create images with varying shades of red
        img.save(output_path)  # Save images as PNG files

    def create_video(self, output_path, sequence_dir=None, codec="libx264", fps=10):
        images = [file for file in os.listdir(sequence_dir) if is_image(os.path.join(sequence_dir, file))]
        temp_dir = os.path.join(os.getcwd(), "temp")

        if not images or sequence_dir is None:
            for i in range(10):
                path = os.path.join(temp_dir, f"image_{i:03d}.png")
                self.create_image(path)
                images.append(path)
        clip = ImageSequenceClip(images, fps=fps)
        clip.write_videofile(output_path, codec=codec)

        # Cleanup
        os.removedirs(temp_dir)

    @staticmethod
    def create_static_video(image_path, output_path, codec="libx264", duration=5):
        # Load the image and set its duration
        clip = ImageClip(image_path).set_duration(duration)
        clip.write_videofile(output_path, codec=codec)

    @staticmethod
    def create_audio(filename, duration=3000, frequency=440):
        # Generate a sine wave of specified frequency and duration (in milliseconds)
        audio = pydub.generators.Sine(frequency).to_audio_segment(duration=duration)
        # Export the audio to the specified format
        audio.export(filename, format=filename.split('.')[-1])

    def __repr__(self):
        total_files = sum(len(creator.created_files) for creator in self.creators.values())
        return f"<DummyFile created: {total_files} files>"

    def __str__(self):
        total_files = sum(len(creator.created_files) for creator in self.creators.values())
        return f"DummyFile Utility - {total_files} files created."


class LazyDescriptor:
    """Descriptor that implements lazy evaluation of class attributes."""

    def __init__(self, func: Callable[..., T]) -> None:
        self.func = func
        self.name = func.__name__
        self.cache_name = f'_lazy_{func.__name__}'

    def __get__(self, instance: Any, owner: Any) -> T:
        if instance is None:
            return self

        # Check if we've already computed and cached the value
        if not hasattr(instance, self.cache_name):
            # Compute and cache the value
            result = self.func(instance)
            setattr(instance, self.cache_name, result)

        return getattr(instance, self.cache_name)


def lazy_method(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that makes a method or property lazy-evaluated.
    The result is computed only once and then cached.
    """
    if inspect.iscoroutinefunction(func):
        raise TypeError("Async functions are not supported")

    @wraps(func)
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> T:
        cache_name = f'_lazy_{func.__name__}'

        if not hasattr(self, cache_name):
            result = func(self, *args, **kwargs)
            setattr(self, cache_name, result)

        return getattr(self, cache_name)

    return wrapped


class LazyMetaClass(type):
    """
    Metaclass that enables lazy evaluation of class attributes and methods.
    Methods decorated with @lazy_method will only be evaluated once when first accessed.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        # Transform methods marked with @lazy_method into LazyDescriptor instances
        for key, value in namespace.items():
            if hasattr(value, '_lazy'):
                namespace[key] = LazyDescriptor(value)

        return super().__new__(mcs, name, bases, namespace)


@dataclass
class FileMetadata:
    """Store metadata for recycled files."""
    original_path: str
    deletion_date: datetime
    size: int
    checksum: str
    tags: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            'original_path': self.original_path,
            'deletion_date': self.deletion_date.isoformat(),
            'size': self.size,
            'checksum': self.checksum,
            'tags': self.tags or []
        }


class RecycleBinManager:
    """Singleton manager for recyclebin instances."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        self.bins: Dict[str, 'RecycleBin'] = {}
        self.max_bins = 5


class AbstractRecycleBin(ABC):
    """Abstract base class defining RecycleBin interface."""

    @abstractmethod
    def delete(self, path: str) -> None:
        """Move item to recycle bin."""
        pass

    @abstractmethod
    def restore(self, item_id: str) -> None:
        """Restore item from recycle bin."""
        pass


class RecycleBin(AbstractRecycleBin):
    """Advanced RecycleBin implementation with extensive features."""

    def __init__(self, location: str, max_size: int = 1024 * 1024 * 1024):
        """
        Initialize RecycleBin.

        Args:
            location: Base directory for the recycle bin
            max_size: Maximum size in bytes (default 1GB)
        """
        self.location = Path(location)
        self.max_size = max_size
        self.metadata_file = self.location / "metadata.json"
        self.items: Dict[str, FileMetadata] = {}
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self._setup()

        # Thread pool for parallel operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        # Process pool for CPU-intensive operations
        self.process_pool = ProcessPoolExecutor(max_workers=2)

        # Queue for job handling
        self.job_queue = queue.PriorityQueue()
        self._start_job_handler()

    def _setup(self) -> None:
        """Initialize recycle bin directory structure."""
        self.location.mkdir(parents=True, exist_ok=True)
        if self.metadata_file.exists():
            self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                self.items = {
                    k: FileMetadata(
                        original_path=v['original_path'],
                        deletion_date=datetime.fromisoformat(v['deletion_date']),
                        size=v['size'],
                        checksum=v['checksum'],
                        tags=v['tags']
                    ) for k, v in data.items()
                }
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
            self.items = {}

    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        with self._lock:
            try:
                with open(self.metadata_file, 'w') as f:
                    json.dump({k: v.to_dict() for k, v in self.items.items()}, f)
            except Exception as e:
                self.logger.error(f"Failed to save metadata: {e}")

    def get_total_size(self) -> int:
        """Get total size of items in recycle bin."""
        return sum(item.size for item in self.items.values())

    def delete(self, path: str) -> str:
        """
        Move item to recycle bin.

        Args:
            path: Path to item to be deleted

        Returns:
            str: Item ID in recycle bin

        Raises:
            StorageFullError: If recycle bin is full
            FileNotFoundError: If item doesn't exist
        """
        with self._lock:
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"Item not found: {path}")

            size = path.stat().st_size if path.is_file() else sum(
                f.stat().st_size for f in path.rglob('*') if f.is_file()
            )
            total_size = self.get_total_size() + size
            if total_size > self.max_size:
                raise StorageFullError("Recycle bin storage limit exceeded")

            item_id = datetime.now().strftime('%Y%m%d_%H%M%S_') + path.name
            target = self.location / item_id

            try:
                shutil.move(str(path), str(target))
                metadata = FileMetadata(
                    original_path=str(path),
                    deletion_date=datetime.now(),
                    size=size,
                    checksum=self._calculate_checksum(target),
                    tags=[]
                )
                self.items[item_id] = metadata
                self._save_metadata()
                return item_id
            except Exception as e:
                self.logger.error(f"Failed to delete item: {e}")
                raise RecycleBinError(f"Failed to delete item: {e}")

    async def async_delete(self, path: str) -> str:
        """Asynchronous version of delete operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, self.delete, path)

    def restore(self, item_id: str) -> None:
        """
        Restore item from recycle bin.

        Args:
            item_id: ID of item to restore

        Raises:
            ItemNotFoundError: If item not found in recycle bin
            RestoreError: If restoration fails
        """
        with self._lock:
            if item_id not in self.items:
                raise ItemNotFoundError(f"Item not found: {item_id}")

            metadata = self.items[item_id]
            source = self.location / item_id
            target = Path(metadata.original_path)

            try:
                if target.exists():
                    raise RestoreError(f"Target path already exists: {target}")

                shutil.move(str(source), str(target))
                del self.items[item_id]
                self._save_metadata()
            except Exception as e:
                self.logger.error(f"Failed to restore item: {e}")
                raise RestoreError(f"Failed to restore item: {e}")

    async def async_restore(self, item_id: str) -> None:
        """Asynchronous version of restore operation."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.thread_pool, self.restore, item_id)

    @staticmethod
    def _calculate_checksum(path: Path) -> str:
        """Calculate file checksum."""
        import hashlib
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def list_items(self, pattern: str = None) -> Generator[FileMetadata, None, None]:
        """List items in recycle bin with optional pattern matching."""
        for item_id, metadata in self.items.items():
            if not pattern or pattern in item_id:
                yield metadata

    def add_tag(self, item_id: str, tag: str) -> None:
        """Add tag to item."""
        with self._lock:
            if item_id not in self.items:
                raise ItemNotFoundError(f"Item not found: {item_id}")
            if self.items[item_id].tags is None:
                self.items[item_id].tags = []
            self.items[item_id].tags.append(tag)
            self._save_metadata()

    def remove_tag(self, item_id: str, tag: str) -> None:
        """Remove tag from item."""
        with self._lock:
            if item_id not in self.items:
                raise ItemNotFoundError(f"Item not found: {item_id}")
            if tag in self.items[item_id].tags:
                self.items[item_id].tags.remove(tag)
                self._save_metadata()

    def cleanup(self, days: int = 30) -> None:
        """Remove items older than specified days."""
        threshold = datetime.now() - timedelta(days=days)
        with self._lock:
            for item_id, metadata in list(self.items.items()):
                if metadata.deletion_date < threshold:
                    self._permanent_delete(item_id)

    def _permanent_delete(self, item_id: str) -> None:
        """Permanently delete item from recycle bin."""
        with self._lock:
            if item_id not in self.items:
                raise ItemNotFoundError(f"Item not found: {item_id}")

            path = self.location / item_id
            try:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                del self.items[item_id]
                self._save_metadata()
            except Exception as e:
                self.logger.error(f"Failed to permanently delete item: {e}")
                raise RecycleBinError(f"Failed to permanently delete item: {e}")

    def _start_job_handler(self) -> None:
        """Start background job handler thread."""

        def job_handler():
            while True:
                try:
                    priority, job = self.job_queue.get()
                    job()
                except Exception as e:
                    self.logger.error(f"Job handler error: {e}")
                finally:
                    self.job_queue.task_done()

        thread = threading.Thread(target=job_handler, daemon=True)
        thread.start()

    @contextmanager
    def batch_operation(self):
        """Context manager for batch operations."""
        try:
            with self._lock:
                yield
        finally:
            self._save_metadata()

    @asynccontextmanager
    async def async_batch_operation(self):
        """Async context manager for batch operations."""
        try:
            with self._lock:
                yield
        finally:
            self._save_metadata()

    def __str__(self) -> str:
        """String representation."""
        return f"RecycleBin(location='{self.location}', items={len(self.items)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"RecycleBin(location='{self.location}', max_size={self.max_size}, items={len(self.items)})"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


@dataclass
class FileStats:
    """Enhanced data class to hold file statistics"""
    size: int
    created: datetime
    modified: datetime
    accessed: datetime
    permissions: str
    is_hidden: bool
    mime_type: str
    owner: str
    group: str
    is_symlink: bool
    symlink_target: Optional[str]
    md5_hash: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert stats to dictionary format"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'FileStats':
        """Create FileStats instance from dictionary"""
        return cls(**data)


class FileSystemObject:
    """Enhanced base class for file system objects"""

    def __init__(self, path: str, base_path: str = None):
        self._md5 = hashlib.md5()
        self._path = path
        self._base_path = base_path or os.getcwd()
        self._full_path = os.path.join(self._base_path, path) if not os.path.isabs(path) else path
        self._stats_cache = {}

    @property
    def path(self) -> str:
        return self._path

    @property
    def full_path(self) -> str:
        return self._full_path

    @property
    def exists(self) -> bool:
        return os.path.exists(self.full_path)

    @property
    def name(self) -> str:
        return os.path.basename(self.full_path)

    @property
    def parent(self) -> str:
        return os.path.dirname(self.full_path)

    def clear_cache(self):
        """Clear cached properties"""
        self._stats_cache.clear()

    def get_owner_info(self) -> Tuple[str, str]:
        """Get file owner and group information"""
        try:
            import pwd
            import grp
            stat_info = os.stat(self.full_path)
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name
            return owner, group
        except (ImportError, KeyError):
            return "unknown", "unknown"


class File(FileSystemObject):
    """Enhanced file class with additional capabilities"""

    def __init__(self, path: str, base_path: str = None):
        super().__init__(path, base_path)
        self._mime_type = None

    @property
    def filename(self) -> str:
        return os.path.splitext(self.name)[0]

    @property
    def extension(self) -> str:
        return os.path.splitext(self.name)[1].lower()

    @property
    def size(self) -> int:
        return os.path.getsize(self.full_path) if self.exists else 0

    @property
    @lru_cache(maxsize=128)
    def md5(self) -> str:
        if not self.exists:
            return ""
        hash_md5 = hashlib.md5()
        with open(self.full_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @property
    def mime_type(self) -> str:
        """Get file MIME type"""
        if self._mime_type is None:
            self._mime_type = mimetypes.guess_type(self.full_path)[0] or "application/octet-stream"
        return self._mime_type

    def get_stats(self) -> FileStats:
        """Get comprehensive file statistics"""
        stats = os.stat(self.full_path, follow_symlinks=False)
        is_symlink = os.path.islink(self.full_path)
        owner, group = self.get_owner_info()

        return FileStats(
            size=stats.st_size,
            created=datetime.fromtimestamp(stats.st_ctime),
            modified=datetime.fromtimestamp(stats.st_mtime),
            accessed=datetime.fromtimestamp(stats.st_atime),
            permissions=stat.filemode(stats.st_mode),
            is_hidden=self.name.startswith('.') or bool(stats.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            if os.name == 'nt' else self.name.startswith('.'),
            mime_type=self.mime_type,
            owner=owner,
            group=group,
            is_symlink=is_symlink,
            symlink_target=os.readlink(self.full_path) if is_symlink else None,
            md5_hash=self.md5
        )

    @retry(Exception, max_attempts=3, delay=1)
    def copy_to(self, destination: str, overwrite: bool = False) -> bool:
        """Copy file to destination with retry mechanism"""
        dest_path = os.path.join(self._base_path, destination)
        if os.path.exists(dest_path) and not overwrite:
            return False
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(self.full_path, dest_path)
        return True

    def create_backup(self, suffix: str = '.bak') -> 'File':
        """Create a backup copy of the file"""
        backup_path = f"{self.full_path}{suffix}"
        shutil.copy2(self.full_path, backup_path)
        return File(backup_path)

    def is_text_file(self) -> bool:
        """Check if file is a text file"""
        return self.mime_type.startswith('text/') or self.extension in {'.txt', '.md', '.py', '.json'}

    def read_text(self, encoding: str = 'utf-8') -> str:
        """Read text file content"""
        # Define common text file extensions
        text_extensions = {
            '.txt', '.md', '.py', '.json', '.csv', '.log', '.xml', '.yml',
            '.yaml', '.ini', '.cfg', '.conf', '.html', '.css', '.js',
            '.bak', '.backup', '.tmp', '.text'
        }

        if not (self.is_text_file() or self.extension in text_extensions):
            raise ValueError(f"Not a recognized text file: {self.full_path}")

        try:
            with open(self.full_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(self.full_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Failed to read file: {str(e)}")

    def write_text(self, content: str, encoding: str = 'utf-8') -> int:
        """Write text to file"""
        with open(self.full_path, 'w', encoding=encoding) as f:
            return f.write(content)


class Directory(FileSystemObject):
    """Enhanced directory class with additional capabilities"""

    def __init__(self, path: str, base_path: str = None):
        super().__init__(path, base_path)
        self._size_cache = None
        self._size_cache_time = 0
        self._size_cache_duration = 300  # 5 minutes

    @property
    def size(self) -> int:
        """Get cached directory size with automatic refresh"""
        current_time = time.time()
        if (self._size_cache is None or
                current_time - self._size_cache_time > self._size_cache_duration):
            self._size_cache = self._calculate_size()
            self._size_cache_time = current_time
        return self._size_cache

    def _calculate_size(self) -> int:
        """Calculate total directory size"""
        total_size = 0
        if not self.exists:
            return total_size

        for dirpath, _, filenames in os.walk(self.full_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    continue
        return total_size

    def glob(self, pattern: str) -> Generator[pathlib.Path, None, None]:
        return pathlib.Path(self.full_path).glob(pattern)

    def rglob(self, pattern: str) -> Generator[pathlib.Path, None, None]:
        return pathlib.Path(self.full_path).rglob(pattern)

    def create(self, exist_ok: bool = True) -> bool:
        """Create directory if it doesn't exist"""
        try:
            os.makedirs(self.full_path, exist_ok=exist_ok)
            return True
        except FileExistsError:
            return False

    def zip_contents(self, output_path: str, compression: int = zipfile.ZIP_DEFLATED) -> bool:
        """Create a zip archive of directory contents"""
        try:
            with zipfile.ZipFile(output_path, 'w', compression=compression) as zipf:
                for root, _, files in os.walk(self.full_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.full_path)
                        zipf.write(file_path, arcname)
            return True
        except OSError:
            return False

    def get_tree(self, max_depth: int = None) -> Dict[str, Any]:
        """Get directory structure as a nested dictionary"""

        def _build_tree(path: str, current_depth: int = 0) -> Dict[str, Any]:
            if max_depth is not None and current_depth > max_depth:
                return {}

            result = {}
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        result[item] = _build_tree(item_path, current_depth + 1)
                    else:
                        result[item] = File(item_path).size
            except PermissionError:
                return {"error": "Permission denied"}
            return result

        return _build_tree(self.full_path)


class FileSystemEventHandlerWithCallback(FileSystemEventHandler):
    """Custom event handler for directory watching"""

    def __init__(self, callback):
        self.callback = callback
        super().__init__()

    def on_any_event(self, event):
        if not event.is_directory:
            self.callback(event)


def create_temp_file(suffix: str = None) -> File:
    """Create a temporary file and return File object"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return File(path)


def create_temp_directory() -> Directory:
    """Create a temporary directory and return Directory object"""
    temp_dir = tempfile.mkdtemp(prefix='osutils_')
    return Directory(temp_dir)


class OSUtils:
    """Enhanced OS utility class with comprehensive file system operations"""

    def __init__(self, base_path: str = None, max_workers: int = 4):
        self.base_path = os.path.abspath(base_path) if base_path else os.getcwd()
        self._setup_logging()
        self.operation_history = []
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._watch_handlers = {}
        self._observer = Observer()
        self._observer.start()

    def _setup_logging(self):
        """Configure logging with rotation"""
        self.logger = logging.getLogger(__name__)
        handler = logging.handlers.RotatingFileHandler(
            'osutils.log', maxBytes=1024 * 1024, backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_file(self, path: str) -> File:
        return File(path, self.base_path)

    def get_directory(self, path: str) -> Directory:
        return Directory(path, self.base_path)

    @retry(Exception, max_attempts=3, delay=1)
    def safe_move(self, src: str, dst: str, overwrite: bool = False) -> bool:
        """Safely move a file or directory with retry mechanism"""
        try:
            src_path = self.get_file(src).full_path
            dst_path = self.get_file(dst).full_path

            if os.path.exists(dst_path):
                if not overwrite:
                    self.logger.warning(f"Destination {dst} already exists and overwrite is False")
                    return False
                if os.path.isfile(dst_path):
                    os.remove(dst_path)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)

            self._log_operation('move', {
                'source': src,
                'destination': dst,
                'overwrite': overwrite
            })
            return True
        except Exception as e:
            self.logger.error(f"Error moving {src} to {dst}: {str(e)}")
            return False

    def batch_process(self, file_list: List[str], operation: callable,
                      parallel: bool = True) -> Dict[str, bool]:
        """Process multiple files in parallel or sequentially"""
        results = {}

        if parallel:
            futures = {
                file_path: self.thread_pool.submit(operation, file_path)
                for file_path in file_list
            }
            for file_path, future in futures.items():
                try:
                    results[file_path] = future.result()
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    results[file_path] = False
        else:
            for file_path in file_list:
                try:
                    results[file_path] = operation(file_path)
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    results[file_path] = False

        return results

    def watch_directory(self, directory: str, callback: callable) -> None:
        """
        Watch a directory for changes and call callback on file events.

        Args:
            directory: Directory path to watch
            callback: Function to call when changes occur
        """
        dir_path = self.get_directory(directory).full_path
        handler = FileSystemEventHandlerWithCallback(callback)
        self._watch_handlers[directory] = handler
        self._observer.schedule(handler, dir_path, recursive=True)

    def stop_watching(self, directory: str = None) -> None:
        """Stop watching a specific directory or all directories"""
        if directory:
            if directory in self._watch_handlers:
                self._observer.unschedule(self._watch_handlers[directory])
                del self._watch_handlers[directory]
        else:
            self._observer.unschedule_all()
            self._watch_handlers.clear()

    def safe_delete(self, path: str, secure: bool = False) -> bool:
        """
        Safely delete a file or directory with optional secure deletion.

        Args:
            path: Path to delete
            secure: If True, overwrite file contents before deletion
        """
        try:
            full_path = os.path.join(self.base_path, path)
            if os.path.isfile(full_path):
                if secure:
                    self._secure_delete_file(full_path)
                else:
                    os.unlink(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)

            self._log_operation('delete', {
                'path': path,
                'secure': secure
            })
            return True
        except Exception as e:
            self.logger.error(f"Error deleting {path}: {str(e)}")
            return False

    def force_delete(self, path: str) -> bool:
        """
        Forcefully delete a file or directory, using extreme measures for both Unix and Windows.

        Args:
            path (str): Path to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            full_path = os.path.join(self.base_path, path)
            if not os.path.exists(full_path):
                return True

            if platform.system() == "Windows":
                self._force_delete_windows(full_path)
            else:
                self._force_delete_unix(full_path)

            self._log_operation('force_delete', {'path': path})
            return True
        except Exception as e:
            self.logger.error(f"Error force deleting {path}: {str(e)}")
            return False

    def _force_delete_windows(self, path: str) -> None:
        try:
            import win32con
            import win32file
        except ImportError:
            raise ImportError("Install windows api to force deleting.")

        if os.path.isfile(path):
            win32file.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_NORMAL)
            os.chmod(path, 0o777)
            os.unlink(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files + dirs:
                    self._force_delete_windows(os.path.join(root, name))
            os.rmdir(path)

    @staticmethod
    def _force_delete_unix(path: str) -> None:
        if os.path.isfile(path):
            os.chmod(path, 0o777)
            os.unlink(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files + dirs:
                    item_path = os.path.join(root, name)
                    os.chmod(item_path, 0o777)
                    os.remove(item_path) if os.path.isfile(item_path) else os.rmdir(item_path)
            os.rmdir(path)

    @staticmethod
    def _secure_delete_file(path: str, passes: int = 3) -> None:
        """Securely delete a file by overwriting its contents"""
        if not os.path.exists(path):
            return

        file_size = os.path.getsize(path)
        with open(path, "wb") as f:
            for _ in range(passes):
                # Overwrite with random data
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

                # Overwrite with zeros
                f.seek(0)
                f.write(b'\x00' * file_size)
                f.flush()
                os.fsync(f.fileno())

        os.unlink(path)

    def find_files_by_date(self, directory: str,
                           start_date: datetime = None,
                           end_date: datetime = None,
                           modified: bool = True) -> List[str]:
        """
        Find files within a date range.

        Args:
            directory: Directory to search
            start_date: Start date for search
            end_date: End date for search
            modified: If True, use modification date, else creation date
        """
        found_files = []
        dir_obj = self.get_directory(directory)

        for file_path in dir_obj.rglob('*'):
            if not os.path.isfile(file_path):
                continue

            file_obj = self.get_file(str(file_path))
            stats = file_obj.get_stats()
            file_date = stats.modified if modified else stats.created

            if start_date and file_date < start_date:
                continue
            if end_date and file_date > end_date:
                continue

            found_files.append(str(file_path))

        return found_files

    def get_directory_stats(self, directory: str) -> Dict[str, Any]:
        """Get comprehensive directory statistics"""
        dir_obj = self.get_directory(directory)
        stats = {
            'total_size': 0,
            'file_count': 0,
            'dir_count': 0,
            'file_types': {},
            'largest_files': [],
            'newest_files': []
        }

        all_files = []

        for entry in dir_obj.rglob('*'):
            if entry.is_file():
                file_obj = self.get_file(str(entry))
                file_stats = file_obj.get_stats()

                # Update counts and sizes
                stats['total_size'] += file_stats.size
                stats['file_count'] += 1

                # Track file types
                ext = file_obj.extension
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1

                # Track file details for sorting later
                all_files.append({
                    'path': str(entry),
                    'size': file_stats.size,
                    'modified': file_stats.modified
                })
            else:
                stats['dir_count'] += 1

        # Find largest files
        largest_files = sorted(all_files, key=lambda x: x['size'], reverse=True)[:10]
        stats['largest_files'] = [
            {'path': f['path'], 'size': f['size']} for f in largest_files
        ]

        # Find newest files
        newest_files = sorted(all_files, key=lambda x: x['modified'], reverse=True)[:10]
        stats['newest_files'] = [
            {'path': f['path'], 'modified': f['modified'].isoformat()}
            for f in newest_files
        ]

        return stats

    def _log_operation(self, operation_type: str, details: dict) -> None:
        """Log operation with timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'operation': operation_type,
            'details': details
        }
        self.operation_history.append(log_entry)
        self.logger.info(f"Operation: {operation_type} - Details: {json.dumps(details)}")

    def export_operation_history(self, output_file: str) -> bool:
        """Export operation history to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.operation_history, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting operation history: {str(e)}")
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.stop_watching()
        self._observer.stop()
        self._observer.join()
        self.thread_pool.shutdown()
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

    def __del__(self):
        """Cleanup on deletion"""
        with contextlib.suppress(Exception):
            self.stop_watching()
            self._observer.stop()
            self.thread_pool.shutdown(wait=False)


if __name__ == "__main__":
    pass
    # Basic usage
    # recyclebin = RecycleBin(".")
    # item_id = recyclebin.delete("__init__.py")
    # recyclebin.restore(item_id)

    # # Async usage
    # async with RecycleBin("/path/to/bin") as rb:
    #     item_id = await rb.async_delete("/path/to/file")
    #     await rb.async_restore(item_id)

    # Batch operations
    # with recyclebin.batch_operation():
    #     recyclebin.add_tag(item_id, "important")
    #     recyclebin.delete("/path/to/another/file")
    #
    # # List items with pattern
    # for item in recyclebin.list_items("*.txt"):
    #     print(item.original_path)
