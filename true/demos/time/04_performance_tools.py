"""
Examples of using time-related performance tools and decorators.
"""

import time

from true.time import timeout, timer, Time


@timeout(2.0)
def long_running_task():
    """A task that takes too long and should timeout."""
    time.sleep(3)
    return "This should never be returned"


@timeout(5.0)
def quick_task():
    """A task that completes within the timeout."""
    time.sleep(1)
    return "Task completed successfully"


@timer
def cpu_intensive_task():
    """A CPU-intensive task to demonstrate the timer decorator."""
    result = 0
    for i in range(1000000):
        result += i
    return result


def demo_timeout_decorator():
    """Demonstrate the timeout decorator."""
    print("=== Timeout Decorator ===")

    print("Running quick task...")
    try:
        result = quick_task()
        print(f"Quick task result: {result}")
    except TimeoutError as e:
        print(f"Quick task error: {e}")

    print("\nRunning long task...")
    try:
        result = long_running_task()
        print(f"Long task result: {result}")
    except TimeoutError as e:
        print(f"Long task error: {e}")


def demo_timer_decorator():
    """Demonstrate the timer decorator."""
    print("\n=== Timer Decorator ===")

    print("Running CPU intensive task...")
    result = cpu_intensive_task()
    print(f"Task result: {result}")


def demo_timer_context():
    """Demonstrate the timer context manager."""
    print("\n=== Timer Context Manager ===")

    time_obj = Time.now()

    print("Measuring block execution time...")
    with time_obj.timer():
        # Simulate some work
        time.sleep(1.5)
        result = sum(range(100000))

        print(f"Computed result: {result}")


def demo_performance_comparison():
    """Demonstrate comparing performance of different approaches."""
    print("\n=== Performance Comparison ===")

    @timer
    def method1():
        return sum(i * i for i in range(1000000))

    @timer
    def method2():
        return sum([i * i for i in range(1000000)])

    print("Method 1 (generator):")
    result1 = method1()

    print("\nMethod 2 (list comprehension):")
    result2 = method2()

    print(f"\nResults match: {result1 == result2}")


if __name__ == "__main__":
    demo_timeout_decorator()
    demo_timer_decorator()
    demo_timer_context()
    demo_performance_comparison()
