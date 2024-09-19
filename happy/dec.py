import inspect

def is_decorator(func):
    # Check if the function is callable
    if not callable(func):
        return False

    # Define a sample function to use for inspecting the decorator
    sample_func = lambda: None

    # Check if the function takes exactly one argument
    parameters = list(inspect.signature(func).parameters.values())
    if len(parameters) != 1:
        return False

    # Check if the single argument is callable (i.e., a function)
    if not callable(parameters[0].annotation):
        return False

    # Try to get the result of calling the decorator with a sample function
    try:
        result = func(sample_func)
    except Exception:
        return False

    # Check if the result is callable
    return callable(result)

def normal_func(n):
    return lambda: n + 1

def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Something is happening before the function is called.")
        return func(*args, **kwargs)
    return wrapper

print(is_decorator(my_decorator))  # Output: True
print(is_decorator(normal_func))   # Output: False
