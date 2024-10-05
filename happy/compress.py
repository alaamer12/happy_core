import shutil
import os
from typing import NoReturn, Optional


def tar_compression(node: str, output_dir: Optional[str] = None) -> NoReturn:
    """
    Compress the directory or file 'node' into a tar archive.

    :param node: The file or directory to compress.
    :param output_dir: Directory where the archive will be saved (optional).
    :return: None
    """
    compress(node, "tar", output_dir)


def zip_compression(node: str, output_dir: Optional[str] = None) -> NoReturn:
    """
    Compress the directory or file 'node' into a zip archive.

    :param node: The file or directory to compress.
    :param output_dir: Directory where the archive will be saved (optional).
    :return: None
    """
    compress(node, "zip", output_dir)


def gzip_compression(node: str, output_dir: Optional[str] = None) -> NoReturn:
    """
    Compress the directory or file 'node' into a gzip archive.

    :param node: The file or directory to compress.
    :param output_dir: Directory where the archive will be saved (optional).
    :return: None
    """
    compress(node, "gztar", output_dir)


def rar_compression(node: str, output_dir: Optional[str] = None) -> NoReturn:
    """
    Compress the directory or file 'node' into a rar archive.

    :param node: The file or directory to compress.
    :param output_dir: Directory where the archive will be saved (optional).
    :return: None
    """
    compress(node, "rar", output_dir)


def compress(node: str, _format: str, output_dir: Optional[str] = None) -> NoReturn:
    """
    Helper function to compress 'node' into the specified format.

    :param node: The file or directory to compress.
    :param _format: The compression format (tar, zip, etc.).
    :param output_dir: Directory where the archive will be saved (optional).
    :return: None
    """
    try:
        output_path = output_dir if output_dir else os.path.dirname(node)
        archive_name = os.path.join(output_path, os.path.basename(node))
        shutil.make_archive(archive_name, _format, node)
        print(f"Compressed {node} to {archive_name}.{_format}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def decompression(node: str, extract_dir: Optional[str] = None) -> NoReturn:
    """
    Decompress the specified archive to the given directory.

    :param node: The archive file to decompress.
    :param extract_dir: Directory to extract the files to (optional).
    :return: None
    """
    try:
        if extract_dir is None:
            extract_dir = os.path.splitext(node)[0]  # Default to a directory with the same name as the archive
        shutil.unpack_archive(node, extract_dir)
        print(f"Decompressed {node} to {extract_dir}")
    except shutil.ReadError as e:
        print(f"Error: {e} - Unsupported archive format or corrupted file.")
