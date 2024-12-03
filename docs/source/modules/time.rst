Time Module
===========

.. module:: true.time

This module provides advanced time handling utilities with extended support for time zones, localization,
and time-based operations.

Classes
-------

TimeFormat
~~~~~~~~~

.. autoclass:: TimeFormat
   :members:
   :undoc-members:
   :show-inheritance:

   An enumeration for different time formats.

   * HOUR_12: 12-hour format
   * HOUR_24: 24-hour format
   * ISO: ISO format
   * CUSTOM: Custom format

TimeUnit
~~~~~~~~

.. autoclass:: TimeUnit
   :members:
   :undoc-members:
   :show-inheritance:

   An enumeration for time units.

   * MILLISECONDS: Milliseconds unit
   * SECONDS: Seconds unit
   * MINUTES: Minutes unit
   * HOURS: Hours unit
   * DAYS: Days unit
   * WEEKS: Weeks unit
   * MONTHS: Months unit
   * YEARS: Years unit

TimeConfig
~~~~~~~~~

.. autoclass:: TimeConfig
   :members:
   :undoc-members:
   :show-inheritance:

   Configuration class for Time settings.

   :param default_timezone: Default timezone (default: "UTC")
   :param default_format: Default time format (default: TimeFormat.HOUR_24)
   :param date_separator: Separator for date components (default: "-")
   :param time_separator: Separator for time components (default: ":")
   :param datetime_separator: Separator between date and time (default: " ")

Time
~~~~

.. autoclass:: Time
   :members:
   :undoc-members:
   :show-inheritance:

   Advanced Time handling class with localization support and extended functionality.

   Key Features:
   
   * Time rounding, flooring, and ceiling based on time units
   * Time difference calculations with specified units
   * Conversion to different time zones
   * Flexible formatting with locale support
   * Support for checking if a time instance is within DST
   * Serialization to dictionary format

Event
~~~~~

.. autoclass:: Event
   :members:
   :undoc-members:
   :show-inheritance:

   Represents a scheduled event with comprehensive time management capabilities.

   :param name: Event name
   :param start_time: Event start time
   :param end_time: Event end time
   :param description: Optional event description
   :param recurrence: Optional recurrence pattern
   :param tags: Optional list of tags
   :param priority: Event priority (default: 0)
   :param metadata: Optional metadata dictionary

Schedule
~~~~~~~~

.. autoclass:: Schedule
   :members:
   :undoc-members:
   :show-inheritance:

   Advanced scheduling system with support for complex time-based operations.

   Features:
   
   * Event management (add, remove, update)
   * Conflict detection and resolution
   * Recurring events support
   * Event filtering and searching
   * Schedule optimization
   * Time block allocation
   * Schedule statistics and analytics

Functions
---------

timeout
~~~~~~~

.. autofunction:: timeout

   Decorator that raises TimeoutError if function execution exceeds specified timeout in seconds.

   :param timeout: Maximum execution time in seconds
   :raises: TimeoutError if execution time exceeds the specified timeout

timer
~~~~~

.. autofunction:: timer

   Decorator that measures and prints function execution time.

   :param per_counter: Use performance counter for higher precision if True
   :return: Wrapped function that prints execution time