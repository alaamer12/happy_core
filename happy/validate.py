def validate_complex_type(value, expected_type):
    if isinstance(expected_type, type):
        return isinstance(value, expected_type)

    if isinstance(expected_type, list):
        if not isinstance(value, list):
            return False
        if len(expected_type) != 1:
            raise ValueError("Expected type should contain exactly one type.")
        return all(validate_complex_type(v, expected_type[0]) for v in value)

    if isinstance(expected_type, dict):
        if not isinstance(value, dict):
            return False
        if len(expected_type) != 1:
            raise ValueError("Expected type should contain exactly one key-value pair.")
        key_type, value_type = list(expected_type.items())[0]
        return all(validate_complex_type(k, key_type) and validate_complex_type(v, value_type) for k, v in value.items())

    if isinstance(expected_type, set):
        if not isinstance(value, set):
            return False
        if len(expected_type) != 1:
            raise ValueError("Expected type should contain exactly one type.")
        element_type = list(expected_type)[0]
        return all(validate_complex_type(e, element_type) for e in value)

    if isinstance(expected_type, tuple):
        if not isinstance(value, tuple) or len(value) != len(expected_type):
            return False
        return all(validate_complex_type(v, t) for v, t in zip(value, expected_type))

    return isinstance(value, expected_type)

# Examples of complex validation
print(validate_complex_type([{"a": 1}, {"b": 2}], [dict]))                     # True
print(validate_complex_type({"a": {1, 2}, "b": {3, 4}}, {str: set}))          # True
print(validate_complex_type({"a": {1: (2, 3)}}, {str: {int: tuple}}))         # True
print(validate_complex_type({"a": {1: (2, "3")}}, {str: {int: (int, int)}}))  # False
print(validate_complex_type({"a": (1, {2, "3"})}, {str: (int, set)}))         # False
print(validate_complex_type({(1, 2): [{"a": {3, 4}}]}, {(tuple): [dict]}))    # True
