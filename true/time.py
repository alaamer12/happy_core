"""
This module provides advanced time handling utilities with extended support for time zones, localization,
and time-based operations. It defines several classes and functions to facilitate working with date and time
in various formats and with custom configurations.

Classes:
    - TimeFormat: Enum for specifying different time formats (e.g., 12-hour, 24-hour, ISO, and custom).
    - TimeUnit: Enum for specifying time units (e.g., seconds, minutes, hours, days, months).
    - TimeConfig: Dataclass for configuring time settings, including default timezone and separators.
    - Time: Main class for creating and manipulating time objects with rich functionality, including time
      arithmetic, formatting, rounding, and timezone conversions.

Functions:
    - timeout: Decorator that limits the execution time of a function, raising a TimeoutError if it exceeds a given limit.
    - timer: Decorator that measures the execution time of a function, with an option to use a high-resolution timer.

Features:
    - Time rounding, flooring, and ceiling based on time units.
    - Time difference calculations with specified units.
    - Conversion to different time zones.
    - Flexible formatting with locale support.
    - Context manager for timing code execution.
    - Support for checking if a time instance is within Daylight Saving Time (DST).
    - Serialization to dictionary format for easy access to time components.

This module also provides helper methods for working with multiple time instances, such as finding the earliest
and latest times in a sequence, and ensures compatibility with various input formats, including timestamps,
datetime objects, and formatted strings.
"""

from __future__ import annotations

import calendar
import contextlib
import functools
import locale
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
from functools import lru_cache
from typing import Union, Optional, Dict, List, Any, Callable

import pytz

from true.exceptions import ScheduleError, ScheduleConflictError, ScheduleValidationError

TimeType = Optional[Union[float, str, datetime]]


def timeout(timeout_: float):
    """Decorator that raises TimeoutError if function execution exceeds specified timeout in seconds."""

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Result container for the thread execution
            result = {}

            # Target function to run in the thread, capturing the result
            def target():
                result["value"] = func(*args, **kwargs)

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout_)

            if thread.is_alive():
                raise TimeoutError(f"Timeout of {timeout_} seconds reached")

            return result.get("value")  # Return the result if completed in time

        return wrapper

    return decorator


def timer(func, per_counter: bool = False):
    """Decorator that measures and prints function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time_func = time.perf_counter if per_counter else time.time

        start_time = time_func()

        result = func(*args, **kwargs)

        end_time = time_func()

        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.4f} seconds")
        return result

    return wrapper


class TimeFormat(Enum):
    """Enum for different time formats."""
    HOUR_12 = "12"
    HOUR_24 = "24"
    ISO = "iso"
    CUSTOM = "custom"


class TimeUnit(Enum):
    """Enum for time units."""
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


# noinspection PyUnusedName
@dataclass
class TimeConfig:
    """Configuration class for Time settings."""
    default_timezone: str = "UTC"
    default_format: TimeFormat = TimeFormat.HOUR_24
    date_separator: str = "-"
    time_separator: str = ":"
    datetime_separator: str = " "


@dataclass
class Time:
    """Advanced Time handling class with localization support and extended functionality."""

    def __init__(self, time_input: TimeType = None,
                 timezone_name: Optional[str] = None,
                 config: Optional[TimeConfig] = None
                 ):
        """
        Initialize a Time object.

        Args:
            time_input: Input time (timestamp, datetime string, or datetime object)
            timezone_name: Timezone name (e.g., 'America/New_York')
            config: TimeConfig object for customization
        """
        self.config = config or TimeConfig()
        self._timezone = pytz.timezone(timezone_name or self.config.default_timezone)
        self._datetime: datetime = self._parse_input(time_input)

    @property
    def datetime(self) -> datetime:
        """Get datetime object."""
        return self._datetime

    @property
    def timezone(self) -> str:
        """Get timezone name."""
        return str(self._timezone)

    @property
    def quarter(self) -> int:
        """Get year quarter (1-4)."""
        return (self._datetime.month - 1) // 3 + 1

    def floor(self, unit: TimeUnit) -> 'Time':
        """Floor time to the nearest unit."""
        dt = self._datetime
        if unit == TimeUnit.YEARS:
            dt = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit == TimeUnit.MONTHS:
            dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit == TimeUnit.DAYS:
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == TimeUnit.HOURS:
            dt = dt.replace(minute=0, second=0, microsecond=0)
        elif unit == TimeUnit.MINUTES:
            dt = dt.replace(second=0, microsecond=0)
        elif unit == TimeUnit.SECONDS:
            dt = dt.replace(microsecond=0)
        return Time(dt, str(self._timezone))

    def ceil(self, unit: TimeUnit) -> 'Time':
        """Ceil time to the nearest unit."""
        floored = self.floor(unit)
        if floored == self:
            return self
        return floored.add(1, unit)

    def round(self, unit: TimeUnit) -> 'Time':
        """Round time to the nearest unit."""
        floored = self.floor(unit)
        ceiled = self.ceil(unit)
        if abs(self - floored) < abs(self - ceiled):
            return floored
        return ceiled

    def start_of(self, unit: TimeUnit) -> 'Time':
        """Get start of time unit (alias for a floor)."""
        return self.floor(unit)

    def end_of(self, unit: TimeUnit) -> 'Time':
        """Get end-of-time unit."""
        next_unit = self.add(1, unit)
        # noinspection PyTypeChecker
        return next_unit.floor(unit) - timedelta(microseconds=1)

    def is_between(self, start: 'Time', end: 'Time', inclusive: bool = True) -> bool:
        """Check if time is between start and end times."""
        if inclusive:
            return start <= self <= end
        return start < self < end

    def is_same(self, other: 'Time', unit: TimeUnit) -> bool:
        """Check if two times are in the same time unit."""
        return self.floor(unit) == other.floor(unit)

    @classmethod
    def min(cls, *times: 'Time') -> 'Time':
        """Get the earliest time from a sequence."""
        return min(times, key=lambda t: t.datetime)

    @classmethod
    def max(cls, *times: 'Time') -> 'Time':
        """Get the latest time from a sequence."""
        return max(times, key=lambda t: t.datetime)

    def with_timezone(self, timezone_name: str) -> 'Time':
        """Return new Time instance with different timezone."""
        return Time(self._datetime, timezone_name)

    def with_time(self, hour: int = 0, minute: int = 0,
                  second: int = 0, microsecond: int = 0) -> 'Time':
        """Return new Time instance with specified time components."""
        dt = self._datetime.replace(hour=hour, minute=minute,
                                    second=second, microsecond=microsecond)
        return Time(dt, str(self._timezone))

    def with_date(self, year: Optional[int] = None,
                  month: Optional[int] = None,
                  day: Optional[int] = None) -> 'Time':
        """Return new Time instance with specified date components."""
        dt = self._datetime.replace(
            year=year if year is not None else self._datetime.year,
            month=month if month is not None else self._datetime.month,
            day=day if day is not None else self._datetime.day
        )
        return Time(dt, str(self._timezone))

    @staticmethod
    @lru_cache(maxsize=128)
    def _parse_input(time_input: Optional[Union[float, str, datetime]]) -> datetime:
        """Parse various input formats to a datetime object."""
        if time_input is None:
            return datetime.now(timezone.utc)
        if isinstance(time_input, float):
            return datetime.fromtimestamp(time_input, timezone.utc)
        if isinstance(time_input, str):
            try:
                # Try multiple common datetime formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f",
                            "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                    try:
                        return datetime.strptime(time_input, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
                raise ValueError(f"Unrecognized datetime format: {time_input}")
            except Exception as e:
                raise ValueError(f"Failed to parse datetime string: {e}")
        if isinstance(time_input, datetime):
            return time_input if time_input.tzinfo else time_input.replace(tzinfo=timezone.utc)
        raise ValueError("Input must be a float (timestamp), datetime string, or datetime object.")

    def to_timezone(self, timezone_name: str) -> 'Time':
        """Convert time to different timezone."""
        new_tz = pytz.timezone(timezone_name)
        return Time(self._datetime.astimezone(new_tz), timezone_name)

    def format(self, format_type: TimeFormat = TimeFormat.HOUR_24,
               custom_format: Optional[str] = None,
               locale_name: Optional[str] = None) -> str:
        """
        Format time according to specified format and locale.

        Args:
            format_type: TimeFormat enum value
            custom_format: Custom strftime format string
            locale_name: Locale name (e.g., 'en_US')
        """
        if locale_name:
            try:
                locale.setlocale(locale.LC_TIME, locale_name)
            except locale.Error:
                raise ValueError(f"Unsupported locale: {locale_name}")

        if format_type == TimeFormat.HOUR_12:
            return self._datetime.strftime("%I:%M:%S %p")
        elif format_type == TimeFormat.HOUR_24:
            return self._datetime.strftime("%H:%M:%S")
        elif format_type == TimeFormat.ISO:
            return self._datetime.isoformat()
        elif format_type == TimeFormat.CUSTOM and custom_format:
            return self._datetime.strftime(custom_format)
        else:
            raise ValueError("Invalid format type or missing custom format")

    def difference(self, other: 'Time', unit: TimeUnit = TimeUnit.SECONDS) -> float:
        """Calculate time difference in specified unit."""
        delta = self._datetime - other._datetime
        conversions = {
            TimeUnit.MILLISECONDS: lambda d: d.total_seconds() * 1000,
            TimeUnit.SECONDS: lambda d: d.total_seconds(),
            TimeUnit.MINUTES: lambda d: d.total_seconds() / 60,
            TimeUnit.HOURS: lambda d: d.total_seconds() / 3600,
            TimeUnit.DAYS: lambda d: d.total_seconds() / 86400,
            TimeUnit.WEEKS: lambda d: d.total_seconds() / 604800,
            TimeUnit.MONTHS: lambda d: d.total_seconds() / 2592000,  # approximate
            TimeUnit.YEARS: lambda d: d.total_seconds() / 31536000,  # approximate
        }
        return conversions[unit](delta)

    @staticmethod
    def get_available_timezones() -> List[str]:
        """Return list of available timezone names."""
        return pytz.all_timezones

    def add(self, amount: int, unit: TimeUnit) -> 'Time':
        """Add time duration to current time."""
        additions = {
            TimeUnit.MILLISECONDS: lambda a: timedelta(milliseconds=a),
            TimeUnit.SECONDS: lambda a: timedelta(seconds=a),
            TimeUnit.MINUTES: lambda a: timedelta(minutes=a),
            TimeUnit.HOURS: lambda a: timedelta(hours=a),
            TimeUnit.DAYS: lambda a: timedelta(days=a),
            TimeUnit.WEEKS: lambda a: timedelta(weeks=a),
            TimeUnit.MONTHS: lambda a: self._add_months(a),
            TimeUnit.YEARS: lambda a: self._add_months(a * 12),
        }
        new_datetime = self._datetime + additions[unit](amount)
        return Time(new_datetime, str(self._timezone))

    def _add_months(self, months: int) -> datetime:
        """Helper method to add months to a date."""
        year = self._datetime.year + ((self._datetime.month + months - 1) // 12)
        month = ((self._datetime.month + months - 1) % 12) + 1
        day = min(self._datetime.day, calendar.monthrange(year, month)[1])
        return self._datetime.replace(year=year, month=month, day=day)

    def is_dst(self) -> bool:
        """Check if the current time is in DST."""
        return bool(self._timezone.dst(self._datetime))

    def to_dict(self) -> Dict:
        """Convert a time object to dictionary representation."""
        return {
            'timestamp': self._datetime.timestamp(),
            'iso': self._datetime.isoformat(),
            'timezone': str(self._timezone),
            'is_dst': self.is_dst(),
            'year': self._datetime.year,
            'month': self._datetime.month,
            'day': self._datetime.day,
            'hour': self._datetime.hour,
            'minute': self._datetime.minute,
            'second': self._datetime.second,
            'microsecond': self._datetime.microsecond,
        }

    @contextlib.contextmanager
    def timer(self):
        """A Timer context manager to calculate the time consumed inside a block of code."""
        start_time = time.time()
        yield
        end_time = time.time()
        print(f"Time consumed: {end_time - start_time} seconds")

    @classmethod
    def now(cls, timezone_name: Optional[str] = None) -> 'Time':
        """Get current time in specified timezone."""
        return cls(datetime.now(timezone.utc), timezone_name)

    def __str__(self) -> str:
        """String representation of a time object."""
        return self.format(self.config.default_format)

    def __repr__(self) -> str:
        """Detailed string representation of a time object."""
        return f"Time({self._datetime.isoformat()}, {str(self._timezone)})"

    def __add__(self, other: Union[timedelta, int, float]) -> 'Time':
        """Add timedelta or seconds to Time instance."""
        if isinstance(other, (int, float)):
            other = timedelta(seconds=other)
        if not isinstance(other, timedelta):
            return NotImplemented
        return Time(self._datetime + other, str(self._timezone))

    def __sub__(self, other: Union['Time', timedelta, int, float]) -> Union['Time', timedelta]:
        """Subtract Time, timedelta, or seconds from Time instance."""
        if isinstance(other, Time):
            return self._datetime - other._datetime
        if isinstance(other, (int, float)):
            other = timedelta(seconds=other)
        if not isinstance(other, timedelta):
            return NotImplemented
        return Time(self._datetime - other, str(self._timezone))

    def __eq__(self, other: Any) -> bool:
        """Compare equality with another Time instance."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime == other._datetime

    def __lt__(self, other: Any) -> bool:
        """Compare less than with another Time instance."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime < other._datetime

    def __le__(self, other):
        """Compare less than or equal with another Time instance."""
        if not isinstance(other, Time):
            return NotImplemented
        return self._datetime <= other._datetime


@dataclass
class Event:
    """Represents a scheduled event with comprehensive time management capabilities."""
    name: str
    start_time: Time
    end_time: Time
    description: Optional[str] = None
    recurrence: Optional[str] = None  # 'daily', 'weekly', 'monthly', 'yearly'
    tags: List[str] = None
    priority: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate event data after initialization."""
        self.tags = self.tags or []
        self.metadata = self.metadata or {}

        if self.end_time < self.start_time:
            raise ScheduleValidationError("End time cannot be before start time")

        if self.recurrence and self.recurrence not in {'daily', 'weekly', 'monthly', 'yearly'}:
            raise ScheduleValidationError(f"Invalid recurrence pattern: {self.recurrence}")

    def overlaps(self, other: 'Event') -> bool:
        """Check if this event overlaps with another event."""
        return (self.start_time < other.end_time and
                self.end_time > other.start_time)

    def duration(self, unit: TimeUnit = TimeUnit.MINUTES) -> float:
        """Get event duration in specified unit."""
        return self.start_time.difference(self.end_time, unit)

    def is_recurring(self) -> bool:
        """Check if the event is recurring."""
        return bool(self.recurrence)

    def get_next_occurrence(self) -> Optional['Event']:
        """Get the next occurrence of a recurring event."""
        if not self.is_recurring():
            return None

        duration = self.duration()
        new_start = None

        if self.recurrence == 'daily':
            new_start = self.start_time.add(1, TimeUnit.DAYS)
        elif self.recurrence == 'weekly':
            new_start = self.start_time.add(1, TimeUnit.WEEKS)
        elif self.recurrence == 'monthly':
            new_start = self.start_time.add(1, TimeUnit.MONTHS)
        elif self.recurrence == 'yearly':
            new_start = self.start_time.add(1, TimeUnit.YEARS)

        if new_start:
            return Event(
                name=self.name,
                start_time=new_start,
                end_time=new_start.add(int(duration), TimeUnit.MINUTES),
                description=self.description,
                recurrence=self.recurrence,
                tags=self.tags.copy(),
                priority=self.priority,
                metadata=self.metadata.copy()
            )

    def __str__(self) -> str:
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Schedule:
    """
    Advanced scheduling system with support for complex time-based operations.

    Features:
    - Event management (add, remove, update)
    - Conflict detection and resolution
    - Recurring events support
    - Event filtering and searching
    - Schedule optimization
    - Time block allocation
    - Schedule statistics and analytics
    """

    def __init__(self, timezone_name: Optional[str] = None):
        self._events: List[Event] = []
        self._timezone = timezone_name or TimeConfig().default_timezone
        self._lock = threading.RLock()

    def add_event(self, event: Event, check_conflicts: bool = True) -> None:
        """Add an event to the schedule with optional conflict checking."""
        with self._lock:
            if check_conflicts:
                conflicts = self._find_conflicts(event)
                if conflicts:
                    raise ScheduleConflictError(
                        f"Event conflicts with existing events: {[e.name for e in conflicts]}"
                    )
            self._events.append(event)
            self._events.sort(key=lambda x: x.start_time)

    def remove_event(self, event_name: str) -> Event:
        """Remove an event by name."""
        with self._lock:
            for i, event in enumerate(self._events):
                if event.name == event_name:
                    return self._events.pop(i)
            raise ScheduleError(f"Event '{event_name}' not found")

    def update_event(self, event_name: str, **kwargs) -> Event:
        """Update an existing event with new attributes."""
        with self._lock:
            for event in self._events:
                if event.name == event_name:
                    # Create new event with updated attributes
                    updated = Event(
                        name=kwargs.get('name', event.name),
                        start_time=kwargs.get('start_time', event.start_time),
                        end_time=kwargs.get('end_time', event.end_time),
                        description=kwargs.get('description', event.description),
                        recurrence=kwargs.get('recurrence', event.recurrence),
                        tags=kwargs.get('tags', event.tags),
                        priority=kwargs.get('priority', event.priority),
                        metadata=kwargs.get('metadata', event.metadata)
                    )

                    # Remove old event and add updated one
                    self.remove_event(event_name)
                    self.add_event(updated)
                    return updated

            raise ScheduleError(f"Event '{event_name}' not found")

    def get_events(self, start: Time, end: Time,
                   tags: Optional[List[str]] = None,
                   priority_min: Optional[int] = None) -> List[Event]:
        """Get events within a time range with optional filtering."""
        events = [
            event for event in self._events
            if event.start_time >= start and event.end_time <= end
        ]

        if tags:
            events = [e for e in events if any(tag in e.tags for tag in tags)]

        if priority_min is not None:
            events = [e for e in events if e.priority >= priority_min]

        return events

    def find_free_slots(self, start: Time, end: Time,
                        duration: int, unit: TimeUnit = TimeUnit.MINUTES) -> List[Time]:
        """Find available time slots of specified duration."""
        free_slots = []
        current = start

        for event in self._events:
            if event.start_time > current:
                slot_duration = current.difference(event.start_time, unit)
                if slot_duration >= duration:
                    free_slots.append(current)
            current = max(current, event.end_time)

        if current < end:
            free_slots.append(current)

        return free_slots

    def get_statistics(self, start: Time, end: Time) -> Dict[str, Any]:
        """Calculate comprehensive schedule statistics for a time period."""
        events = self.get_events(start, end)
        total_duration = sum(e.duration() for e in events)
        period_duration = start.difference(end)

        # Calculate priority distribution
        priority_dist = {}
        for event in events:
            priority_dist[event.priority] = priority_dist.get(event.priority, 0) + 1

        return {
            'total_events': len(events),
            'total_duration': total_duration,
            'avg_duration': total_duration / len(events) if events else 0,
            'busy_percentage': (total_duration / period_duration) * 100 if period_duration else 0,
            'tags_distribution': self._calculate_tags_distribution(events),
            'priority_distribution': priority_dist,
            'recurring_events': sum(1 for e in events if e.is_recurring()),
            'unique_tags': len(set(tag for e in events for tag in e.tags))
        }

    def _find_conflicts(self, new_event: Event) -> List[Event]:
        """Find all events that conflict with a given event."""
        return [
            event for event in self._events
            if event.overlaps(new_event)
        ]

    @staticmethod
    def _calculate_tags_distribution(events: List[Event]) -> Dict[str, int]:
        """Calculate the distribution of tags across events."""
        distribution = {}
        for event in events:
            for tag in event.tags:
                distribution[tag] = distribution.get(tag, 0) + 1
        return distribution

    def __str__(self) -> str:
        return f"Schedule with {len(self._events)} events"

    def __repr__(self) -> str:
        return f"Schedule(events={len(self._events)}, timezone={self._timezone})"

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
