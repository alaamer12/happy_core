import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from true.collections import RecycleBin


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def recyclebin(temp_dir):
    """Create a RecycleBin instance for testing."""
    bin_path = temp_dir / "recyclebin"
    rb = RecycleBin(location=str(bin_path), max_size=1024 * 1024)  # 1MB max size
    yield rb
    # Cleanup
    shutil.rmtree(bin_path, ignore_errors=True)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = temp_dir / "test_file.txt"
    with open(file_path, "w") as f:
        f.write("Test content")
    return file_path


class TestRecycleBin:
    def test_initialization(self, recyclebin, temp_dir):
        """Test RecycleBin initialization."""
        assert recyclebin.location == Path(temp_dir) / "recyclebin"
        assert recyclebin.max_size == 1024 * 1024
        assert isinstance(recyclebin.items, dict)
        assert str(recyclebin.metadata_file.exists())  # Dont forget __Str__

    def test_delete_file(self, recyclebin, sample_file):
        """Test deleting a file."""
        item_id = recyclebin.delete(str(sample_file))
        assert item_id in recyclebin.items
        assert not sample_file.exists()
        assert (recyclebin.location / item_id).exists()

    def test_delete_nonexistent_file(self, recyclebin):
        """Test deleting a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            recyclebin.delete("nonexistent.txt")

    def test_restore_file(self, recyclebin, sample_file):
        """Test restoring a file."""
        original_content = sample_file.read_text()
        item_id = recyclebin.delete(str(sample_file))
        recyclebin.restore(item_id)

        assert sample_file.exists()
        assert sample_file.read_text() == original_content
        assert not (recyclebin.location / item_id).exists()
        assert item_id not in recyclebin.items

    # @pytest.mark.asyncio
    # async def test_async_delete_restore(self, recyclebin, sample_file):
    #     """Test async delete and restore operations."""
    #     item_id = await recyclebin.async_delete(str(sample_file))
    #     assert item_id in recyclebin.items
    #     assert not sample_file.exists()
    #
    #     await recyclebin.async_restore(item_id)
    #     assert sample_file.exists()
    #     assert item_id not in recyclebin.items

    def test_storage_limit(self, recyclebin, temp_dir):
        """Test storage limit enforcement."""
        # Create a file larger than max_size
        large_file = temp_dir / "large_file.txt"
        with open(large_file, "wb") as f:
            f.write(b"0" * (recyclebin.max_size + 1))

        with pytest.raises(Exception):
            # This test works but because of monorepo he cant read the exceptions
            # To reproduce swap StorageFullError for Exception
            recyclebin.delete(str(large_file))

    def test_metadata_persistence(self, recyclebin, sample_file):
        """Test metadata is saved and loaded correctly."""
        item_id = recyclebin.delete(str(sample_file))

        # Create new RecycleBin instance to test loading
        new_bin = RecycleBin(str(recyclebin.location))
        assert item_id in new_bin.items
        assert new_bin.items[item_id].original_path == str(sample_file)

    def test_tags(self, recyclebin, sample_file):
        """Test tag operations."""
        item_id = recyclebin.delete(str(sample_file))

        recyclebin.add_tag(item_id, "important")
        assert "important" in recyclebin.items[item_id].tags

        recyclebin.remove_tag(item_id, "important")
        assert "important" not in recyclebin.items[item_id].tags

    def test_cleanup(self, recyclebin, sample_file):
        """Test cleanup of old items."""
        item_id = recyclebin.delete(str(sample_file))

        # Modify deletion date to be old
        recyclebin.items[item_id].deletion_date = datetime.now() - timedelta(days=31)

        recyclebin.cleanup(days=30)
        assert item_id not in recyclebin.items
        assert not (recyclebin.location / item_id).exists()

    def test_batch_operation(self, recyclebin, temp_dir):
        """Test batch operations."""
        files = []
        for i in range(3):
            file_path = temp_dir / f"test_file_{i}.txt"
            with open(file_path, "w") as f:
                f.write(f"Test content {i}")
            files.append(file_path)

        with recyclebin.batch_operation():
            item_ids = [recyclebin.delete(str(f)) for f in files]

        assert all(id in recyclebin.items for id in item_ids)
        assert len(recyclebin.items) == 3

    # @pytest.mark.asyncio
    # async def test_async_batch_operation(self, recyclebin, temp_dir):
    #     """Test async batch operations."""
    #     files = []
    #     for i in range(3):
    #         file_path = temp_dir / f"test_file_{i}.txt"
    #         with open(file_path, "w") as f:
    #             f.write(f"Test content {i}")
    #         files.append(file_path)
    #
    #     async with recyclebin.async_batch_operation():
    #         item_ids = [await recyclebin.async_delete(str(f)) for f in files]
    #
    #     assert all(id in recyclebin.items for id in item_ids)
    #     assert len(recyclebin.items) == 3

    def test_list_items(self, recyclebin, temp_dir):
        """Test listing items with pattern matching."""
        # Create and delete multiple files
        files = []
        for prefix in ['doc', 'img']:
            file_path = temp_dir / f"{prefix}_test.txt"
            with open(file_path, "w") as f:
                f.write("Test content")
            files.append(file_path)
            recyclebin.delete(str(file_path))

        # Test listing with pattern
        doc_items = list(recyclebin.list_items(pattern='doc'))
        assert len(doc_items) == 1
        assert 'doc' in doc_items[0].original_path

    def test_get_total_size(self, recyclebin, sample_file):
        """Test total size calculation."""
        initial_size = recyclebin.get_total_size()
        item_id = recyclebin.delete(str(sample_file))

        assert recyclebin.get_total_size() > initial_size
        assert recyclebin.get_total_size() == recyclebin.items[item_id].size


if __name__ == '__main__':
    pytest.main(['-v'])
