import re
from decimal import Decimal, getcontext


def is_even(number: int) -> bool:
    return number % 2 == 0


def is_odd(number: int) -> bool:
    return number % 2 == 1


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True


def to_scientific_form(num: int, fixed_precision: bool = True) -> str:
    """Convert a number to scientific notation (e form) with arbitrary precision."""
    try:
        # Set the precision for Decimal (adjust as needed)
        getcontext().prec = 100  # Sufficiently high precision for large numbers
        decimal_num = Decimal(num)
        precision = 10 if fixed_precision else len(str(num))
        if precision > 100:
            import warnings
            warnings.warn("Precision is too high. This may result in an error."
                          " setting `fixed_precision` to true to avoid error but it may"
                          " result in a loss of precision.", stacklevel=2)

        # Convert to scientific notation
        scientific_notation = f"{decimal_num:.{precision}e}"
        return scientific_notation
    except (ValueError, OverflowError) as e:
        return f"Error converting number: {e}"


def scientific_to_int(scientific_str):
    """Convert a scientific notation string to an integer."""
    try:
        # Convert to Decimal first
        decimal_num = Decimal(scientific_str)
        # Then convert to integer
        return int(decimal_num)
    except (ValueError, OverflowError) as e:
        return f"Error converting scientific notation to int: {e}"


def is_scientific_notation(num_str):
    """Check if the given string is in scientific notation."""
    pattern = r'^[+-]?(\d+(\.\d+)?|\.\d+)([eE][+-]?\d+)?$'
    return bool(re.match(pattern, num_str))
