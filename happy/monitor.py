import time
import logging
import functools


# Step 1: Create a decorator that wraps the execution of a function
def monitor_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logging.info(f"Function {func.__name__} executed successfully in {elapsed_time:.4f} seconds.")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logging.error(f"Function {func.__name__} failed after {elapsed_time:.4f} seconds with error: {e}")
            raise

    return wrapper

def wrap_with_monitoring(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            print(f"Entering: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"Exiting: {func.__name__}")
            return result
        except Exception as e:
            # Here you could send the error to an external monitoring system like Sentry
            print(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


# Step 2: Example function that we want to monitor
@monitor_function
def example_function(n):
    if n == 0:
        raise ValueError("n cannot be zero!")
    time.sleep(n)
    return f"Slept for {n} seconds"


# Step 3: Using the monitored function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # This call will be wrapped
    print(example_function(2))

    # This call will trigger an exception and be logged
    print(example_function(0))
