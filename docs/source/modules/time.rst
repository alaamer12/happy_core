Time Module
===========

.. module:: happy_core.time

A powerful time management module providing intuitive interfaces for handling time-related operations, scheduling, and time series analysis.

Key Features
-----------

- ⏰ **Intuitive time manipulation** with human-readable interfaces
- 📅 **Flexible scheduling** with cron-like expressions
- 🔄 **Time zone aware** operations
- 📊 **Time series analysis** tools
- ⚡ **High-performance** implementations

TimeUtils
--------

.. py:class:: TimeUtils

   A comprehensive utility class for time-related operations.

   **Key Benefits:**
   
   - Human-readable time manipulation
   - Timezone awareness
   - Performance optimized
   - Thread-safe operations
   
   .. code-block:: python

      from happy_core.time import TimeUtils
      
      # Human-readable time operations
      next_week = TimeUtils.now().add_days(7)
      last_month = TimeUtils.now().subtract_months(1)
      
      # Timezone handling
      utc_time = TimeUtils.to_utc(local_time)
      local_time = TimeUtils.to_local(utc_time)
   
   .. py:classmethod:: now(tz: Optional[str] = None) -> datetime
      
      Get current timestamp.

      :param tz: Optional timezone name
      :return: Current datetime
      :raises TimeZoneError: If timezone is invalid

   .. py:classmethod:: parse(time_str: str, format: Optional[str] = None) -> datetime
      
      Parse time string into datetime.

      :param time_str: Time string to parse
      :param format: Optional format string
      :return: Parsed datetime
      :raises ParseError: If parsing fails

   .. py:classmethod:: format_iso(dt: datetime) -> str
      
      Format datetime in ISO format.

      :param dt: Datetime to format
      :return: ISO formatted string

Scheduler
--------

.. py:class:: Scheduler

   A flexible task scheduling system with cron-like expressions.

   **Features:**
   
   - Cron-like scheduling
   - Task prioritization
   - Error handling
   - Task dependencies
   
   .. code-block:: python

      from happy_core.time import Scheduler
      
      scheduler = Scheduler()
      
      # Schedule task with cron expression
      @scheduler.cron("0 9 * * 1-5")  # Weekdays at 9 AM
      def daily_task():
          process_daily_data()
      
      # Schedule with interval
      scheduler.every(minutes=30).do(check_status)
   
   .. py:method:: schedule(task_func: Callable, run_at: datetime, **kwargs) -> str
      
      Schedule a one-time task.

      :param task_func: Function to execute
      :param run_at: Execution time
      :return: Task ID

   .. py:method:: cron(expression: str) -> Callable
      
      Schedule task using cron expression.

      :param expression: Cron expression
      :return: Decorator for task function

TimeSeries
---------

.. py:class:: TimeSeries

   Tools for time series analysis and manipulation.

   **Capabilities:**
   
   - Data resampling
   - Rolling windows
   - Time-based aggregation
   - Missing data handling
   
   .. code-block:: python

      from happy_core.time import TimeSeries
      
      # Create time series
      ts = TimeSeries(data, timestamp_column="date")
      
      # Resample to daily frequency
      daily = ts.resample("1D").mean()
      
      # Rolling average
      moving_avg = ts.rolling(window="7D").mean()

Best Practices
------------

1. **Timezone Handling**

   Always be explicit about timezones:

   .. code-block:: python

      # Good - explicit timezone
      meeting_time = TimeUtils.parse("2024-01-01 10:00", tz="America/New_York")
      
      # Bad - implicit timezone
      meeting_time = TimeUtils.parse("2024-01-01 10:00")

2. **Task Scheduling**

   Use appropriate scheduling methods:

   .. code-block:: python

      # Good - clear scheduling intent
      scheduler.daily_at("09:00").do(morning_task)
      
      # Better - with error handling
      @scheduler.cron("0 9 * * *")
      @retry(max_attempts=3)
      def morning_task():
          process_morning_data()

3. **Performance Optimization**

   Cache time-intensive calculations:

   .. code-block:: python

      from happy_core.toolkits import cache
      
      @cache(ttl=3600)
      def calculate_daily_metrics(date: datetime) -> Dict[str, float]:
          return TimeSeries(data).resample("1D").aggregate(metrics)

Advanced Usage
------------

1. **Custom Time Formats**

   Create specialized time formats:

   .. code-block:: python

      class CustomTimeFormat:
          def __init__(self, format_string: str):
              self.format = format_string
          
          def parse(self, time_str: str) -> datetime:
              return TimeUtils.parse(time_str, self.format)
          
          def format(self, dt: datetime) -> str:
              return dt.strftime(self.format)

2. **Task Dependencies**

   Implement task dependencies:

   .. code-block:: python

      scheduler = Scheduler()
      
      @scheduler.task("task_1")
      def first_task():
          return process_data()
      
      @scheduler.task("task_2")
      @scheduler.depends_on("task_1")
      def second_task(task_1_result):
          return analyze_data(task_1_result)

3. **Custom Time Series Analysis**

   Implement custom analysis methods:

   .. code-block:: python

      class CustomTimeSeries(TimeSeries):
          def custom_metric(self, window: str = "7D") -> float:
              """Calculate custom metric over time window."""
              return self.rolling(window=window).apply(self._calc_metric)
          
          def _calc_metric(self, window_data: pd.Series) -> float:
              # Custom calculation logic
              pass

Examples
-------

Basic Time Operations
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from happy_core.time import TimeUtils

   # Get current time in different formats
   timestamp = TimeUtils.now()  # Unix timestamp
   iso_time = TimeUtils.now_iso()  # ISO format
   
   # Format time
   formatted = TimeUtils.format_time(timestamp, "%Y-%m-%d %H:%M:%S")
   
   # Parse time string
   parsed = TimeUtils.parse_time("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")

Using Timer
~~~~~~~~~

.. code-block:: python

   from happy_core.time import Timer
   import time

   # Basic timer usage
   with Timer() as timer:
       time.sleep(1)  # Some operation
       elapsed = timer.elapsed  # Get elapsed time
   
   # Timer with callback
   def on_complete(elapsed):
       print(f"Operation took {elapsed:.2f} seconds")
   
   timer = Timer(callback=on_complete)
   with timer:
       time.sleep(2)  # Some operation

Scheduling Tasks
~~~~~~~~~~~~~~

.. code-block:: python

   from happy_core.time import Scheduler
   from datetime import datetime, timedelta

   scheduler = Scheduler()

   # Schedule a one-time task
   def task():
       print("Task executed!")

   # Schedule for 5 minutes from now
   future_time = datetime.now() + timedelta(minutes=5)
   scheduler.schedule_once(task, future_time)

   # Schedule a recurring task
   def recurring_task():
       print("Recurring task executed!")

   # Run every hour
   scheduler.schedule_recurring(recurring_task, timedelta(hours=1))

   # Start the scheduler
   scheduler.start()

Performance Monitoring
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from happy_core.time import Timer
   from typing import List
   import time

   def measure_performance(func):
       def wrapper(*args, **kwargs):
           with Timer() as timer:
               result = func(*args, **kwargs)
               print(f"{func.__name__} took {timer.elapsed:.2f} seconds")
           return result
       return wrapper

   @measure_performance
   def process_data(data: List[int]) -> List[int]:
       time.sleep(0.1)  # Simulate processing
       return sorted(data)

   # Usage
   data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
   processed = process_data(data)
