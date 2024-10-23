import inspect
import os
import tempfile
from datetime import datetime
from functools import wraps
from io import TextIOWrapper
from typing import Optional, Callable
from happy import run_once, SingletonMeta
from loguru import logger

UNIX_LOGGING_FORMAT_STYLE = "[{level}]  [{time.iso}]: {extra[func_name]} {message} {time.iso}"
HAPPY_LOGGING_FORMAT_STYLE = (
                "{time:YYYY-MM-DD at HH:mm:ss} | module {extra[module_name]} "
                "| line {extra[lineno]} | function {extra[func_name]} | <bold>{level}</bold> | {message}"
            )

class InvalidLoggingFormat(ValueError):
    pass


LEVELS = {
    "DEBUG": "debug",
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical",
    "TRACE": "trace",
}
ICONS = {
    "DEBUG": ("🐞", "<green><bold>"),
    "INFO": ("ℹ️", "<blue><bold>"),
    "WARNING": ("⚠️", "<yellow><bold>"),
    "ERROR": ("❌", "<red>"),
    "CRITICAL": ("x", "<red><bold>"),
    "TRACE": ("🔮", "<cyan>"),
}

class Logger(logger, metaclass=SingletonMeta):
    def __init__(self, _format: Optional[str], file_only: bool = False):
        self.log_file = None
        self.file_only = file_only
        self._setup_logging()
        self._format = _format

    def _setup_logging(self):
        """Sets up logging format and file."""
        if self.file_only:
            logger.remove()

        logger.add(
            "./logs/file_{time:YYYY-MM-DD}.log",
            format=self._format,
            rotation="00:00",
            compression="zip",
            diagnose=True,
            retention="14 days",
        )
        self._configure_log_levels()

    @staticmethod
    def _configure_log_levels():
        """Configures custom log levels."""
        for level, (icon, color) in ICONS.items():
            logger.level(name=level, icon=icon, color=color)

    def sort_logs(self, temp: bool = False):
        """Sorts logs by level and writes them to a new file."""
        today = str(datetime.today())
        self.log_file = f"./logs/file_{today}.log"
        log_levels = {level: [] for level in LEVELS}

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

    def deprecated(self):
        # TODO: Implement this
        pass

    def silent_deprecated(self):
        # TODO: Implement this
        pass

    @run_once
    def _log_function_call(self, func: Callable, message: Optional[str], level: str, func_name: str):
        """Helper to log a specific function call."""
        _level = level.strip().upper()
        if _level not in LEVELS:
            raise ValueError(f"Invalid level: {level}")

        module_name = inspect.getmodule(func).__name__
        line_number = inspect.getsourcelines(func)[1]
        log_message = message or f"Call to '{func_name}' at line {line_number}"

        logger_context = logger.bind(func_name=func_name, module_name=module_name,
                                     lineno=line_number)
        getattr(logger_context, LEVELS[_level])(log_message)

    def remove_duplicate_logs(self):
        """Removes duplicate log entries from the log file."""
        with open(self.log_file, "r") as f:
            lines = f.read().split("\n")

        unique_lines = list(dict.fromkeys(lines))  # Using dict to remove duplicates

        with open(self.log_file, "w") as f:
            f.write("\n".join(unique_lines))

    def warn(self, message: str):
        # TODO: implement
        pass
