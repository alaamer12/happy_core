import os
import shutil

import pytest

from true.collections import (DummyFile, PDFFileCreator, TXTFileCreator,
                                    JPGFileCreator, PNGFileCreator, GIFFileCreator, ZIPFileCreator,
                                    EPUBFileCreator, DOCXFileCreator, XLSXFileCreator)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file creation x."""
    yield tmp_path
    # Cleanup after x
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


@pytest.fixture
def dummy_file():
    """Create a DummyFile instance for testing."""
    return DummyFile()


def test_file_creator_initialization():
    """Test basic initialization of FileCreator classes."""
    pdf_creator = PDFFileCreator()
    assert pdf_creator.extension == '.pdf'
    assert pdf_creator.default_size == 1024
    assert pdf_creator.default_content == b'0'
    assert len(pdf_creator.created_files) == 0


def test_create_pdf_file(temp_dir):
    """Test creation of PDF dummy file."""
    pdf_creator = PDFFileCreator()
    filename = temp_dir / "test.pdf"
    pdf_creator.create_file(str(filename))

    assert filename.exists()
    with open(filename, 'rb') as f:
        content = f.read()
        assert content.startswith(b'%PDF-1.4\n%')


def test_create_txt_file_with_content(temp_dir):
    """Test creation of TXT file with specific content."""
    txt_creator = TXTFileCreator()
    filename = temp_dir / "test.txt"
    test_content = "Hello, World!"
    txt_creator.create_file(str(filename), content=test_content)

    assert filename.exists()
    with open(filename, 'r') as f:
        content = f.read()
        assert test_content in content


@pytest.mark.parametrize("extension,header", [
    ('.pdf', b'%PDF-1.4\n%'),
    ('.epub', b'PK\x03\x04'),
    ('.docx', b'PK\x03\x04'),
    ('.jpg', b'\xFF\xD8\xFF'),
    ('.png', b'\x89PNG\r\n\x1a\n'),
])
def test_file_headers(temp_dir, extension, header):
    """Test that files are created with correct headers."""
    dummy = DummyFile()
    filename = temp_dir / f"test{extension}"
    dummy.create_file(extension, str(filename))

    assert filename.exists()
    with open(filename, 'rb') as f:
        content = f.read()
        assert content.startswith(header)


def test_custom_file_creation(temp_dir):
    """Test creation of custom file type."""
    dummy = DummyFile()
    filename = temp_dir / "test.custom"
    custom_header = b'CUSTOM'
    dummy.custom_file(
        str(filename),
        '.custom',
        header=custom_header,
        content=b'test content'
    )

    assert filename.exists()
    with open(filename, 'rb') as f:
        content = f.read()
        assert content.startswith(custom_header)


def test_file_size_specification(temp_dir):
    """Test that files are created with specified size."""
    dummy = DummyFile()
    filename = temp_dir / "test.txt"
    specified_size = 2048
    dummy.create_file('.txt', str(filename), size=specified_size)

    assert filename.exists()
    assert os.path.getsize(filename) == specified_size


def test_reset_functionality():
    """Test reset functionality of DummyFile."""
    dummy = DummyFile()
    dummy.created_files = ['test1.txt', 'test2.pdf']
    dummy.reset()
    assert len(dummy.created_files) == 0


def test_list_created_files(temp_dir):
    """Test listing of created files."""
    pdf_creator = PDFFileCreator()
    filename = temp_dir / "test.pdf"
    pdf_creator.create_file(str(filename))

    created_files = pdf_creator.list_created_files()
    assert len(created_files) == 1
    assert str(filename) in created_files


@pytest.mark.parametrize("creator_class,extension", [
    (PDFFileCreator, '.pdf'),
    (EPUBFileCreator, '.epub'),
    (DOCXFileCreator, '.docx'),
    (XLSXFileCreator, '.xlsx'),
    (TXTFileCreator, '.txt'),
    (JPGFileCreator, '.jpg'),
    (PNGFileCreator, '.png'),
    (GIFFileCreator, '.gif'),
    (ZIPFileCreator, '.zip'),
])
def test_file_creator_classes(temp_dir, creator_class, extension):
    """Test all file creator classes."""
    creator = creator_class()
    filename = temp_dir / f"test{extension}"
    creator.create_file(str(filename))

    assert filename.exists()
    assert creator.extension == extension


def test_audio_creation(temp_dir):
    """Test audio file creation."""
    dummy = DummyFile()
    filename = temp_dir / "test.mp3"
    dummy.create_audio(str(filename), duration=1000, frequency=440)

    assert filename.exists()
    assert os.path.getsize(filename) > 0


@pytest.mark.parametrize("size", [1024, 2048, 4096])
def test_different_file_sizes(temp_dir, size):
    """Test creation of files with different sizes."""
    dummy = DummyFile()
    filename = temp_dir / "test.txt"
    dummy.create_file('.txt', str(filename), size=size)

    assert filename.exists()
    assert os.path.getsize(filename) == size


def test_error_handling_invalid_extension():
    """Test handling of invalid file extensions."""
    dummy = DummyFile()
    assert '.invalid' not in dummy.creators
    # Should not raise an exception, just print a message
    dummy.create_file('.invalid')


def test_string_representation():
    """Test string and representation methods."""
    dummy = DummyFile()
    assert str(dummy) == "DummyFile Utility - 0 files created."
    assert repr(dummy) == "<DummyFile created: 0 files>"


def test_multiple_file_creation(temp_dir):
    """Test creation of multiple files."""
    dummy = DummyFile()
    extensions = ['.txt', '.pdf', '.jpg']
    filenames = []

    for ext in extensions:
        filename = temp_dir / f"test{ext}"
        filenames.append(filename)
        dummy.create_file(ext, str(filename))

    for filename in filenames:
        assert filename.exists()


def test_content_overflow_handling(temp_dir):
    """Test handling of content that's larger than specified size."""
    txt_creator = TXTFileCreator()
    filename = temp_dir / "test.txt"
    content = "A" * 2048  # Content larger than default size
    txt_creator.create_file(str(filename), size=1024, content=content)

    assert filename.exists()
    assert os.path.getsize(filename) == 1024  # Should truncate to specified size
