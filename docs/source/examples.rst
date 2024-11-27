Examples
========

This section provides practical examples of using the Happy Core library features.

Time Handling
-------------

Basic Time Operations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from happy_core.time import Time, TimeUnit, TimeFormat, TimeConfig

    # Create time instances
    current = Time.now()  # Current time in UTC
    ny_time = Time.now("America/New_York")  # Current time in NY

    # Custom time configuration
    config = TimeConfig(
        default_timezone="Europe/London",
        default_format=TimeFormat.HOUR_24,
        date_separator="-"
    )
    london_time = Time(timezone_name="Europe/London", config=config)

Time Formatting and Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Format time in different styles
    time_obj = Time.now()
    
    # 24-hour format
    print(time_obj.format(TimeFormat.HOUR_24))  # e.g., "14:30:00"
    
    # 12-hour format
    print(time_obj.format(TimeFormat.HOUR_12))  # e.g., "02:30:00 PM"
    
    # ISO format
    print(time_obj.format(TimeFormat.ISO))  # e.g., "2024-01-20T14:30:00+00:00"
    
    # Custom format with locale
    print(time_obj.format(
        TimeFormat.CUSTOM,
        custom_format="%B %d, %Y",
        locale_name="fr_FR"
    ))  # e.g., "20 janvier 2024"

Time Calculations
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from happy_core.time import Time, TimeUnit

    time_obj = Time.now()

    # Add time units
    tomorrow = time_obj.add(1, TimeUnit.DAYS)
    next_week = time_obj.add(1, TimeUnit.WEEKS)
    
    # Time difference
    diff = next_week.difference(time_obj, TimeUnit.DAYS)  # 7.0
    
    # Round times
    rounded = time_obj.round(TimeUnit.HOURS)
    floor = time_obj.floor(TimeUnit.HOURS)
    ceil = time_obj.ceil(TimeUnit.HOURS)

Time Comparisons
~~~~~~~~~~~~~~~~

.. code-block:: python

    start = Time.now()
    end = start.add(1, TimeUnit.HOURS)
    
    # Check if time is between two times
    check_time = Time.now()
    is_between = check_time.is_between(start, end)
    
    # Compare times
    are_same_hour = start.is_same(end, TimeUnit.HOURS)
    
    # Find earliest/latest times
    times = [Time.now() for _ in range(3)]
    earliest = Time.min(*times)
    latest = Time.max(*times)

Performance Measurement
-----------------------

Using the Timer Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from happy_core.time import timer
    
    @timer
    def expensive_operation():
        # Some time-consuming operation
        result = sum(i * i for i in range(1000000))
        return result
    
    # Timer will print execution time
    result = expensive_operation()

Using Timeout Decorator
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from happy_core.time import timeout
    
    @timeout(5.0)  # 5 seconds timeout
    def long_running_operation():
        # Operation that might take too long
        import time
        time.sleep(6)  # Will raise TimeoutError
    
    try:
        long_running_operation()
    except TimeoutError:
        print("Operation timed out!")

Context Manager for Timing
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from happy_core.time import Time
    
    time_obj = Time.now()
    
    with time_obj.timer() as t:
        # Some operation to time
        result = sum(i * i for i in range(1000000))
    
    print(f"Operation took {t.elapsed} seconds")

Best Practices
--------------

1. **Timezone Handling**

   Always be explicit about timezones:

   .. code-block:: python

       # Good - explicit timezone
       ny_time = Time.now("America/New_York")
       
       # Less good - uses default UTC
       current = Time.now()

2. **Time Comparisons**

   Use appropriate comparison methods:

   .. code-block:: python

       # Good - explicit unit comparison
       if time1.is_same(time2, TimeUnit.DAYS):
           process_daily_data()
       
       # Less good - exact timestamp comparison
       if time1 == time2:
           process_data()

3. **Performance Monitoring**

   Use built-in timing utilities:

   .. code-block:: python

       @timer
       def critical_operation():
           # Your code here
           pass
       
       # Or use context manager for specific blocks
       with Time.now().timer() as t:
           # Critical code block
           pass
