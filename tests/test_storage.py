import json
import threading
from collections import OrderedDict
import pytest
from freezegun import freeze_time
from happy.storage import ColdStorage, HotStorage, SessionStore, SessionStoreConfig
import time


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to create a temporary directory."""
    return tmp_path


class TestColdStorage:
    def test_store_item(self, temp_dir):
        """Test storing an item in ColdStorage."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        key = "test_key"
        value = {"data": 123}

        cs.store_item(key, value)

        # Check if a file is created
        file_path = storage_dir / f"{key}.bin"
        assert file_path.exists()

        # Check if metadata is updated
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        assert key in metadata
        assert metadata[key]["filename"] == f"{key}.bin"
        assert "stored_at" in metadata[key]

        # Verify the content of the stored file
        with open(file_path, "rb") as f:
            compressed_data = f.read()
        decompressed_data = cs._decompress_data(compressed_data)
        assert decompressed_data == value

    def test_retrieve_existing_item(self, temp_dir):
        """Test retrieving an existing item from ColdStorage."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        key = "test_key"
        value = {"data": 456}
        cs.store_item(key, value)

        retrieved = cs.retrieve_item(key)
        assert retrieved == value

    def test_retrieve_non_existing_item(self, temp_dir):
        """Test retrieving a non-existing item returns None."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        retrieved = cs.retrieve_item("non_existing_key")
        assert retrieved is None

    def test_delete_existing_item(self, temp_dir):
        """Test deleting an existing item from ColdStorage."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        key = "test_key"
        value = {"data": 789}
        cs.store_item(key, value)

        # Ensure item exists
        assert cs.retrieve_item(key) == value

        # Delete the item
        cs.delete_item(key)

        # Ensure item is deleted
        assert cs.retrieve_item(key) is None
        file_path = storage_dir / f"{key}.bin"
        assert not file_path.exists()

        # Ensure metadata is updated
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        assert key not in metadata

    def test_delete_non_existing_item(self, temp_dir):
        """Test deleting a non-existing item does not raise an error."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        # Attempt to delete a key that doesn't exist
        try:
            cs.delete_item("non_existing_key")
        except Exception as e:
            pytest.fail(f"Deleting a non-existing key raised an exception: {e}")

    def test_clear_storage(self, temp_dir):
        """Test clearing all items from ColdStorage."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"
        cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))

        # Store multiple items
        for i in range(5):
            cs.store_item(f"key{i}", {"data": i})

        # Ensure items are stored
        for i in range(5):
            assert cs.retrieve_item(f"key{i}") == {"data": i}

        # Clear storage
        cs.clear_storage()

        # Ensure all items are deleted
        for i in range(5):
            assert cs.retrieve_item(f"key{i}") is None

        # Ensure the storage directory is empty
        assert not any(storage_dir.iterdir())

        # Ensure metadata is cleared
        assert cs.metadata == {}
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        assert metadata == {}

    # def test_load_metadata_when_file_not_exists(self, temp_dir, mocker):
    #     """Test that ColdStorage initializes with empty metadata if a metadata file does not exist."""
    #     storage_dir = temp_dir / "cold_storage_test"
    #     metadata_file = temp_dir / "metadata_test.json"
    #
    #     # Mock os.path.exists to return False for metadata_file
    #     mocker.patch("os.path.exists", side_effect=lambda path: path == storage_dir)
    #
    #     cs = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))
    #
    #     assert cs.metadata == {}

    def test_metadata_persistence(self, temp_dir):
        """Test that metadata persists across ColdStorage instances."""
        storage_dir = temp_dir / "cold_storage"
        metadata_file = temp_dir / "metadata.json"

        # First instance: store an item
        cs1 = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))
        cs1.store_item("persistent_key", {"data": "persistent_value"})

        # Second instance: load metadata
        cs2 = ColdStorage(storage_directory=str(storage_dir), metadata_file=str(metadata_file))
        retrieved = cs2.retrieve_item("persistent_key")
        assert retrieved == {"data": "persistent_value"}


class TestHotStorage:
    def test_initialization_defaults(self):
        """Test that HotStorage initializes with default parameters."""
        hs = HotStorage()
        assert hs.max_size == 100
        assert hs.expiration_time == 300
        assert isinstance(hs.data, OrderedDict)
        assert hs.data == OrderedDict()

    def test_store_and_retrieve_item(self):
        """Test storing and retrieving items in HotStorage."""
        hs = HotStorage(max_size=10, expiration_time=300)
        hs.store_item("key1", "value1")
        hs.store_item("key2", "value2")

        assert hs.retrieve_item("key1") == "value1"
        assert hs.retrieve_item("key2") == "value2"

    def test_retrieve_non_existing_item(self):
        """Test retrieving a non-existing item returns None."""
        hs = HotStorage()
        assert hs.retrieve_item("non_existing_key") is None

    @freeze_time("2024-01-01 12:00:00")
    def test_item_expiration(self):
        """Test that items expire after expiration_time."""
        hs = HotStorage(expiration_time=60)  # 1 minute expiration
        hs.store_item("key1", "value1")

        # Advance time by 30 seconds: item should still exist
        with freeze_time("2024-01-01 12:00:30"):
            assert hs.retrieve_item("key1") == "value1"

        # Advance time by another 40 seconds (total 70 seconds): item should expire
        with freeze_time("2024-01-01 12:01:10"):
            assert hs.retrieve_item("key1") is None

    def test_max_size_eviction(self):
        """Test that HotStorage evicts the oldest item when max_size is exceeded."""
        hs = HotStorage(max_size=3, expiration_time=300)
        hs.store_item("key1", "value1")
        hs.store_item("key2", "value2")
        hs.store_item("key3", "value3")

        # At this point, storage is full
        assert hs.retrieve_item("key1") == "value1"
        assert hs.retrieve_item("key2") == "value2"
        assert hs.retrieve_item("key3") == "value3"

        # Add another item, should evict key1
        hs.store_item("key4", "value4")
        assert hs.retrieve_item("key1") is None
        assert hs.retrieve_item("key2") == "value2"
        assert hs.retrieve_item("key3") == "value3"
        assert hs.retrieve_item("key4") == "value4"

    def test_store_existing_key_updates_value_and_order(self):
        """Test that storing an existing key updates its value and moves it to the end."""
        hs = HotStorage(max_size=3, expiration_time=300)
        hs.store_item("key1", "value1")
        hs.store_item("key2", "value2")
        hs.store_item("key3", "value3")

        # Update key2
        hs.store_item("key2", "new_value2")

        # Add another item, should evict key1
        hs.store_item("key4", "value4")

        assert hs.retrieve_item("key1") is None
        assert hs.retrieve_item("key2") == "new_value2"
        assert hs.retrieve_item("key3") == "value3"
        assert hs.retrieve_item("key4") == "value4"

    def test_delete_existing_item(self):
        """Test deleting an existing item from HotStorage."""
        hs = HotStorage()
        hs.store_item("key1", "value1")
        hs.store_item("key2", "value2")

        hs.delete_item("key1")
        assert hs.retrieve_item("key1") is None
        assert hs.retrieve_item("key2") == "value2"

    def test_delete_non_existing_item(self):
        """Test deleting a non-existing item does not raise an error."""
        hs = HotStorage()
        try:
            hs.delete_item("non_existing_key")
        except Exception as e:
            pytest.fail(f"Deleting a non-existing key raised an exception: {e}")

    def test_clear_storage(self):
        """Test clearing all items from HotStorage."""
        hs = HotStorage()
        hs.store_item("key1", "value1")
        hs.store_item("key2", "value2")

        hs.clear_storage()

        assert hs.retrieve_item("key1") is None
        assert hs.retrieve_item("key2") is None
        assert len(hs.data) == 0

    def test_thread_safety(self):
        """Test that HotStorage is thread-safe."""
        hs = HotStorage(max_size=1000, expiration_time=300)

        def store_items(start, end):
            for item in range(start, end):
                hs.store_item(f"key{item}", f"value{item}")

        threads = []
        for i in range(10):
            t = threading.Thread(target=store_items, args=(i * 100, (i + 1) * 100))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify that all items are stored
        for i in range(1000):
            assert hs.retrieve_item(f"key{i}") == f"value{i}"

    @freeze_time("2024-01-01 12:00:00")
    def test_expiration_with_multiple_items(self):
        """Test that multiple items expire correctly based on their individual timestamps."""
        hs = HotStorage(expiration_time=60)  # 1 minute expiration
        hs.store_item("key1", "value1")

        with freeze_time("2024-01-01 12:00:30"):
            hs.store_item("key2", "value2")
            assert hs.retrieve_item("key1") == "value1"
            assert hs.retrieve_item("key2") == "value2"

        with freeze_time("2024-01-01 12:01:01"):
            # key1 was stored at 12:00:00, should now be expired (61 > 60)
            # key2 was stored at 12:00:30, still valid (31 < 60)
            assert hs.retrieve_item("key1") is None
            assert hs.retrieve_item("key2") == "value2"

        with freeze_time("2024-01-01 12:01:31"):
            # key2 was stored at 12:00:30, now expired (61 > 60)
            assert hs.retrieve_item("key2") is None


@pytest.fixture
def session_store():
    """Fixture for creating a new SessionStore instance."""
    return SessionStore(config=SessionStoreConfig(max_size=5, expiration_time=2))

def test_set_and_get(session_store):
    """Test setting and getting session values."""
    session_store.set('key1', 'value1')
    assert session_store.get('key1') == 'value1'

def test_get_non_existent_key(session_store):
    """Test getting a non-existent key returns None."""
    assert session_store.get('non_existent_key') is None

def test_set_over_max_size(session_store):
    """Test the LRU eviction policy when exceeding max_size."""
    for i in range(6):
        session_store.set(f'key{i}', f'value{i}')
    assert 'key0' not in session_store  # key0 should be evicted

def test_key_expiration(session_store):
    """Test key expiration functionality."""
    session_store.set('temp_key', 'temp_value')
    time.sleep(3)  # Wait for the key to expire
    assert session_store.get('temp_key') is None  # The key should be expired

def test_delete_existing_key(session_store):
    """Test deleting an existing key."""
    session_store.set('key_to_delete', 'value')
    assert session_store.delete('key_to_delete') is True
    assert session_store.get('key_to_delete') is None

def test_delete_non_existent_key(session_store):
    """Test deleting a non-existent key."""
    assert session_store.delete('non_existent_key') is False

def test_clear(session_store):
    """Test clearing all sessions."""
    session_store.set('key1', 'value1')
    session_store.set('key2', 'value2')
    session_store.clear()
    assert len(session_store) == 0

def test_keys_method(session_store):
    """Test the keys' method."""
    session_store.set('key1', 'value1')
    session_store.set('key2', 'value2')
    keys = list(session_store.keys())
    assert set(keys) == {'key1', 'key2'}

def test_values_method(session_store):
    """Test the values' method."""
    session_store.set('key1', 'value1')
    session_store.set('key2', 'value2')
    values = list(session_store.values())
    assert set(values) == {'value1', 'value2'}

def test_items_method(session_store):
    """Test the items' method."""
    session_store.set('key1', 'value1')
    session_store.set('key2', 'value2')
    items = list(session_store.items())
    assert set(items) == {('key1', 'value1'), ('key2', 'value2')}

def test_len_method(session_store):
    """Test the len method."""
    assert len(session_store) == 0
    session_store.set('key1', 'value1')
    assert len(session_store) == 1
    session_store.set('key2', 'value2')
    assert len(session_store) == 2
    session_store.clear()
    assert len(session_store) == 0

def test_stop_cleanup(session_store):
    """Test stopping the cleanup thread."""
    session_store.stop_cleanup()
    assert session_store._stop_cleanup.is_set()  # Ensure the cleanup thread is stopped
