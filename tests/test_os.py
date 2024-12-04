import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta

import pytest

# Import the classes to test
from true.collections import (
    FileStats, File, Directory, OSUtils,
    create_temp_file, create_temp_directory
)


@pytest.fixture
def temp_dir():
    """Fixture to create and cleanup a temporary directory"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_file(temp_dir):
    """Fixture to create a test file with content"""
    file_path = os.path.join(temp_dir, "test.txt")
    content = "Test content\nSecond line"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def os_utils(temp_dir):
    """Fixture to create OSUtils instance"""
    with OSUtils(base_path=temp_dir) as utils:
        yield utils


class TestFileStats:
    def test_file_stats_creation(self):
        stats = FileStats(
            size=100,
            created=datetime.now(),
            modified=datetime.now(),
            accessed=datetime.now(),
            permissions="rw-r--r--",
            is_hidden=False,
            mime_type="text/plain",
            owner="user",
            group="group",
            is_symlink=False,
            symlink_target=None
        )
        assert stats.size == 100
        assert stats.mime_type == "text/plain"

    def test_file_stats_conversion(self):
        original_stats = FileStats(
            size=100,
            created=datetime.now(),
            modified=datetime.now(),
            accessed=datetime.now(),
            permissions="rw-r--r--",
            is_hidden=False,
            mime_type="text/plain",
            owner="user",
            group="group",
            is_symlink=False,
            symlink_target=None
        )

        # Test to_dict and from_dict
        stats_dict = original_stats.to_dict()
        recreated_stats = FileStats.from_dict(stats_dict)
        assert recreated_stats.size == original_stats.size
        assert recreated_stats.mime_type == original_stats.mime_type


class TestFile:
    def test_file_creation(self, test_file):
        file = File(test_file)
        assert file.exists
        assert file.size > 0

    def test_file_properties(self, test_file):
        file = File(test_file)
        assert file.extension == ".txt"
        assert file.filename == "test"
        assert file.mime_type == "text/plain"

    def test_file_stats(self, test_file):
        file = File(test_file)
        stats = file.get_stats()
        assert isinstance(stats, FileStats)
        assert stats.size > 0
        assert not stats.is_hidden
        assert stats.mime_type == "text/plain"

    def test_file_operations(self, temp_dir):
        # Test file creation and writing
        file_path = os.path.join(temp_dir, "write_test.txt")
        file = File(file_path)
        content = "Test content"
        file.write_text(content)
        assert file.exists
        assert file.read_text() == content

        # Test file copying
        copy_path = os.path.join(temp_dir, "copy_test.txt")
        assert file.copy_to(copy_path)
        assert os.path.exists(copy_path)

        # Test backup creation
        backup = file.create_backup()
        assert backup.exists
        assert backup.read_text() == content


class TestDirectory:
    def test_directory_creation(self, temp_dir):
        dir_path = os.path.join(temp_dir, "test_dir")
        directory = Directory(dir_path)
        assert directory.create()
        assert os.path.exists(dir_path)

    def test_directory_size(self, temp_dir):
        directory = Directory(temp_dir)
        # Create some files
        for i in range(3):
            with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
                f.write("test" * 100)

        assert directory.size > 0

    def test_directory_tree(self, temp_dir):
        # Create a directory structure
        os.makedirs(os.path.join(temp_dir, "dir1/subdir"))
        with open(os.path.join(temp_dir, "dir1/file1.txt"), "w") as f:
            f.write("test")

        directory = Directory(temp_dir)
        tree = directory.get_tree()
        assert "dir1" in tree
        assert isinstance(tree["dir1"], dict)

    def test_zip_contents(self, temp_dir):
        directory = Directory(temp_dir)
        # Create some files
        for i in range(3):
            with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
                f.write("test")

        zip_path = os.path.join(temp_dir, "archive.zip")
        assert directory.zip_contents(zip_path)
        assert os.path.exists(zip_path)


class TestOSUtils:
    def test_file_operations(self, os_utils, temp_dir):
        # Test file creation and movement
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("test")

        dest_path = os.path.join(temp_dir, "dest.txt")
        assert os_utils.safe_move(source_path, dest_path)
        assert not os.path.exists(source_path)
        assert os.path.exists(dest_path)

    def test_batch_processing(self, os_utils, temp_dir):
        # Create test files
        file_paths = []
        for i in range(3):
            path = os.path.join(temp_dir, f"test{i}.txt")
            with open(path, "w") as f:
                f.write("test")
            file_paths.append(path)

        # Test batch processing
        def process_file(path):
            return os.path.exists(path)

        results = os_utils.batch_process(file_paths, process_file)
        assert all(results.values())

    def test_find_files_by_date(self, os_utils, temp_dir):
        # Create files with different dates
        now = datetime.now()

        # Create old file
        old_file = os.path.join(temp_dir, "old.txt")
        with open(old_file, "w") as f:
            f.write("old")
        os.utime(old_file, (time.time() - 86400, time.time() - 86400))

        # Create new file
        new_file = os.path.join(temp_dir, "new.txt")
        with open(new_file, "w") as f:
            f.write("new")

        files = os_utils.find_files_by_date(
            temp_dir,
            start_date=now - timedelta(hours=1)
        )
        assert len(files) == 1
        assert os.path.basename(files[0]) == "new.txt"

    def test_directory_stats(self, os_utils, temp_dir):
        # Create some test files
        for i in range(3):
            with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
                f.write("test" * 100)

        stats = os_utils.get_directory_stats(temp_dir)
        assert stats["file_count"] == 3
        assert stats["total_size"] > 0
        assert ".txt" in stats["file_types"]
        assert len(stats["largest_files"]) > 0
        assert len(stats["newest_files"]) > 0

    def test_operation_history(self, os_utils, temp_dir):
        # Perform some operations
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("test")

        dest_path = os.path.join(temp_dir, "dest.txt")
        os_utils.safe_move(source_path, dest_path)

        # Export and check history
        history_path = os.path.join(temp_dir, "history.json")
        assert os_utils.export_operation_history(history_path)

        with open(history_path) as f:
            history = json.load(f)
        assert len(history) > 0
        assert history[0]["operation"] == "move"


def test_temp_file_creation():
    temp_file = create_temp_file()
    try:
        assert isinstance(temp_file, File)
        assert temp_file.exists
    finally:
        if temp_file.exists:
            os.unlink(temp_file.full_path)


def test_temp_directory_creation():
    temp_dir = create_temp_directory()
    try:
        assert isinstance(temp_dir, Directory)
        assert temp_dir.exists
    finally:
        if temp_dir.exists:
            shutil.rmtree(temp_dir.full_path)


from pathlib import Path

if Path("osutils.log").exists():
    os.remove("osutils.log")
