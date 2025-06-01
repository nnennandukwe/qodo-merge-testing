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
    
    # INTENTIONAL ISSUE: No input validation, division by zero
    def divide(self, a, b):
        result = a / b  # Will crash on b=0
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    # OPTIMIZED: Efficient memoized fibonacci - O(n) complexity
    def fibonacci(self, n):
        if not hasattr(self, '_fib_cache'):
            self._fib_cache = {}
        
        if n in self._fib_cache:
            return self._fib_cache[n]
        
        if n <= 1:
            result = n
        else:
            result = self.fibonacci(n-1) + self.fibonacci(n-2)
        
        self._fib_cache[n] = result
        return result
    
    # INTENTIONAL ISSUE: Using eval() - major security vulnerability
    def calculate_expression(self, expression):
        try:
            result = eval(expression)  # DANGEROUS!
            return result
        except:
            return "Error"  # Poor error handling
    
    # INTENTIONAL ISSUE: No input validation, potential overflow
    def power(self, base, exponent):
        return base ** exponent  # No limits on exponent size
    
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
    
    # INTENTIONAL ISSUE: Poor error handling and type checking
    def sqrt(self, number):
        return math.sqrt(number)  # Will crash on negative numbers
    
    # INTENTIONAL ISSUE: No input sanitization
    def factorial(self, n):
        if n == 0:
            return 1
        result = 1
        for i in range(1, n + 1):  # No check if n is negative or too large
            result *= i
        return result

# INTENTIONAL ISSUE: Global state and poor initialization
calculator_instance = Calculator()

def quick_divide(a, b):
    # INTENTIONAL ISSUE: No error handling
    return a / b

def batch_calculate(expressions):
    # INTENTIONAL ISSUE: Using eval on user input without sanitization
    results = []
    for expr in expressions:
        try:
            results.append(eval(expr))  # Major security risk
        except:
            results.append(None)  # Silent failures
    return results