import os
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Optional, Union

from happy.types import AvifencConfig

PathLike = Union[Path, str, os.PathLike, None]


def tar_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    """
    Compresses the given directory or file into a tar archive.

    Args:
        node (PathLike): Path to the file or directory to compress.
        output_dir (PathLike, optional): Directory to store the compressed archive. Defaults to the parent directory of 'node'.
    """


def zip_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    """
    Compresses the given directory or file into a zip archive.

    Args:
        node (PathLike): Path to the file or directory to compress.
        output_dir (PathLike, optional): Directory to store the compressed archive. Defaults to the parent directory of 'node'.
    """


def gzip_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    """
    Compresses the given directory or file into a gzip archive.

    Args:
        node (PathLike): Path to the file or directory to compress.
        output_dir (PathLike, optional): Directory to store the compressed archive. Defaults to the parent directory of 'node'.
    """


def compress(node: PathLike, _format: str, output_dir: Optional[PathLike] = None) -> NoReturn:
    """
    Compresses the given directory or file into the specified format.

    Args:
        node (PathLike): Path to the file or directory to compress.
        _format (str): Compression format ('tar', 'zip', 'gztar', etc.).
        output_dir (PathLike, optional): Directory to store the compressed archive. Defaults to the parent directory of 'node'.

    Raises:
        FileNotFoundError: If the specified path does not exist.
    """


def decompression(node: PathLike, extract_dir: Optional[PathLike] = None) -> NoReturn:
    """
    Decompresses the specified archive to the given directory.

    Args:
        node (PathLike): Path to the archive file to decompress.
        extract_dir (PathLike, optional): Directory to extract the contents to. Defaults to the name of the archive without the extension.

    Raises:
        shutil.ReadError: If the archive format is unsupported or the file is corrupted.
    """


class OptimizeImage:
    """Class for optimizing and converting images."""

    def __init__(self, path: PathLike):
        """
        Initializes the OptimizeImage instance.

        Args:
            path (PathLike): Path to the image to optimize.

        Raises:
            ValueError: If the image path is invalid.
        """
        self.__img: PathLike = path
        self.__optimized_img: PathLike = None

    def __validate_path(self, img: PathLike) -> None:
        """
        Validates the given image path and ensures the correct extension.

        Args:
            img (PathLike): Path to the image.

        Raises:
            ValueError: If the image is invalid or has an incorrect extension.
        """

    def __pre_optimize(self) -> None:
        """
        Pre-optimizes the image using the MozJPEG lossless optimization.
        """

    def __save_at_temp_dir(self, output_bytes: bytes) -> None:
        """
        Saves the optimized image to a temporary directory.

        Args:
            output_bytes (bytes): Optimized image data.
        """

    @staticmethod
    def __check_extension(file: PathLike) -> PathLike:
        """
        Checks and adjusts the file extension to be '.avif'.

        Args:
            file (PathLike): File path to check.

        Returns:
            PathLike: File path with the corrected '.avif' extension.
        """

    def pillow_process(self, output_path: PathLike = ".") -> None:
        """
        Converts the optimized image to AVIF using Pillow.

        Args:
            output_path (PathLike, optional): Path to save the converted image. Defaults to current directory.
        """

    def avifenc_process(self, *, config: AvifencConfig, output_path: PathLike = ".") -> None:
        """
        Converts the optimized image to AVIF using the `avifenc` tool.

        Args:
            config (AvifencConfig): Configuration for the AVIF encoding process.
            output_path (PathLike, optional): Path to save the converted image. Defaults to current directory.
        """


@dataclass
class VideoConfig:
    codec: str
    crf: int
    preset: str


class OptimizeVideo:
    """Class for optimizing video files."""

    def __init__(self, path: PathLike):
        """
        Initializes the OptimizeVideos instance.

        Args:
            path (PathLike): Path to the video to optimize.

        Raises:
            FileNotFoundError: If the video file does not exist.
        """
        self.__webm = None
        self.__video = None

    def __validate_path(self) -> None:
        """
        Validates the given video path.

        Raises:
            FileNotFoundError: If the video file does not exist.
        """

    def is_video(self) -> bool:
        """
        Checks if the file is a valid video format based on its extension.

        Returns:
            bool: True if the file is a recognized video format, otherwise False.
        """

    def ffmpeg_process(self, output_path: PathLike, codec: str = 'libx265', crf: int = 28,
                       preset: str = 'slow') -> None:
        """
        Compresses and optimizes the video using FFmpeg.

        Args:
            output_path (PathLike): Path to save the optimized video.
            codec (str, optional): Video codec to use. Defaults to 'libx265'.
            crf (int, optional): Constant Rate Factor (quality setting). Defaults to 28.
            preset (str, optional): Compression preset. Defaults to 'slow'.

        Raises:
            RuntimeError: If the FFmpeg processing fails.
        """

    def __create_command(self, config: VideoConfig, output_path: PathLike):
        pass


class OptimizeAudios:
    def __init__(self, path: PathLike):
        self.__audio: PathLike = None

    def process(self, output_path: PathLike) -> None:
        """
        Processes the audio file using FFmpeg.
        :param output_path:
        :return:
        """
