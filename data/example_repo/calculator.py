"""
A simple calculator module with basic arithmetic operations.
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base, exponent):
    """Raise base to the power of exponent."""
    return base ** exponent


def square_root(n):
    """Calculate the square root of a number.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Cannot calculate square root of negative number")
    if n == 0:
        return 0
    return n ** 0.5


class Calculator:
    """A calculator class that maintains state."""

    def __init__(self):
        self._history = []

    def add(self, a, b):
        """Add two numbers and record in history."""
        result = a + b
        self._history.append(f"add({a}, {b}) = {result}")
        return result

    def subtract(self, a, b):
        """Subtract two numbers and record in history."""
        result = a - b
        self._history.append(f"subtract({a}, {b}) = {result}")
        return result

    def multiply(self, a, b):
        """Multiply two numbers and record in history."""
        result = a * b
        self._history.append(f"multiply({a}, {b}) = {result}")
        return result

    def divide(self, a, b):
        """Divide two numbers and record in history.

        Raises:
            ValueError: If b is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._history.append(f"divide({a}, {b}) = {result}")
        return result

    def get_history(self):
        """Return the calculation history."""
        return self._history.copy()

    def clear_history(self):
        """Clear the calculation history."""
        self._history.clear()
