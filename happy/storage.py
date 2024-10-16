import json
import os
import pickle
import threading
import time
import zlib
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Iterator, Tuple


class ColdStorage:
    def __init__(self, storage_directory='cold_storage', metadata_file='metadata.json'):
        self.storage_directory = storage_directory
        self.metadata_file = metadata_file
        self.metadata = {}
        self._load_metadata()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create the storage directory if it does not exist."""
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def _load_metadata(self):
        """Load metadata from a JSON file."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as file:
                self.metadata = json.load(file)

    def _save_metadata(self):
        """Save metadata to a JSON file."""
        with open(self.metadata_file, 'w') as file:
            json.dump(self.metadata, file)

    @staticmethod
    def _compress_data(data):
        """Compress data using zlib."""
        return zlib.compress(pickle.dumps(data))

    @staticmethod
    def _decompress_data(compressed_data):
        """Decompress data using zlib."""
        return pickle.loads(zlib.decompress(compressed_data))

    def store_item(self, key, value):
        """Store an item in cold storage with metadata."""
        filename = os.path.join(self.storage_directory, f"{key}.bin")
        compressed_data = self._compress_data(value)

        with open(filename, 'wb') as file:
            file.write(compressed_data)

        self.metadata[key] = {
            'filename': f"{key}.bin",
            'stored_at': datetime.now().isoformat()
        }
        self._save_metadata()

    def retrieve_item(self, key):
        """Retrieve an item from cold storage."""
        if key in self.metadata:
            filename = os.path.join(self.storage_directory, self.metadata[key]['filename'])
            with open(filename, 'rb') as file:
                compressed_data = file.read()
                return self._decompress_data(compressed_data)
        return None

    def delete_item(self, key):
        """Delete an item from cold storage."""
        if key in self.metadata:
            filename = os.path.join(self.storage_directory, self.metadata[key]['filename'])
            if os.path.exists(filename):
                os.remove(filename)
            del self.metadata[key]
            self._save_metadata()

    def clear_storage(self):
        """Clear all items from cold storage."""
        for filename in os.listdir(self.storage_directory):
            file_path = os.path.join(self.storage_directory, filename)
            os.remove(file_path)
        self.metadata.clear()
        self._save_metadata()


class HotStorage:
    def __init__(self, max_size=100, expiration_time=300):
        self.data = OrderedDict()  # Maintains insertion order
        self.max_size = max_size
        self.expiration_time = expiration_time  # Time in seconds
        self.lock = threading.Lock()  # For thread-safe access

    def _remove_expired_items(self):
        """Remove expired items from storage."""
        current_time = time.time()
        keys_to_delete = [key for key, (value, timestamp) in self.data.items() if
                          current_time - timestamp > self.expiration_time]
        for key in keys_to_delete:
            del self.data[key]

    def store_item(self, key, value):
        """Store an item in hot storage with a timestamp."""
        with self.lock:
            self._remove_expired_items()  # Clean up expired items
            if key in self.data:
                del self.data[key]  # Remove existing key to reinsert (to maintain order)
            self.data[key] = (value, time.time())  # Store value with timestamp
            if len(self.data) > self.max_size:
                self.data.popitem(last=False)  # Remove oldest item if max size exceeded

    def retrieve_item(self, key):
        """Retrieve an item from hot storage."""
        with self.lock:
            self._remove_expired_items()  # Clean up expired items
            item = self.data.get(key, None)
            return item[0] if item else None

    def delete_item(self, key):
        """Delete an item from hot storage."""
        with self.lock:
            if key in self.data:
                del self.data[key]

    def clear_storage(self):
        """Clear all items from hot storage."""
        with self.lock:
            self.data.clear()


class MixedStorage:
    def __init__(self, max_size=100, expiration_time=300):
        self.hot_storage = HotStorage(max_size, expiration_time)
        self.cold_storage = ColdStorage()
        self._lock = threading.Lock()

    def store_session(self, session_id, session_data):
        with self._lock:
            self.hot_storage.store_item(session_id, session_data)
            self.cold_storage.store_item(session_id, session_data)

    def retrieve_session(self, session_id):
        with self._lock:
            session_data = self.hot_storage.retrieve_item(session_id)
            if session_data is None:
                session_data = self.cold_storage.retrieve_item(session_id)
            return session_data

    def delete_session(self, session_id):
        with self._lock:
            self.hot_storage.delete_item(session_id)
            self.cold_storage.delete_item(session_id)

    def clear_storage(self):
        with self._lock:
            self.hot_storage.clear_storage()
            self.cold_storage.clear_storage()

    def __del__(self):
        self.clear_storage()

    def __repr__(self):
        return f"{self.__class__.__name__}(max_size={self.hot_storage.max_size}, expiration_time={self.hot_storage.expiration_time})"

    def __str__(self):
        return self.__repr__()


@dataclass(kw_only=True)
class SessionStoreConfig:
    max_size: int = 1000
    expiration_time: int = 3600  # seconds
    cleanup_interval: int = 60  # seconds


@dataclass
class SessionStore:
    """A robust and thread-safe in-memory session store with expiration and LRU eviction."""

    config: SessionStoreConfig = field(default_factory=SessionStoreConfig)
    _store: OrderedDict = field(init=False, default_factory=OrderedDict)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _stop_cleanup: threading.Event = field(init=False, default_factory=threading.Event)
    _cleanup_thread: threading.Thread = field(init=False)

    def __post_init__(self):
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self._cleanup_thread.start()

    def set(self, key: Any, value: Any) -> None:
        """Set a session key to a value with the current timestamp."""
        with self._lock:
            current_time = time.time()
            if key in self._store:
                del self._store[key]
            elif len(self._store) >= self.config.max_size:
                evicted_key, _ = self._store.popitem(last=False)  # Evict LRU item
                print(f"Evicted key due to max_size limit: {evicted_key}")
            self._store[key] = (value, current_time + self.config.expiration_time)
            print(f"Set key: {key} with expiration at {current_time + self.config.expiration_time}")

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Retrieve a session value by key. Returns default if key is not found or expired."""
        with self._lock:
            item = self._store.get(key)
            if item:
                value, expire_at = item
                if expire_at >= time.time():
                    # Move the key to the end to mark it as recently used
                    self._store.move_to_end(key)
                    print(f"Accessed key: {key}")
                    return value
                else:
                    # Item has expired
                    del self._store[key]
                    print(f"Expired key removed: {key}")
            return default

    def delete(self, key: Any) -> bool:
        """Delete a session key. Returns True if the key was deleted, False if not found."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                print(f"Deleted key: {key}")
                return True
            print(f"Attempted to delete non-existent key: {key}")
            return False

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            self._store.clear()
            print("Cleared all sessions.")

    def keys(self) -> Iterator[Any]:
        """Return an iterator over the session keys."""
        with self._lock:
            return iter(self._store.keys())

    def values(self) -> Iterator[Any]:
        """Return an iterator over the session values."""
        with self._lock:
            return (value for value, _ in self._store.values())

    def items(self) -> Iterator[Tuple[Any, Any]]:
        """Return an iterator over the session items (key, value)."""
        with self._lock:
            return ((key, value) for key, (value, expire_at) in self._store.items())

    def _cleanup_expired_sessions(self) -> None:
        """Background thread method to clean up expired sessions periodically."""
        while not self._stop_cleanup.is_set():
            with self._lock:
                current_time = time.time()
                keys_to_delete = [key for key, (_, expire_at) in self._store.items() if expire_at < current_time]
                for key in keys_to_delete:
                    del self._store[key]
                    print(f"Cleanup thread removed expired key: {key}")
            self._stop_cleanup.wait(self.config.cleanup_interval)

    def stop_cleanup(self) -> None:
        """Stop the background cleanup thread."""
        self._stop_cleanup.set()
        self._cleanup_thread.join()
        print("Cleanup thread stopped.")

    def __del__(self):
        """Ensure the cleanup thread is stopped when the instance is deleted."""
        self.stop_cleanup()

    def __setitem__(self, key: Any, value: Any) -> None:
        """Enable dict-like setting of items."""
        self.set(key, value)

    def __getitem__(self, key: Any) -> Any:
        """Enable dict-like getting of items."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __delitem__(self, key: Any) -> None:
        """Enable dict-like deletion of items."""
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        """Enable use of 'in' keyword to check for key existence."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return the number of active (non-expired) sessions."""
        with self._lock:
            return len(self._store)

    def __repr__(self) -> str:
        with self._lock:
            return (f"{self.__class__.__name__}(max_size={self.config.max_size}, "
                    f"expiration_time={self.config.expiration_time}, current_size={len(self._store)})")

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return False
        with self._lock, other._lock:
            return self._store == other._store and self.config == other.config

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, SessionStore):
            return NotImplemented
        with self._lock, other._lock:
            return len(self._store) <= len(other._store)
