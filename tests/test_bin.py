import pytest

# Assuming the functions are defined in a module named conversion
from happy.bin import str_to_bits, bits_to_str, into_to_bits, bits_to_into, bits_to_hex, hex_to_bits


def test_str_to_bits():
    assert str_to_bits("A") == "01000001"
    assert str_to_bits("Hello") == "0100100001100101011011000110110001101111"
    assert str_to_bits("") == ""


def test_bits_to_str():
    assert bits_to_str("01000001") == "A"
    assert bits_to_str("0100100001100101011011000110110001101111") == "Hello"
    assert bits_to_str("") == ""


def test_into_to_bits():
    assert into_to_bits(1) == "00000000000000000000000000000001"
    assert into_to_bits(255) == "00000000000000000000000011111111"
    assert into_to_bits(1024) == "00000000000000000000010000000000"  # Corrected to 32 bits



def test_bits_to_into():
    assert bits_to_into("00000000000000000000000000000001") == 1
    assert bits_to_into("00000000000000000000000011111111") == 255
    assert bits_to_into("00000000000000000000010000000000") == 1024


def test_bits_to_hex():
    assert bits_to_hex("00000000000000000000000000000001") == "1"
    assert bits_to_hex("00000000000000000000000011111111") == "ff"
    assert bits_to_hex("00000000000000000000010000000000") == "400"


def test_hex_to_bits():
    assert hex_to_bits("1") == "00000000000000000000000000000001"
    assert hex_to_bits("ff") == "00000000000000000000000011111111"
    assert hex_to_bits("400") == "00000000000000000000010000000000"


# Run the tests if this file is executed directly
if __name__ == "__main__":
    pytest.main()
