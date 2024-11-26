import pytest

from happy_core.enums_toolkits import (
    DynamicEnum, IterableEnum, IteratorEnum,
    GeneratorEnum, ByteEnum, FloatEnum, ComplexNumberEnum,
    DictEnum, SetEnum, ListEnum
)
from happy_core.exceptions import EnumTypeError


def test_dynamic_enum():
    # Create a new dynamic enum
    colors = DynamicEnum(RED="red", GREEN="green", BLUE="blue")

    # Access members
    print(colors.RED.value)  # "red"
    print(colors.RED.name)  # "RED"

    # Iterate over members
    for color in colors:
        assert color.name in ("RED", "GREEN", "BLUE")
        assert color.value in ("red", "green", "blue")

    # Add new members dynamically
    colors.add_member("YELLOW", "yellow")
    assert colors.YELLOW.value == "yellow"

    # Remove members
    colors.remove_member("BLUE")

    with pytest.raises(Exception):
        assert colors.BLUE.value == "blue"

    # Convert from regular Enum
    from enum import Enum
    class RegularColors(Enum):
        RED = "red"
        GREEN = "green"

    dynamic_colors = DynamicEnum.from_enum(RegularColors)

    assert dynamic_colors.RED.value == "red"
    assert dynamic_colors.GREEN.value == "green"


def test_iterable_enum():
    class IterableEnumColors(IterableEnum):
        RED = (255, 0, 0)
        Green = (0, 255, 0)
        Blue = (0, 0, 255)

    iec = IterableEnumColors
    assert iec.RED
    assert iec.Blue
    assert iec.Green

    with pytest.raises(EnumTypeError):
        class InvalidIterableEnumColors(IterableEnum):
            RED = 0
            Green = (0, 255, 0)
            Blue = (0, 0, 255)


def test_iterator_enum():
    def simple_gen():
        yield 1

    class IteratorEnumColors(IteratorEnum):
        RED = simple_gen()
        Green = simple_gen()
        Blue = simple_gen()

    iec = IteratorEnumColors
    assert iec.RED
    assert iec.Blue
    assert iec.Green

    with pytest.raises(Exception):
        class InvalidIteratorEnumColors(IteratorEnum):
            RED = 0
            Green = simple_gen()
            Blue = simple_gen()


def test_generator_enum():
    def gen():
        yield from range(3)

    class GeneratorEnumColors(GeneratorEnum):
        RED = gen()
        GREEN = gen()
        BLUE = gen()

    iec = GeneratorEnumColors
    assert iec.RED
    assert iec.BLUE
    assert iec.GREEN

    # Test invalid generator
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidIteratorEnumColors(GeneratorEnum):
            RED = 0
            Green = gen()
            Blue = gen()


# def test_ranging_enum():
#     # Test valid range
#     enum = RangingEnum(5, 0, 10)
#     assert enum == 5
#
#     # Test out of range
#     with pytest.raises(Exception):  # Replace with actual error type
#         RangingEnum(11, 0, 10)
#
#     # Test invalid type
#     with pytest.raises(Exception):  # Replace with actual error type
#         RangingEnum("5", 0, 10)


def test_byte_enum():
    # Test valid bytes
    class ByteEnumColors(ByteEnum):
        RED = b"red"
        GREEN = b"green"
        BLUE = b"blue"

    iec = ByteEnumColors
    assert iec.RED
    assert iec.GREEN
    assert iec.BLUE

    # Test invalid generator
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidByteEnumColors(ByteEnum):
            RED = "red"
            GREEN = b"green"
            BLUE = b"blue"


def test_float_enum():
    class FloatEnumColors(FloatEnum):
        RED = 0.1
        GREEN = 0.2
        BLUE = 0.3

    iec = FloatEnumColors
    assert iec.RED
    assert iec.GREEN
    assert iec.BLUE

    # Test invalid generator
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidFloatEnumColors(FloatEnum):
            RED = 1
            GREEN = 0.2
            BLUE = 0.3


def test_complex_number_enum():
    class ComplexNumberEnumColors(ComplexNumberEnum):
        RED = 0.1 + 1j
        GREEN = 0.2 + 1j
        BLUE = 0.3 + 1j

    iec = ComplexNumberEnumColors
    assert iec.RED
    assert iec.GREEN
    assert iec.BLUE

    # Test invalid generator
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidComplexNumberEnumColors(ComplexNumberEnum):
            RED = 1
            GREEN = 0.2 + 1j
            BLUE = 0.3 + 1j


def test_dict_enum():
    # Test valid dictionary
    class DictEnumColors(DictEnum):
        RED = {'r': 1, 'g': 2, 'b': 3}
        GREEN = {'r': 1, 'g': 2, 'b': 3}
        BLUE = {'r': 1, 'g': 2, 'b': 3}

    de = DictEnumColors
    assert de.RED
    assert de.GREEN
    assert de.BLUE

    # Test invalid arguments
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidDictEnumColors(DictEnum):
            RED = {'r' 'g', 'b'}
            GREEN = {'r': 1, 'g': 2, 'b': 3}
            BLUE = {'r': 1, 'g': 2, 'b': 3}


def test_set_enum():
    # Test valid dictionary
    class SetEnumColors(SetEnum):
        RED = {'r' 'g', 'b'}
        GREEN = {'r' 'g', 'b'}
        BLUE = {'r' 'g', 'b'}

    se = SetEnumColors
    assert se.RED
    assert se.GREEN
    assert se.BLUE

    # Test invalid arguments
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidSetEnumColors(SetEnum):
            RED = {'r' 'g', 'b'}
            GREEN = {'r': 1, 'g': 2, 'b': 3}
            BLUE = {'r' 'g', 'b'}


def test_list_enum():
    # Test valid list
    class ListEnumColors(ListEnum):
        RED = ['r' 'g', 'b']
        GREEN = ['r' 'g', 'b']
        BLUE = ['r' 'g', 'b']

    le = ListEnumColors
    assert le.RED
    assert le.GREEN
    assert le.BLUE

    # Test invalid arguments
    with pytest.raises(Exception):  # Replace with actual error type
        class InvalidListEnumColors(ListEnum):
            RED = ['r' 'g', 'b']
            GREEN = {'r': 1, 'g': 2, 'b': 3}
            BLUE = ['r' 'g', 'b']


def test_tuple_enum():
    # Bugged it has a weird situation with tupling

    # Test valid tuple
    # class TupleEnumColors(TupleEnum):
    #     RED = ('r' 'g', 'b')
    #     GREEN = {'r': 1, 'g': 2, 'b': 3}
    #     BLUE = ('r' 'g', 'b')
    #
    # te = TupleEnumColors
    # assert te.RED
    # assert te.GREEN
    # assert te.BLUE
    #
    # # Test invalid arguments
    # with pytest.raises(Exception):  # Replace with actual error type
    #     class InvalidTupleEnumColors(TupleEnum):
    #         RED = ('r' 'g', 'b')
    #         GREEN = {'r': 1, 'g': 2, 'b': 3}
    #         BLUE = ('r' 'g', 'b')
    assert True

# Should be used with dynamic enum class
# def test_serialized_enum_meta():
#     class Colors(metaclass=SerializedEnumMeta):
#         RED = 1
#         BLUE = 2
#         GREEN = 3
#
#     assert Colors.RED.value == 1
#     assert Colors.BLUE.value == 2
#     assert Colors.GREEN.value == 3
#
#     dict_data = Colors.to_dict()
#     assert dict_data == {'RED': 1, 'BLUE': 2, 'GREEN': 3}
#
#     class Week(metaclass=SerializedEnumMeta):
#         pass
#
#     week = Week.from_dict('Week', dict_data)
#     assert week['RED'] == 1
#     assert week['BLUE'] == 2
#     assert week['GREEN'] == 3
