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
