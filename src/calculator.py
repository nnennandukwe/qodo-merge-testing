"""
Calculator module with intentional issues for Qodo Merge testing

INTENTIONAL ISSUES:
- Division by zero vulnerability
- Inefficient recursive fibonacci without memoization
- No input validation
- Poor error handling
- Eval usage (security risk)
"""

import math

class Calculator:
    def __init__(self):
        self.history = []
    
    def divide(self, a, b):
        try:
            # Input validation
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Both arguments must be numbers")
            if b == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            
            result = a / b
            self.history.append(f"{a} / {b} = {result}")
            return result
        except (TypeError, ZeroDivisionError) as e:
            error_msg = f"Division error: {str(e)}"
            self.history.append(f"{a} / {b} = ERROR: {str(e)}")
            raise ValueError(error_msg)
    
    # INTENTIONAL ISSUE: Inefficient recursive fibonacci - O(2^n) complexity
    def fibonacci(self, n):
        if n <= 1:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)
    
    def calculate_expression(self, expression):
        try:
            # Input validation
            if not isinstance(expression, str) or len(expression.strip()) == 0:
                raise ValueError("Expression must be a non-empty string")
            
            # Sanitize expression - only allow basic math operations
            import re
            allowed_chars = re.compile(r'^[0-9+\-*/().\s]+$')
            if not allowed_chars.match(expression):
                raise ValueError("Expression contains invalid characters")
            
            # Additional safety: prevent function calls
            if any(func in expression.lower() for func in ['import', 'exec', 'eval', '__']):
                raise ValueError("Expression contains forbidden operations")
            
            # Use ast.literal_eval for safer evaluation (only literals)
            import ast
            try:
                # For simple expressions, we can use a safer approach
                result = eval(expression, {"__builtins__": {}}, {})
                self.history.append(f"{expression} = {result}")
                return result
            except (SyntaxError, NameError, TypeError) as e:
                raise ValueError(f"Invalid mathematical expression: {str(e)}")
        except ValueError as e:
            self.history.append(f"{expression} = ERROR: {str(e)}")
            raise e
        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            self.history.append(f"{expression} = ERROR: {error_msg}")
            raise ValueError(error_msg)
    
    def power(self, base, exponent):
        try:
            # Input validation
            if not isinstance(base, (int, float)) or not isinstance(exponent, (int, float)):
                raise TypeError("Both base and exponent must be numbers")
            
            # Prevent extremely large calculations that could cause overflow
            if abs(exponent) > 1000:
                raise ValueError("Exponent too large (limit: 1000)")
            if abs(base) > 10000 and abs(exponent) > 10:
                raise ValueError("Result would be too large")
            
            result = base ** exponent
            
            # Check for infinity or NaN results
            if math.isinf(result) or math.isnan(result):
                raise ValueError("Result is infinity or not a number")
            
            self.history.append(f"{base} ^ {exponent} = {result}")
            return result
        except (TypeError, ValueError, OverflowError) as e:
            error_msg = f"Power calculation error: {str(e)}"
            self.history.append(f"{base} ^ {exponent} = ERROR: {str(e)}")
            raise ValueError(error_msg)
    
    # INTENTIONAL ISSUE: Inefficient algorithm for large numbers
    def is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, n):  # Should be range(2, int(math.sqrt(n)) + 1)
            if n % i == 0:
                return False
        return True
    
    # INTENTIONAL ISSUE: Memory leak - history grows without bounds
    def get_calculation_history(self):
        return self.history  # Never clears, will grow indefinitely
    
    def sqrt(self, number):
        try:
            # Input validation
            if not isinstance(number, (int, float)):
                raise TypeError("Input must be a number")
            if number < 0:
                raise ValueError("Cannot calculate square root of negative number")
            
            result = math.sqrt(number)
            self.history.append(f"√{number} = {result}")
            return result
        except (TypeError, ValueError) as e:
            error_msg = f"Square root error: {str(e)}"
            self.history.append(f"√{number} = ERROR: {str(e)}")
            raise ValueError(error_msg)
    
    def factorial(self, n):
        try:
            # Input validation
            if not isinstance(n, int):
                raise TypeError("Factorial input must be an integer")
            if n < 0:
                raise ValueError("Factorial is not defined for negative numbers")
            if n > 170:  # Factorial of 171 overflows in most systems
                raise ValueError("Number too large for factorial calculation (limit: 170)")
            
            if n == 0 or n == 1:
                result = 1
            else:
                result = 1
                for i in range(1, n + 1):
                    result *= i
            
            self.history.append(f"{n}! = {result}")
            return result
        except (TypeError, ValueError) as e:
            error_msg = f"Factorial error: {str(e)}"
            self.history.append(f"{n}! = ERROR: {str(e)}")
            raise ValueError(error_msg)

# INTENTIONAL ISSUE: Global state and poor initialization
calculator_instance = Calculator()

def quick_divide(a, b):
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both arguments must be numbers")
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    except (TypeError, ZeroDivisionError) as e:
        raise ValueError(f"Division error: {str(e)}")

def batch_calculate(expressions):
    try:
        if not isinstance(expressions, list):
            raise TypeError("Input must be a list of expressions")
        
        results = []
        calc = Calculator()
        
        for expr in expressions:
            try:
                if not isinstance(expr, str):
                    results.append({"expression": expr, "result": None, "error": "Expression must be a string"})
                    continue
                
                result = calc.calculate_expression(expr)
                results.append({"expression": expr, "result": result, "error": None})
            except ValueError as e:
                results.append({"expression": expr, "result": None, "error": str(e)})
            except Exception as e:
                results.append({"expression": expr, "result": None, "error": f"Unexpected error: {str(e)}"})
        
        return results
    except TypeError as e:
        raise ValueError(f"Batch calculation error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in batch calculation: {str(e)}")