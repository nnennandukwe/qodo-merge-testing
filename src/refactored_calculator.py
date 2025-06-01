"""
Refactored calculator module with improved code quality.

This module demonstrates:
- Clear naming conventions and documentation
- Separation of concerns with different calculator types
- Proper error handling and input validation
- Optimized algorithms and memory management
- Type hints and comprehensive testing support
"""

import math
import logging
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from .common.error_handling import ValidationError, BusinessLogicError, default_error_handler
from .common.security_utils import default_sanitizer


class CalculationError(Exception):
    """Raised when calculation operations fail."""
    pass


class OperationType(Enum):
    """Types of mathematical operations."""
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    POWER = "power"
    SQUARE_ROOT = "square_root"
    FACTORIAL = "factorial"
    FIBONACCI = "fibonacci"
    PRIME_CHECK = "prime_check"
    EXPRESSION = "expression"


@dataclass
class CalculationResult:
    """Result of a mathematical calculation."""
    operation: OperationType
    operands: List[Union[int, float]]
    result: Union[int, float, bool]
    timestamp: float
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        return {
            'operation': self.operation.value,
            'operands': self.operands,
            'result': self.result,
            'timestamp': self.timestamp,
            'error': self.error
        }


class CalculationHistory:
    """Manages calculation history with size limits."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._history: List[CalculationResult] = []
        self.logger = logging.getLogger(__name__)
    
    def add_calculation(self, result: CalculationResult) -> None:
        """Add a calculation result to history."""
        self._history.append(result)
        
        # Maintain size limit to prevent memory leaks
        if len(self._history) > self.max_size:
            self._history = self._history[-self.max_size:]
    
    def get_history(self, limit: Optional[int] = None) -> List[CalculationResult]:
        """Get calculation history with optional limit."""
        if limit is None:
            return self._history.copy()
        return self._history[-limit:] if limit > 0 else []
    
    def clear_history(self) -> None:
        """Clear all calculation history."""
        self._history.clear()
        self.logger.info("Calculation history cleared")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about calculation history."""
        operation_counts = {}
        for result in self._history:
            op_type = result.operation.value
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
        
        return {
            'total_calculations': len(self._history),
            'operation_counts': operation_counts,
            'error_count': sum(1 for r in self._history if r.error is not None)
        }


class InputValidator:
    """Validates inputs for mathematical operations."""
    
    @staticmethod
    def validate_number(value: Union[int, float], 
                       min_value: Optional[float] = None,
                       max_value: Optional[float] = None,
                       allow_negative: bool = True) -> float:
        """
        Validate and convert input to a number.
        
        Args:
            value: Input value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative numbers are allowed
            
        Returns:
            Validated number
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(value, str):
                # Sanitize string input
                value = default_sanitizer.sanitize_html_input(value)
                num_value = float(value)
            elif isinstance(value, (int, float)):
                num_value = float(value)
            else:
                raise ValidationError(f"Invalid number type: {type(value)}")
            
            # Check for infinity and NaN
            if math.isinf(num_value):
                raise ValidationError("Infinite values are not allowed")
            if math.isnan(num_value):
                raise ValidationError("NaN values are not allowed")
            
            # Check sign constraint
            if not allow_negative and num_value < 0:
                raise ValidationError("Negative values are not allowed for this operation")
            
            # Check range constraints
            if min_value is not None and num_value < min_value:
                raise ValidationError(f"Value must be at least {min_value}")
            if max_value is not None and num_value > max_value:
                raise ValidationError(f"Value must be at most {max_value}")
            
            return num_value
            
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid number format: {str(e)}")
    
    @staticmethod
    def validate_integer(value: Union[int, float, str],
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None) -> int:
        """
        Validate and convert input to an integer.
        
        Args:
            value: Input value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        num_value = InputValidator.validate_number(value, min_value, max_value)
        
        if not isinstance(value, int) and not num_value.is_integer():
            raise ValidationError("Value must be an integer")
        
        int_value = int(num_value)
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_expression(expression: str) -> str:
        """
        Validate a mathematical expression for safety.
        
        Args:
            expression: Mathematical expression to validate
            
        Returns:
            Sanitized expression
            
        Raises:
            ValidationError: If expression is invalid or unsafe
        """
        if not isinstance(expression, str):
            raise ValidationError("Expression must be a string")
        
        # Sanitize input
        sanitized = default_sanitizer.sanitize_html_input(expression.strip())
        
        if not sanitized:
            raise ValidationError("Expression cannot be empty")
        
        if len(sanitized) > 1000:
            raise ValidationError("Expression is too long (max 1000 characters)")
        
        # Check for allowed characters only
        import re
        allowed_pattern = re.compile(r'^[0-9+\-*/().%\s]+$')
        if not allowed_pattern.match(sanitized):
            raise ValidationError("Expression contains invalid characters")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'import', 'exec', 'eval', '__', 'getattr', 'setattr',
            'delattr', 'hasattr', 'globals', 'locals', 'dir',
            'open', 'file', 'input', 'raw_input'
        ]
        
        sanitized_lower = sanitized.lower()
        for pattern in dangerous_patterns:
            if pattern in sanitized_lower:
                raise ValidationError(f"Expression contains forbidden pattern: {pattern}")
        
        return sanitized


class BasicCalculator:
    """Handles basic arithmetic operations."""
    
    def __init__(self):
        self.validator = InputValidator()
        self.logger = logging.getLogger(__name__)
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Add two numbers."""
        try:
            num_a = self.validator.validate_number(a)
            num_b = self.validator.validate_number(b)
            
            result = num_a + num_b
            
            # Check for overflow
            if math.isinf(result):
                raise CalculationError("Addition result is too large")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Addition failed: {str(e)}")
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Subtract two numbers."""
        try:
            num_a = self.validator.validate_number(a)
            num_b = self.validator.validate_number(b)
            
            result = num_a - num_b
            
            if math.isinf(result):
                raise CalculationError("Subtraction result is too large")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Subtraction failed: {str(e)}")
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Multiply two numbers."""
        try:
            num_a = self.validator.validate_number(a)
            num_b = self.validator.validate_number(b)
            
            result = num_a * num_b
            
            if math.isinf(result):
                raise CalculationError("Multiplication result is too large")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Multiplication failed: {str(e)}")
    
    def divide(self, dividend: Union[int, float], divisor: Union[int, float]) -> float:
        """
        Divide two numbers with proper error handling.
        
        Args:
            dividend: Number to be divided
            divisor: Number to divide by
            
        Returns:
            Division result
            
        Raises:
            ValidationError: If inputs are invalid
            CalculationError: If division fails
        """
        try:
            num_dividend = self.validator.validate_number(dividend)
            num_divisor = self.validator.validate_number(divisor)
            
            if num_divisor == 0:
                raise CalculationError("Cannot divide by zero")
            
            result = num_dividend / num_divisor
            
            if math.isinf(result):
                raise CalculationError("Division result is infinite")
            if math.isnan(result):
                raise CalculationError("Division result is not a number")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Division failed: {str(e)}")
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """
        Calculate base raised to the power of exponent.
        
        Args:
            base: Base number
            exponent: Exponent value
            
        Returns:
            Power calculation result
            
        Raises:
            ValidationError: If inputs are invalid
            CalculationError: If calculation fails
        """
        try:
            num_base = self.validator.validate_number(base, max_value=10000)
            num_exponent = self.validator.validate_number(exponent, min_value=-1000, max_value=1000)
            
            # Additional safety checks
            if abs(num_base) > 100 and abs(num_exponent) > 10:
                raise CalculationError("Result would be too large")
            
            result = num_base ** num_exponent
            
            if math.isinf(result):
                raise CalculationError("Power result is infinite")
            if math.isnan(result):
                raise CalculationError("Power result is not a number")
            
            return result
            
        except ValidationError:
            raise
        except (OverflowError, ZeroDivisionError) as e:
            raise CalculationError(f"Power calculation failed: {str(e)}")
        except Exception as e:
            raise CalculationError(f"Power calculation error: {str(e)}")
    
    def square_root(self, number: Union[int, float]) -> float:
        """
        Calculate square root of a number.
        
        Args:
            number: Number to calculate square root of
            
        Returns:
            Square root result
            
        Raises:
            ValidationError: If input is invalid
            CalculationError: If calculation fails
        """
        try:
            num_value = self.validator.validate_number(number, min_value=0, allow_negative=False)
            
            result = math.sqrt(num_value)
            
            if math.isinf(result) or math.isnan(result):
                raise CalculationError("Square root result is invalid")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Square root calculation failed: {str(e)}")


class AdvancedCalculator:
    """Handles advanced mathematical operations."""
    
    def __init__(self):
        self.validator = InputValidator()
        self.logger = logging.getLogger(__name__)
        # Memoization cache for fibonacci
        self._fibonacci_cache: Dict[int, int] = {0: 0, 1: 1}
    
    def factorial(self, n: Union[int, float]) -> int:
        """
        Calculate factorial of a number.
        
        Args:
            n: Number to calculate factorial of
            
        Returns:
            Factorial result
            
        Raises:
            ValidationError: If input is invalid
            CalculationError: If calculation fails
        """
        try:
            int_n = self.validator.validate_integer(n, min_value=0, max_value=170)
            
            if int_n == 0 or int_n == 1:
                return 1
            
            result = 1
            for i in range(2, int_n + 1):
                result *= i
                
                # Safety check for extremely large results
                if result > 10**308:  # Close to float limit
                    raise CalculationError("Factorial result is too large")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Factorial calculation failed: {str(e)}")
    
    def fibonacci(self, n: Union[int, float]) -> int:
        """
        Calculate nth Fibonacci number using memoization.
        
        Args:
            n: Position in Fibonacci sequence
            
        Returns:
            Fibonacci number at position n
            
        Raises:
            ValidationError: If input is invalid
            CalculationError: If calculation fails
        """
        try:
            int_n = self.validator.validate_integer(n, min_value=0, max_value=1000)
            
            return self._fibonacci_memoized(int_n)
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Fibonacci calculation failed: {str(e)}")
    
    def _fibonacci_memoized(self, n: int) -> int:
        """Internal memoized Fibonacci calculation."""
        if n in self._fibonacci_cache:
            return self._fibonacci_cache[n]
        
        # Calculate iteratively to avoid stack overflow
        a, b = 0, 1
        for i in range(2, n + 1):
            if i not in self._fibonacci_cache:
                self._fibonacci_cache[i] = a + b
            a, b = b, self._fibonacci_cache[i]
        
        return self._fibonacci_cache[n]
    
    def is_prime(self, n: Union[int, float]) -> bool:
        """
        Check if a number is prime using optimized algorithm.
        
        Args:
            n: Number to check for primality
            
        Returns:
            True if number is prime, False otherwise
            
        Raises:
            ValidationError: If input is invalid
            CalculationError: If calculation fails
        """
        try:
            int_n = self.validator.validate_integer(n, min_value=0, max_value=10**9)
            
            if int_n < 2:
                return False
            if int_n == 2:
                return True
            if int_n % 2 == 0:
                return False
            
            # Check odd divisors up to sqrt(n)
            sqrt_n = int(math.sqrt(int_n)) + 1
            for i in range(3, sqrt_n, 2):
                if int_n % i == 0:
                    return False
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Prime check failed: {str(e)}")


class ExpressionCalculator:
    """Safely evaluates mathematical expressions."""
    
    def __init__(self):
        self.validator = InputValidator()
        self.basic_calc = BasicCalculator()
        self.logger = logging.getLogger(__name__)
        
        # Safe namespace for evaluation
        self.safe_namespace = {
            '__builtins__': {},
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'pi': math.pi,
            'e': math.e
        }
    
    def evaluate_expression(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Evaluation result
            
        Raises:
            ValidationError: If expression is invalid
            CalculationError: If evaluation fails
        """
        try:
            sanitized_expr = self.validator.validate_expression(expression)
            
            # Use AST parsing for additional safety
            import ast
            
            try:
                # Parse the expression into an AST
                parsed = ast.parse(sanitized_expr, mode='eval')
                
                # Validate the AST contains only safe nodes
                self._validate_ast_nodes(parsed)
                
                # Evaluate with restricted namespace
                result = eval(compile(parsed, '<string>', 'eval'), self.safe_namespace, {})
                
                if not isinstance(result, (int, float)):
                    raise CalculationError(f"Expression result is not a number: {type(result)}")
                
                if math.isinf(result):
                    raise CalculationError("Expression result is infinite")
                if math.isnan(result):
                    raise CalculationError("Expression result is not a number")
                
                return float(result)
                
            except SyntaxError as e:
                raise ValidationError(f"Invalid expression syntax: {str(e)}")
            except (NameError, TypeError) as e:
                raise ValidationError(f"Expression contains invalid operations: {str(e)}")
            
        except ValidationError:
            raise
        except Exception as e:
            raise CalculationError(f"Expression evaluation failed: {str(e)}")
    
    def _validate_ast_nodes(self, node: ast.AST) -> None:
        """Validate that AST contains only safe node types."""
        allowed_nodes = (
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare,
            ast.Num, ast.Constant, ast.Name, ast.Load,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
            ast.USub, ast.UAdd,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
            ast.Call
        )
        
        for child in ast.walk(node):
            if not isinstance(child, allowed_nodes):
                raise ValidationError(f"Unsafe expression: contains {type(child).__name__}")
            
            # Additional checks for function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id not in self.safe_namespace:
                        raise ValidationError(f"Unsafe function: {child.func.id}")


class ComprehensiveCalculator:
    """Main calculator class that combines all calculation capabilities."""
    
    def __init__(self, history_size: int = 1000):
        self.basic_calc = BasicCalculator()
        self.advanced_calc = AdvancedCalculator()
        self.expression_calc = ExpressionCalculator()
        self.history = CalculationHistory(history_size)
        self.logger = logging.getLogger(__name__)
    
    def _record_calculation(self, operation: OperationType, operands: List[Union[int, float]], 
                          result: Union[int, float, bool], error: Optional[str] = None) -> CalculationResult:
        """Record a calculation in history."""
        import time
        
        calc_result = CalculationResult(
            operation=operation,
            operands=operands,
            result=result,
            timestamp=time.time(),
            error=error
        )
        
        self.history.add_calculation(calc_result)
        return calc_result
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """Add two numbers and record the result."""
        try:
            result = self.basic_calc.add(a, b)
            return self._record_calculation(OperationType.ADDITION, [a, b], result)
        except Exception as e:
            return self._record_calculation(OperationType.ADDITION, [a, b], 0, str(e))
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """Subtract two numbers and record the result."""
        try:
            result = self.basic_calc.subtract(a, b)
            return self._record_calculation(OperationType.SUBTRACTION, [a, b], result)
        except Exception as e:
            return self._record_calculation(OperationType.SUBTRACTION, [a, b], 0, str(e))
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """Multiply two numbers and record the result."""
        try:
            result = self.basic_calc.multiply(a, b)
            return self._record_calculation(OperationType.MULTIPLICATION, [a, b], result)
        except Exception as e:
            return self._record_calculation(OperationType.MULTIPLICATION, [a, b], 0, str(e))
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """Divide two numbers and record the result."""
        try:
            result = self.basic_calc.divide(a, b)
            return self._record_calculation(OperationType.DIVISION, [a, b], result)
        except Exception as e:
            return self._record_calculation(OperationType.DIVISION, [a, b], 0, str(e))
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> CalculationResult:
        """Calculate power and record the result."""
        try:
            result = self.basic_calc.power(base, exponent)
            return self._record_calculation(OperationType.POWER, [base, exponent], result)
        except Exception as e:
            return self._record_calculation(OperationType.POWER, [base, exponent], 0, str(e))
    
    def square_root(self, number: Union[int, float]) -> CalculationResult:
        """Calculate square root and record the result."""
        try:
            result = self.basic_calc.square_root(number)
            return self._record_calculation(OperationType.SQUARE_ROOT, [number], result)
        except Exception as e:
            return self._record_calculation(OperationType.SQUARE_ROOT, [number], 0, str(e))
    
    def factorial(self, n: Union[int, float]) -> CalculationResult:
        """Calculate factorial and record the result."""
        try:
            result = self.advanced_calc.factorial(n)
            return self._record_calculation(OperationType.FACTORIAL, [n], result)
        except Exception as e:
            return self._record_calculation(OperationType.FACTORIAL, [n], 0, str(e))
    
    def fibonacci(self, n: Union[int, float]) -> CalculationResult:
        """Calculate Fibonacci number and record the result."""
        try:
            result = self.advanced_calc.fibonacci(n)
            return self._record_calculation(OperationType.FIBONACCI, [n], result)
        except Exception as e:
            return self._record_calculation(OperationType.FIBONACCI, [n], 0, str(e))
    
    def is_prime(self, n: Union[int, float]) -> CalculationResult:
        """Check if number is prime and record the result."""
        try:
            result = self.advanced_calc.is_prime(n)
            return self._record_calculation(OperationType.PRIME_CHECK, [n], result)
        except Exception as e:
            return self._record_calculation(OperationType.PRIME_CHECK, [n], False, str(e))
    
    def evaluate_expression(self, expression: str) -> CalculationResult:
        """Evaluate expression and record the result."""
        try:
            result = self.expression_calc.evaluate_expression(expression)
            return self._record_calculation(OperationType.EXPRESSION, [expression], result)
        except Exception as e:
            return self._record_calculation(OperationType.EXPRESSION, [expression], 0, str(e))
    
    def get_calculation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get calculation history in dictionary format."""
        history = self.history.get_history(limit)
        return [calc.to_dict() for calc in history]
    
    def get_statistics(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """Get calculation statistics."""
        return self.history.get_statistics()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear_history()


# Factory function for creating calculator instances
def create_calculator(history_size: int = 1000) -> ComprehensiveCalculator:
    """
    Factory function to create a new calculator instance.
    
    Args:
        history_size: Maximum number of calculations to keep in history
        
    Returns:
        New ComprehensiveCalculator instance
    """
    return ComprehensiveCalculator(history_size)


# Default calculator instance
default_calculator = create_calculator()