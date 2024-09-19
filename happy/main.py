import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # start the timer
        start_time = time.time()
        # call the decorated function
        result = func(*args, **kwargs)
        # remeasure the time
        end_time = time.time()
        # compute the elapsed time and print it
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        # return the result of the decorated function execution
        return result

    # return reference to the wrapper function
    return wrapper


def debugger(func):
    def wrapper(*args, **kwargs):
        # print the function name and arguments
        print(f"Calling {func.__name__} with args: {args} kwargs: {kwargs}")
        # call the function
        result = func(*args, **kwargs)
        # print the results
        print(f"{func.__name__} returned: {result}")
        return result

    return wrapper


def retry(max_attempts, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    time.sleep(delay)
            print(f"Function failed after {max_attempts} attempts")

        return wrapper

    return decorator


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Handle the exception
            print(f"An exception occurred: {str(e)}")
            # Optionally, perform additional error handling or logging
            # Reraise the exception if needed

    return wrapper


import functools


def make_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If the first argument is a function, assume we're being used as a decorator
        if len(args) == 1 and callable(args[0]):
            def decorated(target_func):
                @functools.wraps(target_func)
                def new_func(*func_args, **func_kwargs):
                    return func(target_func, *func_args, **func_kwargs)

                return new_func

            return decorated(args[0])
        else:
            # Otherwise, just run the function normally
            return func(*args, **kwargs)

    return wrapper


# Example usage:

@make_decorator
def my_decorator(func, *args, **kwargs):
    print(f"Decorating {func.__name__}")
    result = func(*args, **kwargs)
    return result


@my_decorator
def say_hello():
    print("Hello!")


# When used directly as a function
say_hello()


# When used as a decorator
@my_decorator
def say_goodbye():
    print("Goodbye!")


say_goodbye()
