from deprecated import deprecated


class ExtendedDeprecated:
    def __init__(self, reason, version):
        self.reason = reason
        self.version = version

    def __call__(self, func):
        deprecated_decorator = deprecated(reason=self.reason, version=self.version)
        wrapped_func = deprecated_decorator(func)

        def wrapper(*args, **kwargs):
            # Add your extended functionality here
            # print(f"This function is deprecated. Reason: {self.reason}. Please use `{func.__name__}` instead.")

            # Call the original function
            return wrapped_func(*args, **kwargs)

        return wrapper


# Create an instance of the extended decorator with custom message
extended_decorator = ExtendedDeprecated(reason="Use `calculation` instead", version="0.1.0")


@extended_decorator
def calculation(x, y, op):
    return eval(f"{x} {op} {y}")


# Call the extended function
print(calculation(1, 2, "+"))
