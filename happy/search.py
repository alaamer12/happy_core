import asyncio
import concurrent
import multiprocessing
import os
import threading
from abc import abstractmethod, ABC
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager
from typing import Callable, List, Union, Any, Optional, Dict
import re

from happy.exceptions import FileTypeNotSupported
from happy.protocols import LoggerProtocol


class GrepContextManager(AbstractContextManager):
    def __init__(self):
        self._resources = []

    def __enter__(self):
        # Initialize resources, e.g., file handles
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up resources
        for resource in self._resources:
            resource.close()


# Abstract Grep strategy for different file types
class GrepStrategy(ABC):
    @abstractmethod
    def search(self, pattern: str, file_path: str) -> List[str]:
        pass


# Concrete strategy for plain text files
class TxtGrepStrategy(GrepStrategy):
    def search(self, pattern: str, file_path: str) -> List[str]:
        with open(file_path, 'r') as file:
            content = file.read()
        return re.findall(pattern, content)


# Concrete strategy for .pdf files (Requires PyPDF2 or similar library)
class PdfGrepStrategy(GrepStrategy):
    def search(self, pattern: str, file_path: str) -> List[str]:
        # Assume PyPDF2 or pdfminer is used here
        # content = extract_pdf_text(file_path)
        # return re.findall(pattern, content)
        return []


# Extend for other file types like .docx, .xlsx etc.
# Use libraries like python-docx for .docx, openpyxl for .xlsx

# Grep class that manages different strategies
class Grep:
    _strategies = {
        ".txt": TxtGrepStrategy(),
        ".pdf": PdfGrepStrategy(),
        # ".docx": DocxGrepStrategy(),
        # ".xlsx": XlsxGrepStrategy(),
        # Extend more strategies as needed
    }

    def __init__(self, logger: Optional[LoggerProtocol] = None):
        self.logger = logger

    def log(self, message: str):
        if self.logger:
            self.logger.log(message)

    def _get_strategy(self, file_path: str) -> GrepStrategy:
        ext = os.path.splitext(file_path)[1]
        if ext not in self._strategies:
            raise FileTypeNotSupported(f"File type {ext} is not supported.")
        return self._strategies[ext]

    def grep(self, pattern: str, file_path: str) -> List[str]:
        strategy = self._get_strategy(file_path)
        self.log(f"Searching for pattern '{pattern}' in {file_path}")
        return strategy.search(pattern, file_path)

    # Multi-threading support
    def grep_multithread(self, pattern: str, file_paths: List[str]) -> List[str]:
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda path: self.grep(pattern, path), file_paths))
        return results

    # Multi-processing support
    def grep_multiprocessing(self, pattern: str, file_paths: List[str]) -> List[str]:
        with multiprocessing.Pool() as pool:
            results = pool.map(lambda path: self.grep(pattern, path), file_paths)
        return results

    def _log(self, message: str):
        if self.logging_protocol:
            self.logging_protocol.log(message)

    def _validate_file(self, filepath: str):
        _, extension = os.path.splitext(filepath)
        if extension not in self.supported_extensions:
            raise FileTypeNotSupported(f"File type {extension} is not supported.")

    def _grep_in_txt(self, filepath: str, pattern: str) -> List[str]:
        self._log(f"Grep in .txt file: {filepath}")
        result = []
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                if re.search(pattern, line):
                    result.append(line.strip())
        return result

    async def _grep_in_async(self, filepath: str, pattern: str) -> List[str]:
        return await asyncio.to_thread(self._grep_in_txt, filepath, pattern)

    def grep_in_file(self, filepath: str, pattern: str) -> List[str]:
        """Grep a file for the given pattern (sync version)."""
        self._validate_file(filepath)
        _, extension = os.path.splitext(filepath)

        if extension == ".txt":
            return self._grep_in_txt(filepath, pattern)
        # TODO: Add support for other file types like .pdf, .docx, .xlsx, etc.

        raise FileTypeNotSupported(f"Support for {extension} is not implemented yet.")

    async def grep_in_file_async(self, filepath: str, pattern: str) -> List[str]:
        """Grep a file for the given pattern (async version)."""
        self._validate_file(filepath)
        _, extension = os.path.splitext(filepath)

        if extension == ".txt":
            return await self._grep_in_async(filepath, pattern)
        # TODO: Add async support for other file types

        raise FileTypeNotSupported(f"Support for {extension} is not implemented yet.")

    def grep_multiple_files(self, filepaths: List[str], pattern: str) -> dict:
        """Grep multiple files concurrently using multi-threading."""
        self._log("Grep multiple files concurrently.")
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.grep_in_file, filepath, pattern): filepath for filepath in filepaths}
            for future in concurrent.futures.as_completed(futures):
                filepath = futures[future]
                try:
                    results[filepath] = future.result()
                except Exception as e:
                    self._log(f"Error grepping {filepath}: {e}")
        return results

    async def grep_multiple_files_async(self, filepaths: List[str], pattern: str) -> dict:
        """Grep multiple files concurrently using asyncio and thread pool."""
        self._log("Grep multiple files asynchronously.")
        tasks = [self.grep_in_file_async(filepath, pattern) for filepath in filepaths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(filepaths, results))

    # Async support
    async def grep_async(self, pattern: str, file_paths: List[str]) -> List[str]:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.grep, pattern, path) for path in file_paths]
        return await asyncio.gather(*tasks)

    # Context management
    def grep_with_context(self, pattern: str, file_path: str) -> List[str]:
        with GrepContextManager():
            return self.grep(pattern, file_path)

    # String representations
    def __str__(self) -> str:
        return f"Grep Utility supporting: {list(self._strategies.keys())}"

    def __repr__(self) -> str:
        return f"<Grep(Strategies={list(self._strategies.keys())})>"



# Optional logger implementation
class DefaultLogger:
    def log(self, message: str) -> None:
        print(f"LOG: {message}")


# Custom Exceptions
class SearchException(Exception):
    pass


class FileNotFoundException(SearchException):
    pass


class InvalidPatternException(SearchException):
    pass


# Context Manager
class SearchContextManager:
    def __enter__(self):
        # Set up any necessary context
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Handle context teardown
        if exc_type is not None:
            raise SearchException("An error occurred during the search operation.")


# Search class with advanced functionality
class Search:
    def __init__(self, logger: Optional[LoggerProtocol] = None):
        self.logger = logger or DefaultLogger()
        self.pool_size = os.cpu_count()
        self.results = []

    def __str__(self) -> str:
        return f"Search utility with {len(self.results)} search results."

    def __repr__(self) -> str:
        return f"<Search(pool_size={self.pool_size}, results={len(self.results)})>"

    def search_in_file(self, pattern: str, file_path: str, regex: bool = True) -> List[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundException(f"File not found: {file_path}")
        self.logger.log(f"Searching in file: {file_path}")

        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return self._apply_search(pattern, content, regex)
        except Exception as e:
            raise SearchException(f"Error searching file: {str(e)}")

    def search_in_database(self, query: str, db_connection: Any) -> List[Any]:
        # Simulate database search logic here
        self.logger.log(f"Executing database search for query: {query}")
        try:
            with SearchContextManager():
                # Simulating a search operation in database
                return db_connection.execute(query).fetchall()
        except Exception as e:
            raise SearchException(f"Database search failed: {str(e)}")

    def search_in_data(self, pattern: Union[str, re.Pattern], data: Any, regex: bool = True) -> List[Any]:
        if isinstance(data, (str, list, dict)):
            self.logger.log(f"Searching in data: {type(data).__name__}")
            return self._apply_search(pattern, data, regex)
        raise SearchException("Unsupported data type for search.")

    def search_async(self, pattern: str, data: Union[str, List[str]], regex: bool = True) -> List[str]:
        self.logger.log(f"Starting async search.")
        return asyncio.run(self._async_search(pattern, data, regex))

    async def _async_search(self, pattern: str, data: Union[str, List[str]], regex: bool) -> List[str]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._apply_search, pattern, data, regex)

    def _apply_search(self, pattern: Union[str, re.Pattern], data: Union[str, List[str], Dict], regex: bool) -> List[
        Any]:
        results = []
        if isinstance(data, str):
            if regex:
                return re.findall(pattern, data)
            else:
                return [line for line in data.splitlines() if pattern in line]

        if isinstance(data, list):
            for item in data:
                if regex:
                    if re.search(pattern, item):
                        results.append(item)
                else:
                    if pattern in item:
                        results.append(item)

        if isinstance(data, dict):
            for key, value in data.items():
                if regex:
                    if re.search(pattern, str(key)) or re.search(pattern, str(value)):
                        results.append({key: value})
                else:
                    if pattern in str(key) or pattern in str(value):
                        results.append({key: value})
        return results

    def search_multithreaded(self, pattern: str, data_list: List[str], regex: bool = True) -> List[str]:
        self.logger.log("Starting multithreaded search.")
        results = []
        threads = []
        lock = threading.Lock()

        def thread_task(data_chunk: str):
            nonlocal results
            try:
                res = self._apply_search(pattern, data_chunk, regex)
                with lock:
                    results.extend(res)
            except Exception as e:
                self.logger.log(f"Error in thread: {e}")

        chunk_size = len(data_list) // self.pool_size
        for i in range(self.pool_size):
            chunk = data_list[i * chunk_size:(i + 1) * chunk_size]
            thread = threading.Thread(target=thread_task, args=(chunk,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return results

    def search_multiprocessing(self, pattern: str, data_list: List[str], regex: bool = True) -> List[str]:
        self.logger.log("Starting multiprocessing search.")
        with multiprocessing.Pool(self.pool_size) as pool:
            chunks = [data_list[i::self.pool_size] for i in range(self.pool_size)]
            results = pool.starmap(self._apply_search, [(pattern, chunk, regex) for chunk in chunks])
        return [item for sublist in results for item in sublist]

    def search_with_custom_algorithm(self, pattern: str, data: List[str],
                                     algorithm: Callable[[str, List[str]], List[str]]) -> List[str]:
        self.logger.log("Using custom algorithm for search.")
        return algorithm(pattern, data)