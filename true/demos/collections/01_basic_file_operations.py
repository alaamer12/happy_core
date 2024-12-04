"""
Basic file operations using the File class.

This demo shows fundamental file operations including:
- Creating and reading files
- Getting file metadata
- File copying and backup
- Text file operations
"""

import os

from true.collections import File, create_temp_file


def demo_file_creation():
    """Demonstrate basic file creation and properties."""
    print("\n=== File Creation and Properties ===")

    # Create a temporary text file
    temp_file = create_temp_file(suffix=".txt").abspath
    file = File(temp_file)

    # Write some content
    file.write_text("Hello, World!\nThis is a test file.")

    # Display basic properties
    print(f"File path: {file.abspath}")
    print(f"Full path: {file.full_path}")
    print(f"Filename: {file.filename}")
    print(f"Extension: {file.extension}")
    print(f"Size: {file.size} bytes")
    print(f"MD5: {file.md5}")
    print(f"MIME type: {file.mime_type}")


def demo_file_operations():
    """Demonstrate file operations."""
    print("\n=== File Operations ===")

    # Create a file with some content
    file = File("test_file.txt")
    file.write_text("Line 1\nLine 2\nLine 3")

    # Read content
    print("File content:")
    print(file.read_text())

    # Create backup
    backup = file.create_backup()
    print(f"\nBackup created: {backup}")

    # Copy file
    file.copy_to("test_file_copy.txt")
    print(f"File copied to: test_file_copy.txt")

    # Clean up
    try:
        os.remove(file.full_path)
        os.remove(backup.abspath)
        os.remove("test_file_copy.txt")
    except Exception as e:
        print(f"Error cleaning up: {str(e)}")


def demo_file_stats():
    """Demonstrate file statistics."""
    print("\n=== File Statistics ===")

    # Create a file
    file = File("stats_test.txt")
    file.write_text("Test content for stats")

    # Get comprehensive stats
    stats = file.get_stats()
    print("File statistics:")
    print(f"Size: {stats.size} bytes")
    print(f"Created: {stats.created}")
    print(f"Modified: {stats.modified}")
    print(f"Accessed: {stats.accessed}")
    print(f"Permissions: {stats.permissions}")
    print(f"Owner: {stats.owner}")
    print(f"Group: {stats.group}")
    print(f"Is hidden: {stats.is_hidden}")

    # Clean up
    os.remove(file.full_path)


if __name__ == "__main__":
    print("Demonstrating File class functionality...")
    demo_file_creation()
    demo_file_operations()
    demo_file_stats()
    print("\nDemo completed successfully!")
