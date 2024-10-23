

class RangingEnum:
    """Enumeration for integer values within a specified range.

    This class ensures that values are of type int and fall within the
    provided minimum and maximum limits.

    Args:
        value (int): The integer value to be validated and stored.
        min_value (int): The minimum allowed value (inclusive).
        max_value (int): The maximum allowed value (inclusive).

    Raises:
        EnumTypeError: If the provided value is not an int.
        EnumValidationError: If the value is not within the specified range.
    """


class ByteEnum:
    """Enumeration for byte values.

    This class ensures that values are of type bytes.

    Args:
        value (bytes): The byte value to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not of type bytes.
    """


class FloatEnum:
    """Enumeration for float values.

    This class ensures that values are of type float.

    Args:
        value (float): The float value to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not of type float.
    """


class DictEnum:
    """Enumeration for dictionary values.

    This class ensures that a single dictionary is provided during instantiation.

    Args:
        *args: Positional arguments (only a single dictionary is allowed).
        **kwargs: Keyword arguments to initialize the dictionary.

    Raises:
        EnumValidationError: If more than one argument is provided or the first argument is not a dictionary.
    """


class SetEnum:
    """Enumeration for set values.

    This class ensures that the provided value is of type set, list, or tuple.

    Args:
        iterable (Any): An iterable (set, list, or tuple) to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not of type set, list, or tuple.
    """


class ListEnum:
    """Enumeration for list values.

    This class ensures that the provided value is of type list or tuple.

    Args:
        iterable (Any): An iterable (list or tuple) to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not of type list or tuple.
    """


class TupleEnum:
    """Enumeration for tuple values.

    This class ensures that the provided value is of type list or tuple.

    Args:
        iterable (Any): An iterable (list or tuple) to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not of type list or tuple.
    """


class IterableEnum:
    """Enumeration for iterable objects.

    This class ensures that the value is an iterable.

    Args:
        value (Iterable): The iterable value to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not iterable.
    """


class IteratorEnum:
    """Enumeration for iterator objects.

    This class ensures that the value is an iterator.

    Args:
        value (Iterator): The iterator value to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not an iterator.
    """


class GeneratorEnum:
    """Enumeration for generator objects.

    This class ensures that the value is a generator.

    Args:
        value (Generator): The generator value to be validated and stored.

    Raises:
        EnumTypeError: If the provided value is not a generator.
    """