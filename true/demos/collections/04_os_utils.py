"""
OS utilities demonstration.

This demo shows the advanced OS utilities including:
- File and directory operations
- Directory watching
- Batch processing
- Secure file operations
"""

from datetime import datetime, timedelta
from true.collections import OSUtils, File, Directory
import time
import os

def demo_basic_operations():
    """Demonstrate basic OSUtils operations."""
    print("\n=== Basic OS Operations ===")
    
    # Initialize OSUtils
    os_utils = OSUtils()
    
    # Create test files and directories
    test_dir = Directory("test_os_utils")
    test_dir.create()
    
    # Create some test files
    File("test_os_utils/file1.txt").write_text("Test file 1")
    File("test_os_utils/file2.txt").write_text("Test file 2")
    
    # Get file and directory objects
    file1 = os_utils.get_file("test_os_utils/file1.txt")
    dir1 = os_utils.get_directory("test_os_utils")
    
    print(f"File path: {file1.abspath}")
    print(f"Directory path: {dir1.abspath}")
    
    # Safe move operation
    os_utils.safe_move("test_os_utils/file1.txt", "test_os_utils/file1_moved.txt")
    print("File moved successfully")
    
    # Clean up
    test_dir.delete()

def demo_batch_processing():
    """Demonstrate batch file processing."""
    print("\n=== Batch Processing ===")
    
    os_utils = OSUtils()
    batch_dir = Directory("batch_dir")
    batch_dir.create()
    
    # Create test files
    files = []
    for i in range(3):
        file_path = f"batch_dir/batch_{i}.txt"
        File(file_path).write_text(f"Batch file {i}")
        files.append(file_path)
    
    # Define processing function
    def process_file(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        print(f"Processed {file_path}: {content}")
    
    # Process files in parallel
    print("\nProcessing files in parallel...")
    os_utils.batch_process(files, process_file, parallel=True)
    
    # Clean up
    batch_dir.delete()

def demo_secure_operations():
    """Demonstrate secure file operations."""
    print("\n=== Secure Operations ===")
    
    os_utils = OSUtils()
    secure_dir = Directory("secure_dir")
    secure_dir.create()
    
    # Create a file with sensitive content
    sensitive_file = File("secure_dir/sensitive.txt")
    sensitive_file.write_text("Sensitive data")
    
    # Securely delete the file
    print("Securely deleting file...")
    os_utils.safe_delete(sensitive_file.abspath, secure=True)
    print("File securely deleted")
    
    # Clean up
    secure_dir.delete()

def demo_file_search():
    """Demonstrate file searching by date."""
    print("\n=== File Search Operations ===")
    
    os_utils = OSUtils()
    search_dir = Directory("search_dir")
    search_dir.create()
    
    # Create files with different dates
    for i in range(3):
        file_path = f"search_dir/file_{i}.txt"
        File(file_path).write_text(f"File {i}")
    
    # Search for files within date range
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=5)
    
    print("\nSearching for recently created files...")
    recent_files = os_utils.find_files_by_date(
        "search_dir",
        start_date=start_date,
        end_date=end_date
    )
    
    for file in recent_files:
        print(f"Found file: {file}")
    
    # Clean up
    search_dir.delete()

if __name__ == "__main__":
    print("Demonstrating OSUtils functionality...")
    demo_basic_operations()
    demo_batch_processing()
    demo_secure_operations()
    demo_file_search()
    print("\nDemo completed successfully!")
