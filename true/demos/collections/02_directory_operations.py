"""
Directory operations and traversal demonstrations.

This demo shows directory manipulation including:
- Directory creation and deletion
- Directory traversal
- File filtering and pattern matching
- Directory statistics and metadata
"""

from true.collections import Directory, File


def demo_directory_creation():
    """Demonstrate directory creation and basic properties."""
    print("\n=== Directory Creation and Properties ===")

    # Create a test directory
    dir_path = "test_directory"
    directory = Directory(dir_path)
    directory.create()

    # Create some test files
    for i in range(3):
        File(f"{dir_path}/file_{i}.txt").write_text(f"Content {i}")

    # Create a subdirectory
    subdir = Directory(f"{dir_path}/subdir")
    subdir.create()

    # Display properties
    print(f"Directory path: {directory.abspath}")
    print(f"Full path: {directory.full_path}")
    print(f"Directory name: {directory.name}")
    print(f"Parent directory: {directory.parent}")
    print(f"Is empty: {directory.is_empty}")
    print(f"Size: {directory.size} bytes")

    # Clean up
    directory.delete()


def demo_directory_traversal():
    """Demonstrate directory traversal and filtering."""
    print("\n=== Directory Traversal and Filtering ===")

    # Create a test directory structure
    root_dir = Directory("test_root")
    root_dir.create()

    # Create some files and subdirectories
    File("test_root/file1.txt").write_text("Text file")
    File("test_root/file2.py").write_text("Python file")
    Directory("test_root/subdir1").create()
    Directory("test_root/subdir2").create()
    File("test_root/subdir1/nested.txt").write_text("Nested file")

    # Filter files by pattern
    print("\nText files only:")
    for file in root_dir.rglob("*.txt"):
        print(f"- {file}")

    # Clean up
    root_dir.delete()


if __name__ == "__main__":
    print("Demonstrating Directory class functionality...")
    demo_directory_creation()
    demo_directory_traversal()
    print("\nDemo completed successfully!")
