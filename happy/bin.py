def str_to_bits(string: str) -> str:
    return "".join([bin(ord(char))[2:].zfill(8) for char in string])


def bits_to_str(bits: str) -> str:
    return "".join([chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)])


def into_to_bits(into: int) -> str:
    return str(bin(into))[2:].zfill(32)


def bits_to_into(bits: str) -> int:
    return int(bits, 2)


def bits_to_hex(bits: str) -> str:
    return str(hex(int(bits, 2)))[2:]


def hex_to_bits(hex_str: str) -> str:
    return str(bin(int(hex_str, 16)))[2:].zfill(32)
