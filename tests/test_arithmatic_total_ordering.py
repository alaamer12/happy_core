import pytest

from true.toolkits import arithmatic_total_ordering, FixIDEComplain


@arithmatic_total_ordering
class MyClass(FixIDEComplain):
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.value == other.value

    def __add__(self, other):
        if not isinstance(other, MyClass):
            return NotImplemented
        return MyClass(self.value + other.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"MyClass({self.value})"


@pytest.fixture
def obj1():
    return MyClass(10)


@pytest.fixture
def obj2():
    return MyClass(20)


@pytest.fixture
def obj3():
    return MyClass(0)


@pytest.fixture
def obj4():
    return MyClass(-5)


# Arithmetic Operation Tests
def test_addition(obj1, obj2):
    assert obj1 + obj2 == MyClass(30)


def test_subtraction(obj1, obj2):
    assert obj1 - obj2 == -10


def test_multiplication(obj1, obj2):
    assert obj1 * obj2 == 200


def test_true_division(obj1, obj2):
    assert obj1 / obj2 == 0.5


def test_floor_division(obj1, obj2):
    assert obj1 // obj2 == 0


def test_modulo(obj1, obj2):
    assert obj1 % obj2 == 10


def test_power(obj1, obj2):
    assert obj1 ** MyClass(2) == 100


# Comparison Operation Tests
def test_equality(obj1):
    assert obj1 == MyClass(10)


def test_inequality(obj1, obj2):
    assert obj1 != obj2


def test_less_than(obj1, obj2):
    assert obj1 < obj2


def test_greater_than(obj1, obj2):
    assert obj2 > obj1


# Edge Case Tests
def test_zero_division(obj1, obj3):
    with pytest.raises(ZeroDivisionError):
        _ = obj1.value / obj3.value
    with pytest.raises(ZeroDivisionError):
        _ = obj1.value // obj3.value


def test_operations_with_incompatible_types(obj1):
    with pytest.raises(TypeError):
        assert (obj1 + "string") == NotImplemented
        assert (obj1 - "string") == NotImplemented
        assert (obj1 * "string") == NotImplemented
        assert (obj1 / "string") == NotImplemented


# Reverse Operation Tests
# def test_reverse_addition(obj1):
#     expected = MyClass(30)
#     found = obj1 + 10
#     assert found == expected
#
# def test_reverse_subtraction(obj1):
#     assert 15 - obj1 == MyClass(5)
#
# def test_reverse_multiplication(obj1):
#     assert 5 * obj1 == MyClass(50)
#
# def test_reverse_division(obj2):
#     assert 200 / obj2 == MyClass(10)

# String Representation Tests
def test_string_representation(obj1):
    assert str(obj1) == "10"
    assert repr(obj1) == "MyClass(10)"


# Test for dynamic method generation
def test_dynamic_methods(obj1, obj2):
    # Ensure that the FixIDEComplain dynamically generates missing methods
    assert hasattr(obj1, '__add__')
    assert hasattr(obj1, '__sub__')
    assert hasattr(obj1, '__mul__')
    assert hasattr(obj1, '__truediv__')
    assert hasattr(obj1, '__floordiv__')
    assert hasattr(obj1, '__mod__')
    assert hasattr(obj1, '__pow__')


# Special Cases
def test_self_modifying_operations(obj1, obj2):
    result = obj1
    result += obj2
    assert result == MyClass(30)


def test_in_place_operations(obj1, obj2):
    obj1 *= obj2
    assert obj1 == (200)
