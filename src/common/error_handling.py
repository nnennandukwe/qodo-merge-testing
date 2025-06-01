"""
Common error handling utilities and custom exceptions.

This module provides standardized error handling, logging utilities,
and custom exception classes for the application.
"""

import logging
import traceback
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    EXTERNAL_API = "external_api"


@dataclass
class ErrorDetails:
    """Structured error information."""
    code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    user_message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[list] = None


class ApplicationError(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ):
        super().__init__(message)
        self.error_details = ErrorDetails(
            code=code,
            message=message,
            category=category,
            severity=severity,
            user_message=user_message or "An error occurred. Please try again.",
            details=details,
            suggestions=suggestions
        )


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value:
            details['invalid_value'] = value
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            user_message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            user_message="Invalid credentials. Please try again.",
            **kwargs
        )


class AuthorizationError(ApplicationError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            code="AUTHZ_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            user_message="You don't have permission to perform this action.",
            **kwargs
        )


class DatabaseError(ApplicationError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            code="DB_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            user_message="A database error occurred. Please try again later.",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )


class NetworkError(ApplicationError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, endpoint: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if endpoint:
            details['endpoint'] = endpoint
        
        super().__init__(
            message=message,
            code="NETWORK_ERROR",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            user_message="Network error. Please check your connection and try again.",
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )


class BusinessLogicError(ApplicationError):
    """Raised when business logic validation fails."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            code="BUSINESS_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            user_message=message,
            **kwargs
        )


class ErrorLogger:
    """Centralized error logging utility."""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
    
    def log_error(
        self,
        error: Union[Exception, ApplicationError],
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ) -> str:
        """
        Log an error with structured information.
        
        Args:
            error: Exception or ApplicationError to log
            context: Additional context information
            include_traceback: Whether to include stack trace
            
        Returns:
            Error ID for tracking
        """
        import uuid
        error_id = str(uuid.uuid4())
        
        if isinstance(error, ApplicationError):
            log_data = {
                'error_id': error_id,
                'code': error.error_details.code,
                'message': error.error_details.message,
                'category': error.error_details.category.value,
                'severity': error.error_details.severity.value,
                'details': error.error_details.details or {},
                'context': context or {}
            }
            
            if include_traceback:
                log_data['traceback'] = traceback.format_exc()
            
            log_level = self._get_log_level(error.error_details.severity)
            self.logger.log(log_level, f"Application error: {error.error_details.message}", extra=log_data)
        else:
            log_data = {
                'error_id': error_id,
                'error_type': type(error).__name__,
                'message': str(error),
                'context': context or {}
            }
            
            if include_traceback:
                log_data['traceback'] = traceback.format_exc()
            
            self.logger.error(f"Unexpected error: {str(error)}", extra=log_data)
        
        return error_id
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Convert error severity to logging level."""
        severity_mapping = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return severity_mapping.get(severity, logging.ERROR)


class ErrorHandler:
    """Centralized error handling and response formatting."""
    
    def __init__(self):
        self.logger = ErrorLogger()
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and return a formatted response.
        
        Args:
            error: Exception to handle
            context: Additional context information
            
        Returns:
            Formatted error response
        """
        error_id = self.logger.log_error(error, context)
        
        if isinstance(error, ApplicationError):
            return {
                'success': False,
                'error': {
                    'id': error_id,
                    'code': error.error_details.code,
                    'message': error.error_details.user_message,
                    'category': error.error_details.category.value,
                    'suggestions': error.error_details.suggestions or []
                }
            }
        else:
            # Generic error response for unexpected errors
            return {
                'success': False,
                'error': {
                    'id': error_id,
                    'code': 'INTERNAL_ERROR',
                    'message': 'An internal error occurred. Please try again later.',
                    'category': 'system'
                }
            }
    
    def handle_validation_errors(self, errors: list) -> Dict[str, Any]:
        """
        Handle multiple validation errors.
        
        Args:
            errors: List of validation error messages
            
        Returns:
            Formatted validation error response
        """
        return {
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'category': 'validation',
                'validation_errors': errors
            }
        }


def safe_execute(func, default_return=None, error_handler: Optional[ErrorHandler] = None):
    """
    Decorator for safe function execution with error handling.
    
    Args:
        func: Function to execute safely
        default_return: Default return value on error
        error_handler: Custom error handler
        
    Returns:
        Decorator function
    """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if error_handler:
                error_handler.handle_error(e)
            else:
                ErrorLogger().log_error(e)
            return default_return
    
    return decorator


# Global instances
default_error_logger = ErrorLogger()
default_error_handler = ErrorHandler()