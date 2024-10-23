from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Callable, Optional, Tuple, Any
import asyncio

# Custom Exceptions
class AsymptoticNotationException(Exception):
    """Base exception for Asymptotic Notation errors."""
    pass

class InvalidAlgorithmException(AsymptoticNotationException):
    """Exception raised when the algorithm provided is invalid."""
    pass

class ConfigurationException(AsymptoticNotationException):
    """Exception raised for any configuration issues."""
    pass

# Abstract Base Class for Calculation Strategy
class AsymptoticStrategy(ABC):
    @abstractmethod
    def calculate(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        """Calculate the Big-O, Big-Theta, and Big-Omega notations."""
        pass

# Concrete Strategies
class TimeComplexityStrategy(AsymptoticStrategy):
    def calculate(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        # Placeholder: Add actual algorithm analysis logic here
        return "O(n)", "Θ(n)", "Ω(n)"

class SpaceComplexityStrategy(AsymptoticStrategy):
    def calculate(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        # Placeholder: Add actual algorithm analysis logic here
        return "O(n)", "Θ(n)", "Ω(n)"

# Asynchronous support class
class AsyncAsymptoticNotation:
    async def calculate_async(self, strategy: AsymptoticStrategy, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        return await asyncio.to_thread(strategy.calculate, algorithm, *args)

# Asymptotic Notation Class with Context Management
class AsymptoticNotation(AbstractContextManager):
    def __init__(self, strategy: AsymptoticStrategy, config: Optional[dict] = None):
        self.strategy = strategy
        self.config = config or {}
        self._validate_config()

    def _validate_config(self):
        """Validate the configuration dictionary."""
        if not isinstance(self.config, dict):
            raise ConfigurationException("Configuration should be a dictionary.")
        # Add more validation rules as needed

    def __enter__(self):
        # Initialization when entering context
        print("Entering AsymptoticNotation context.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Clean-up when exiting context
        print("Exiting AsymptoticNotation context.")

    def calculate(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        """Main method to calculate asymptotic notations."""
        if not callable(algorithm):
            raise InvalidAlgorithmException("Algorithm must be a callable function.")
        return self.strategy.calculate(algorithm, *args)

    # Async support
    async def calculate_async(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        async_notation = AsyncAsymptoticNotation()
        return await async_notation.calculate_async(self.strategy, algorithm, *args)

    # Representation methods
    def __repr__(self) -> str:
        return f"AsymptoticNotation(strategy={self.strategy.__class__.__name__}, config={self.config})"

    def __str__(self) -> str:
        return "AsymptoticNotation class for calculating asymptotic notations (Big-O, Big-Theta, Big-Omega)."

# Example strategies can be extended for more advanced use cases
class AdvancedTimeComplexityStrategy(TimeComplexityStrategy):
    def calculate(self, algorithm: Callable, *args: Any) -> Tuple[str, str, str]:
        # Perform advanced calculation logic here
        return "O(n log n)", "Θ(n log n)", "Ω(n log n)"

# Example usage
if __name__ == "__main__":
    def sample_algorithm(n):
        for i in range(n):
            pass

    # Using basic time complexity strategy
    with AsymptoticNotation(TimeComplexityStrategy()) as notation:
        result = notation.calculate(sample_algorithm, 1000)
        print(result)

    # Using advanced time complexity strategy
    advanced_strategy = AdvancedTimeComplexityStrategy()
    with AsymptoticNotation(advanced_strategy) as notation:
        result = notation.calculate(sample_algorithm, 1000)
        print(result)

    # Using async support
    async def async_test():
        async_notation = AsymptoticNotation(AdvancedTimeComplexityStrategy())
        result = await async_notation.calculate_async(sample_algorithm, 1000)
        print(result)

    asyncio.run(async_test())
