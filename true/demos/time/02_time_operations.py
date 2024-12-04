"""
Examples of time operations and manipulations using the Time class.
"""

from true.time import Time, TimeUnit


def demo_time_arithmetic():
    """Demonstrate time arithmetic operations."""
    print("=== Time Arithmetic ===")

    time_obj = Time.now()
    print(f"Current time: {time_obj}")

    # Adding time
    future = time_obj.add(2, TimeUnit.HOURS)
    print(f"2 hours later: {future}")

    # Adding days
    next_week = time_obj.add(7, TimeUnit.DAYS)
    print(f"Next week: {next_week}")

    # Time difference
    diff = next_week.difference(time_obj, TimeUnit.HOURS)
    print(f"Hours between: {diff}")


def demo_time_rounding():
    """Demonstrate time rounding operations."""
    print("\n=== Time Rounding ===")

    time_obj = Time.now()
    print(f"Original time: {time_obj}")

    # Round to nearest hour
    rounded = time_obj.round(TimeUnit.HOURS)
    print(f"Rounded to hour: {rounded}")

    # Floor to hour
    floored = time_obj.floor(TimeUnit.HOURS)
    print(f"Floored to hour: {floored}")

    # Ceil to hour
    ceiled = time_obj.ceil(TimeUnit.HOURS)
    print(f"Ceiled to hour: {ceiled}")


def demo_time_comparison():
    """Demonstrate time comparison operations."""
    print("\n=== Time Comparison ===")

    time1 = Time.now()
    time2 = time1.add(1, TimeUnit.HOURS)

    print(f"Time 1: {time1}")
    print(f"Time 2: {time2}")

    print(f"time1 < time2: {time1 < time2}")
    print(f"time1 == time2: {time1 == time2}")
    print(f"time1 is between: {time1.is_between(time1, time2)}")
    print(f"Same day: {time1.is_same(time2, TimeUnit.DAYS)}")


def demo_time_ranges():
    """Demonstrate working with time ranges."""
    print("\n=== Time Ranges ===")

    time_obj = Time.now()

    # Start and end of day
    day_start = time_obj.start_of(TimeUnit.DAYS)
    day_end = time_obj.end_of(TimeUnit.DAYS)

    print(f"Start of day: {day_start}")
    print(f"End of day: {day_end}")

    # Start and end of month
    month_start = time_obj.start_of(TimeUnit.MONTHS)
    month_end = time_obj.end_of(TimeUnit.MONTHS)

    print(f"Start of month: {month_start}")
    print(f"End of month: {month_end}")


if __name__ == "__main__":
    demo_time_arithmetic()
    demo_time_rounding()
    demo_time_comparison()
    demo_time_ranges()
