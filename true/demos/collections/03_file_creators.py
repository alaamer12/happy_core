"""
Demonstrates the usage of file creators and metadata operations in the True-Core collections module.

This example shows how to:
1. Create dummy files of various types
2. Work with file metadata
3. Use the DummyFile class for batch file creation
4. Create specialized file types (images, videos, audio)
"""

from true.collections import (
    DummyFile, PDFFileCreator,
    JPGFileCreator, Mp3FileCreator, File
)
import os
import tempfile

def demonstrate_file_creators():
    """Shows how to use various file creators."""
    # Create a PDF file
    pdf_creator = PDFFileCreator()
    pdf_file = pdf_creator.create_file("test.pdf", size=1024)
    print(f"Created PDF file: {pdf_file}")

    # Create a JPG file
    jpg_creator = JPGFileCreator()
    jpg_file = jpg_creator.create_file("test.jpg", size=2048)
    print(f"Created JPG file: {jpg_file}")

    # Create an MP3 file
    mp3_creator = Mp3FileCreator()
    mp3_file = mp3_creator.create_file("test.mp3", size=4096)
    print(f"Created MP3 file: {mp3_file}")

def demonstrate_dummy_file():
    """Shows how to use the DummyFile class for batch creation."""
    dummy = DummyFile(default_size=1024)
    
    # Create files of different types
    dummy.create_file(".pdf", "document.pdf")
    dummy.create_file(".txt", "notes.txt")
    dummy.create_file(".jpg", "image.jpg")
    
    # Create a custom file type
    dummy.custom_file(
        "custom.bin", 
        ".bin", 
        header=b'CUSTOM', 
        size=512
    )

    print("Created files:", dummy.created_files)

def demonstrate_multimedia_creation():
    """Shows how to create multimedia files."""
    dummy = DummyFile()
    
    # Create a test image
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "test_image.jpg")
        dummy.create_image(image_path)
        print(f"Created test image: {image_path}")
        
        # Create a video from the image
        video_path = os.path.join(temp_dir, "test_video.mp4")
        dummy.create_static_video(image_path, video_path)
        print(f"Created test video: {video_path}")
        
        # Create an audio file
        audio_path = os.path.join(temp_dir, "test_audio.wav")
        dummy.create_audio(audio_path)
        print(f"Created test audio: {audio_path}")

def demonstrate_metadata():
    """Shows how to work with file metadata."""
    # Create a test file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"Test content")
        temp_path = temp.name

    # Create a File object and get its metadata
    file = File(temp_path)
    
    # Get basic properties
    print(f"File name: {file.filename}")
    print(f"Extension: {file.extension}")
    print(f"Size: {file.size} bytes")
    print(f"MD5: {file.md5}")
    print(f"MIME type: {file.mime_type}")
    
    # Get comprehensive stats
    stats = file.get_stats()
    print("\nComprehensive stats:")
    print(f"Created: {stats.created}")
    print(f"Modified: {stats.modified}")
    print(f"Accessed: {stats.accessed}")
    print(f"Permissions: {stats.permissions}")
    print(f"Is hidden: {stats.is_hidden}")
    print(f"Owner: {stats.owner}")
    print(f"Group: {stats.group}")
    
    # Clean up
    os.unlink(temp_path)

if __name__ == "__main__":
    print("Demonstrating file creators...")
    demonstrate_file_creators()
    
    print("\nDemonstrating DummyFile class...")
    demonstrate_dummy_file()
    
    print("\nDemonstrating multimedia creation...")
    demonstrate_multimedia_creation()
    
    print("\nDemonstrating metadata operations...")
    demonstrate_metadata()
