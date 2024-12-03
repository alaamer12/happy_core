import asyncio
from typing import ClassVar

import pytest
import pytest_asyncio

from true.exceptions import UnificationError
from true.toolkits import (create_unified_operation, UnifiedOperation,
                                 DynamicUnifiedOperation)


def custom_sync_op(x: float, y: float) -> float:
    return x ** y


async def custom_async_op(x: float, y: float) -> float:
    await asyncio.sleep(0.1)
    return x ** y


# noinspection DuplicatedCode
class Calculator(DynamicUnifiedOperation):
    @staticmethod
    def _sync_add(x: int, y: int) -> int:
        return x + y

    @staticmethod
    async def _async_add(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        return x + y

    # Define the unified operation
    add: ClassVar[UnifiedOperation[..., int]] = UnifiedOperation(_sync_add, _async_add)

    @staticmethod
    def _sync_multiply(x: int, y: int) -> int:
        return x * y

    @staticmethod
    async def _async_multiply(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        return x * y

    # Define another unified operation
    multiply: ClassVar[UnifiedOperation[..., int]] = UnifiedOperation(_sync_multiply, _async_multiply)


class InvalidCalculator:
    """Example implementation using the UnifiedOperation pattern"""

    @staticmethod
    def _sync_add(x: int, y: int) -> int:
        return x + y

    @staticmethod
    async def _async_add(x: int, y: int) -> int:
        await asyncio.sleep(0.1)
        return x + y

    # Define the unified operation
    add: ClassVar[UnifiedOperation[..., int]] = UnifiedOperation(_sync_add, _async_add)


@pytest.fixture
def calculator():
    return Calculator()


@pytest_asyncio.fixture
def async_invalid_calculator():
    return InvalidCalculator()


# Test synchronous operations
def test_sync_addition(calculator):
    result = calculator.add(3, 4)
    assert result == 7, f"Expected 7, but got {result}"


def test_sync_multiplication(calculator):
    result = calculator.multiply(3, 4)
    assert result == 12, f"Expected 12, but got {result}"


# Test asynchronous operations
@pytest.mark.asyncio
async def test_async_addition(calculator):
    result = await calculator.add(3, 4)
    assert result == 7, f"Expected 7, but got {result}"


@pytest.mark.asyncio
async def test_async_multiplication(calculator):
    result = await calculator.multiply(3, 4)
    assert result == 12, f"Expected 12, but got {result}"


# Test custom operations created dynamically
@pytest.mark.asyncio
async def test_custom_async_operation(calculator):
    calc = calculator

    # Test power operation
    calc.power = create_unified_operation(custom_sync_op, custom_async_op)
    result = await calc.power(2, 3)
    assert result == 8, f"Expected 8, but got {result}"


def test_custom_sync_operation(calculator):
    calc = calculator

    # Test power operation
    calc.power = create_unified_operation(custom_sync_op, custom_async_op)
    result = calc.power(2, 3)
    assert result == 8, f"Expected 8, but got {result}"


# Test UnificationError for unsupported dynamic methods
async def test_dynamic_unification_error(async_invalid_calculator):
    calc = async_invalid_calculator

    # Check if calling __call__ or __await__ raises an error
    with pytest.raises(UnificationError):
        calc.power = create_unified_operation(custom_sync_op, custom_async_op)
        _ = calc.power(2, 3)

    with pytest.raises(UnificationError):
        calc.power = create_unified_operation(custom_sync_op, custom_async_op)
        _ = await calc.power(2, 3)


# Test attribute error for missing operations
def test_missing_operation():
    calc = Calculator()

    # Test if accessing an undefined operation raises AttributeError
    with pytest.raises(AttributeError):
        _ = calc.non_existent_operation
