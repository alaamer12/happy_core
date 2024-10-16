import contextlib
import inspect
import os
import tempfile
import threading
from datetime import datetime
from functools import wraps
from io import TextIOWrapper
from typing import Optional, Callable

from loguru import logger


# Decorator to ensure a function is run only once
def run_once(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
        return None

    wrapper.has_run = False
    return wrapper


# Singleton LogHandler for managing logging
class Logger:
    _instance = None
    _lock = threading.Lock()

    # Centralized log level configuration
    LEVELS = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "ERROR": "error",
        "CRITICAL": "critical",
        "EXCEPTION": "exception",
        "TRACE": "trace",
    }
    ICONS = {
        "ERROR": ("❌", "<red><bold>"),
        "WARNING": ("⚠️", "<yellow><bold>"),
        "INFO": ("ℹ️", "<blue><bold>"),
        "DEBUG": ("🐞", "<green><bold>"),
        "TRACE": ("🔮", "<cyan><bold>"),
    }

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, only_file: bool = False, dev_mode: bool = True):
        self.log_file = None
        self.only_file = only_file
        self.dev_mode = dev_mode
        self._setup_logging()

    def _setup_logging(self):
        """Sets up logging format and file."""
        _format: str = "{time:YYYY-MM-DD at HH:mm:ss} | <bold>{level}</bold> | {message}"
        if self.dev_mode:
            _format = (
                "{time:YYYY-MM-DD at HH:mm:ss} | module {extra[module_name]} "
                "| line {extra[lineno]} | function {extra[func_name]} | <bold>{level}</bold> | {message}"
            )
        if self.only_file:
            logger.remove()

        logger.add(
            "./logs/file_{time:YYYY-MM-DD}.log",
            format=_format,
            rotation="00:00",
            compression="zip",
            diagnose=True,
            retention="14 days",
        )
        self._configure_log_levels()

    @staticmethod
    def _configure_log_levels():
        """Configures custom log levels."""
        for level, (icon, color) in Logger.ICONS.items():
            logger.level(name=level, icon=icon, color=color)
        with contextlib.suppress(Exception):
            logger.level(name="EXCEPTION", no=50, icon="🔥", color="<magenta><bold>")

    def sort_logs(self, temp: bool = False):
        """Sorts logs by level and writes them to a new file."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = f"./logs/file_{today}.log"
        log_levels = {level: [] for level in self.LEVELS}

        with open(self.log_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            for level in log_levels:
                if level in line:
                    log_levels[level].append(line)
                    break

        def write_log(cursor: TextIOWrapper):
            for level, logs in log_levels.items():
                cursor.write(f"{level:-^80}\n")
                cursor.write("\n".join(logs))
                cursor.write("\n")

        self._write_sorted_log(temp, write_log)

    def _write_sorted_log(self, temp: bool, write_func: Callable):
        """Writes sorted logs either to a temp file or back to the log file."""
        if temp:
            with tempfile.NamedTemporaryFile(
                    dir=os.path.join(os.getcwd(), "logs"),
                    mode="w",
                    delete=False,
                    prefix="sorted_",
                    suffix=".log"
            ) as temp_file:
                write_func(temp_file)
                self.log_file = temp_file.name
        else:
            with open(self.log_file, "w") as log_file:
                write_func(log_file)

    def log_call(
            self, func: Callable = None, *, message: Optional[str] = None, level="INFO", sorted_logs: bool = False
    ) -> Callable:
        """Decorator to log a function call."""

        def decorator(func: Callable):
            func_name = func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                if sorted_logs:
                    self.sort_logs(temp=True)

                self._log_function_call(func, message, level, func_name)

                return func(*args, **kwargs)

            return wrapper

        return decorator(func) if func else decorator

    @run_once
    def _log_function_call(self, func: Callable, message: Optional[str], level: str, func_name: str):
        """Helper to log a specific function call."""
        _level = level.strip().upper()
        if _level not in self.LEVELS:
            raise ValueError(f"Invalid level: {level}")

        module_name = inspect.getmodule(func).__name__
        line_number = inspect.getsourcelines(func)[1]
        log_message = message or f"Call to '{func_name}' at line {line_number}"

        logger_context = logger.bind(func_name=func_name, module_name=module_name,
                                     lineno=line_number) if self.dev_mode else logger
        getattr(logger_context, self.LEVELS[_level])(log_message)

    def remove_duplicate_logs(self):
        """Removes duplicate log entries from the log file."""
        with open(self.log_file, "r") as f:
            lines = f.read().split("\n")

        unique_lines = list(dict.fromkeys(lines))  # Using dict to remove duplicates

        with open(self.log_file, "w") as f:
            f.write("\n".join(unique_lines))

    def warn(self, message: str):
        pass
