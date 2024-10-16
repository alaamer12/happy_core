import bz2
import gzip
# noinspection PyCompatibility
import imghdr
import io
import logging
import lzma
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Optional, Union

import mozjpeg_lossless_optimization
import pikepdf
import pydub
from PIL import Image
from ebooklib import epub

from happy.types import AvifencConfig

PathLike = Union[Path, str, os.PathLike, None]


class FileCompressionStrategy(ABC):
    @abstractmethod
    def compress(self, input_path, output_path, compression_level):
        raise NotImplementedError

    @abstractmethod
    def decompress(self, input_path, output_path):
        raise NotImplementedError


def tar_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    compress(node, "tar", output_dir)


def zip_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    compress(node, "zip", output_dir)


def gzip_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    compress(node, "gztar", output_dir)


def bz2_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    compress(node, "bztar", output_dir)


def xz_compression(node: PathLike, output_dir: Optional[PathLike] = None) -> NoReturn:
    compress(node, "xztar", output_dir)


def compress(node: PathLike, _format: str, output_dir: Optional[PathLike] = None) -> NoReturn:
    try:
        output_path = output_dir if output_dir else os.path.dirname(node)
        archive_name = os.path.join(output_path, os.path.basename(node))
        shutil.make_archive(archive_name, _format, root_dir=node)
        print(f"Compressed {node} to {archive_name}.{_format}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


def decompression(node: PathLike, extract_dir: Optional[PathLike] = None) -> NoReturn:
    try:
        if extract_dir is None:
            extract_dir = os.path.splitext(node)[0]
        shutil.unpack_archive(node, extract_dir)
        print(f"Decompressed {node} to {extract_dir}")
    except shutil.ReadError as e:
        print(f"Error: {e} - Unsupported archive format or corrupted file.")


class OptimizeImage:
    def __init__(self, path: PathLike):
        self.__img: PathLike = path
        self.__optimized_img: PathLike = None
        self.__validate_path(self.__img)
        self.__pre_optimize()

    def __validate_path(self, img: PathLike) -> None:
        extension = imghdr.what(img)
        if extension is None:
            raise ValueError(f"Invalid image file: {img}")
        if not img.endswith(extension.lower()):
            self.__img += f".{extension.lower()}"

    def __pre_optimize(self) -> None:
        with open(self.__img, "rb") as input_jpeg_file:
            input_jpeg_bytes = input_jpeg_file.read()

        output_jpeg_bytes = mozjpeg_lossless_optimization.optimize(input_jpeg_bytes)
        self.__save_at_temp_dir(output_jpeg_bytes)

    def __save_at_temp_dir(self, output_bytes: bytes) -> None:
        tempdir = tempfile.mkdtemp(suffix="optimized")
        opt_img_path = os.path.join(tempdir, self.__img)
        with open(opt_img_path, "wb") as f:
            f.write(output_bytes)

        self.__optimized_img = opt_img_path

    @staticmethod
    def __check_extension(file):
        if file.endswith(".jpg"):
            file = file.replace(".jpg", ".avif")
        elif not file.endswith("avif"):
            file += ".avif"

        return file

    def pillow_process(self, output_path: PathLike = ".") -> None:
        jpgimg = Image.open(self.__optimized_img)
        _output_path = self.__check_extension(output_path)
        jpgimg.save(_output_path, 'AVIF')

    def avifenc_process(self, *, config: AvifencConfig, output_path: PathLike = ".") -> None:
        _output_path = self.__check_extension(output_path)
        subprocess.run(f"avifenc --min {config.min} --max {config.max} "
                       f"-a end-usage=q -a cq-level=18 -a tune=ssim {self.__optimized_img} {_output_path}",
                       shell=True)


@dataclass
class VideoConfig:
    codec: str
    crf: int
    preset: str

    def __post_init__(self):
        self.codec = self.codec.lower()
        self.crf = int(self.crf)
        self.preset = self.preset.lower()


class OptimizeVideo:

    def __init__(self, path: PathLike, webm: bool = True):
        self.__video: PathLike = path
        self.__webm = webm
        self.__validate_path()

    def __validate_path(self) -> None:
        # Validate if the path exists and is a file
        if not os.path.isfile(self.__video):
            raise FileNotFoundError(f"Video file '{self.__video}' does not exist.")

    def is_video(self) -> bool:
        # Check if the file is a valid video format (basic check for extension)
        valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.mpg', '.mpeg', '.m4v']
        return any(self.__video.endswith(ext) for ext in valid_extensions)

    def __create_command(self, config: VideoConfig, output_path: PathLike) -> list:
        command = [
            'ffmpeg', '-i', str(self.__video),
            '-c:v', config.codec, '-crf', str(config.crf),
            '-preset', config.preset, '-c:a', 'copy',
            str(output_path)
        ]

        # If the video should be processed as webm
        if self.__webm:
            command = [
                'ffmpeg', '-i', str(self.__video),
                '-c:v', 'libvpx', '-c:a', 'libvorbis',
                str(output_path)
            ]

        return command

    def ffmpeg_process(self, output_path: PathLike, codec: str = 'libx265', crf: int = 28,
                       preset: str = 'slow') -> None:
        # Ensure output path exists
        output_dir = os.path.dirname(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # noinspection PyArgumentList
        config = VideoConfig(codec, crf, preset)
        command = self.__create_command(config, output_path)

        # Run the ffmpeg command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg processing failed: {e}")


class OptimizeAudios:
    def __init__(self, path: PathLike):
        self.__audio: PathLike = path

    def process(self, output_path: PathLike):
        # Load the audio file
        audio = pydub.AudioSegment.from_file(self.__audio)

        # Export as Opus
        basename = os.path.basename(output_path)
        audio.export(output_path, format=basename.split('.')[-1])


# Concrete strategy for GZIP compression (e.g., .txt files)
class GzipCompressionStrategy(FileCompressionStrategy):
    def compress(self, input_path: str, output_path: str, compression_level: int = 9):
        logging.info("Compressing using GZIP.")
        # Ensure file-like objects are typed correctly
        with open(input_path, 'rb') as f_in:  # f_in is SupportsRead
            with gzip.open(output_path, 'wb', compresslevel=compression_level) as f_out:  # f_out is SupportsWrite
                # noinspection PyTypeChecker
                shutil.copyfileobj(f_in, f_out)

    def decompress(self, input_path, output_path):
        logging.info("Decompressing GZIP file.")
        with gzip.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# Concrete strategy for LZMA compression (e.g., generic files)
class LzmaCompressionStrategy(FileCompressionStrategy):
    def compress(self, input_path, output_path, compression_level=9):
        logging.info("Compressing using LZMA.")
        with open(input_path, 'rb') as f_in, lzma.open(output_path, 'wb', preset=compression_level) as f_out:
            # noinspection PyTypeChecker
            shutil.copyfileobj(f_in, f_out)

    def decompress(self, input_path, output_path):
        logging.info("Decompressing LZMA file.")
        with lzma.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# Concrete strategy for BZ2 compression
class Bz2CompressionStrategy(FileCompressionStrategy):
    def compress(self, input_path, output_path, compression_level=9):
        logging.info("Compressing using BZ2.")
        with open(input_path, 'rb') as f_in, bz2.open(output_path, 'wb', compresslevel=compression_level) as f_out:
            # noinspection PyTypeChecker
            shutil.copyfileobj(f_in, f_out)

    def decompress(self, input_path, output_path):
        logging.info("Decompressing BZ2 file.")
        with bz2.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# Concrete strategy for PDF optimization using pikepdf
class PdfPikepdfCompressionStrategy(FileCompressionStrategy):
    def compress(self, input_path, output_path, compression_level=9):
        logging.info("Compressing PDF using pikepdf.")
        pdf = pikepdf.open(input_path)
        pdf.save(output_path)
        pdf.close()

    def decompress(self, input_path, output_path):
        logging.warning("Decompression for optimized PDFs is not supported.")


# Concrete strategy for EPUB optimization
class EpubCompressionStrategy(FileCompressionStrategy):
    def compress(self, input_path, output_path, compression_level=9):
        logging.info("Compressing EPUB by optimizing images.")
        book = epub.read_epub(input_path)
        for item in book.get_items():
            if item.get_type() == epub.ITEM_IMAGE:
                try:
                    image = Image.open(io.BytesIO(item.content))
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format, optimize=True, quality=50)
                    item.content = img_byte_arr.getvalue()
                    logging.info(f"Compressed image: {item.get_name()}")
                except Exception as e:
                    logging.warning(f"Failed to compress image {item.get_name()}: {e}")
        epub.write_epub(output_path, book, {})

    def decompress(self, input_path, output_path):
        logging.warning("Decompression for optimized EPUBs is not supported.")


# Context for using different file optimization strategies
def _generate_compressed_path(path):
    base, ext = os.path.splitext(path)
    return f"{base}_optimized{ext}"


class FileOptimizer:
    def __init__(self, input_path, output_path=None, compression_level=9, strategy=None):
        self.input_path = input_path
        self.output_path = output_path or _generate_compressed_path(input_path)
        self.compression_level = compression_level
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def optimize(self):
        if not os.path.isfile(self.input_path):
            logging.error(f"File not found: {self.input_path}")
            return False

        try:
            self.strategy.compress(self.input_path, self.output_path, self.compression_level)
            logging.info(f"Optimized file saved to: {self.output_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to optimize {self.input_path}: {e}")
            return False

    def decompress(self):
        if not os.path.isfile(self.input_path):
            logging.error(f"File not found: {self.input_path}")
            return False

        try:
            self.strategy.decompress(self.input_path, self.output_path)
            logging.info(f"Decompressed file saved to: {self.output_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to decompress {self.input_path}: {e}")
            return False
