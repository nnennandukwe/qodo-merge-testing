"""
Tests for calculator module with intentional gaps in coverage

INTENTIONAL ISSUES:
- Incomplete test coverage
- Missing edge case tests
- No security testing
- Poor test organization
- Missing error case testing
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import Calculator, quick_divide, batch_calculate

class TestCalculator:
    def setup_method(self):
        self.calc = Calculator()
    
    # INTENTIONAL ISSUE: Only testing happy path
    def test_divide_basic(self):
        result = self.calc.divide(10, 2)
        assert result == 5.0
    
    # INTENTIONAL ISSUE: Not testing division by zero
    # def test_divide_by_zero(self):
    #     with pytest.raises(ZeroDivisionError):
    #         self.calc.divide(10, 0)
    
    # INTENTIONAL ISSUE: Only testing small fibonacci numbers
    def test_fibonacci_small(self):
        assert self.calc.fibonacci(0) == 0
        assert self.calc.fibonacci(1) == 1
        assert self.calc.fibonacci(5) == 5
    
    # INTENTIONAL ISSUE: Not testing large numbers that would expose performance issues
    # def test_fibonacci_large(self):
    #     # This would be too slow with current implementation
    #     pass
    
    # INTENTIONAL ISSUE: Testing eval without considering security implications
    def test_calculate_expression_basic(self):
        result = self.calc.calculate_expression("2 + 3")
        assert result == 5
    
    # INTENTIONAL ISSUE: Not testing malicious input
    # def test_calculate_expression_security(self):
    #     # Should test for code injection attempts
    #     pass
    
    # INTENTIONAL ISSUE: Only testing positive numbers
    def test_power_positive(self):
        assert self.calc.power(2, 3) == 8
    
    # INTENTIONAL ISSUE: Not testing edge cases like large exponents
    # def test_power_large_exponent(self):
    #     # Should test memory/time limits
    #     pass
    
    # INTENTIONAL ISSUE: Incomplete prime testing
    def test_is_prime_basic(self):
        assert self.calc.is_prime(2) == True
        assert self.calc.is_prime(4) == False
    
    # INTENTIONAL ISSUE: Not testing performance for large numbers
    # def test_is_prime_large_numbers(self):
    #     # Current implementation is O(n), should be tested
    #     pass
    
    # INTENTIONAL ISSUE: Not testing memory leak in history
    def test_history_basic(self):
        self.calc.divide(10, 2)
        history = self.calc.get_calculation_history()
        assert len(history) == 1
    
    # INTENTIONAL ISSUE: Not testing sqrt edge cases
    def test_sqrt_positive(self):
        assert self.calc.sqrt(4) == 2.0
    
    # INTENTIONAL ISSUE: Not testing negative numbers
    # def test_sqrt_negative(self):
    #     with pytest.raises(ValueError):
    #         self.calc.sqrt(-1)

# INTENTIONAL ISSUE: Minimal testing of utility functions
class TestUtilityFunctions:
    def test_quick_divide_basic(self):
        assert quick_divide(10, 2) == 5.0
    
    # INTENTIONAL ISSUE: Not testing error conditions
    
    def test_batch_calculate_basic(self):
        expressions = ["2 + 2", "3 * 3"]
        results = batch_calculate(expressions)
        assert results == [4, 9]
    
    # INTENTIONAL ISSUE: Not testing security issues with eval

# INTENTIONAL ISSUE: No integration tests
# INTENTIONAL ISSUE: No performance tests
# INTENTIONAL ISSUE: No security tests
# INTENTIONAL ISSUE: No test for global state issues