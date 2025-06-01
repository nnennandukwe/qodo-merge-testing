"""
Security utilities for password hashing, token generation, and validation.

This module provides secure implementations for common security operations
including password hashing, secure random generation, and input sanitization.
"""

import hashlib
import secrets
import string
import re
import time
import logging
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class PasswordRequirements:
    """Password complexity requirements."""
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    forbidden_patterns: List[str] = None
    
    def __post_init__(self):
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                'password', '123456', 'admin', 'qwerty', 'letmein',
                'welcome', 'password123', '12345678', 'abc123'
            ]


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class PasswordValidationError(SecurityError):
    """Raised when password validation fails."""
    pass


class TokenGenerationError(SecurityError):
    """Raised when token generation fails."""
    pass


class PasswordValidator:
    """Validates passwords against security requirements."""
    
    def __init__(self, requirements: Optional[PasswordRequirements] = None):
        self.requirements = requirements or PasswordRequirements()
        self.logger = logging.getLogger(__name__)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not isinstance(password, str):
            errors.append("Password must be a string")
            return False, errors
        
        # Length validation
        if len(password) < self.requirements.min_length:
            errors.append(f"Password must be at least {self.requirements.min_length} characters long")
        
        if len(password) > self.requirements.max_length:
            errors.append(f"Password cannot exceed {self.requirements.max_length} characters")
        
        # Character type validation
        if self.requirements.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.requirements.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.requirements.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.requirements.require_special_chars:
            special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")
        
        # Check for forbidden patterns
        if password.lower() in self.requirements.forbidden_patterns:
            errors.append("Password is too common. Please choose a more secure password.")
        
        # Check for repeated patterns
        if self._has_repeated_patterns(password):
            errors.append("Avoid using repeated patterns in your password")
        
        return len(errors) == 0, errors
    
    def _has_repeated_patterns(self, password: str) -> bool:
        """Check if password contains repeated patterns."""
        # Simple pattern detection for consecutive repeated characters
        return bool(re.search(r'(.)\1{2,}', password))


class SecureHasher:
    """Provides secure hashing operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using a secure algorithm.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
            
        Raises:
            PasswordValidationError: If password is invalid
        """
        if not isinstance(password, str) or len(password) == 0:
            raise PasswordValidationError("Password must be a non-empty string")
        
        try:
            # Generate a random salt
            salt = secrets.token_bytes(32)
            
            # Use PBKDF2 for password hashing (secure alternative to bcrypt)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            
            # Combine salt and hash for storage
            return salt.hex() + ':' + pwd_hash.hex()
        except Exception as e:
            self.logger.error(f"Password hashing error: {e}")
            raise PasswordValidationError("Password hashing failed")
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: Plain text password
            stored_hash: Previously hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            if not isinstance(password, str) or not isinstance(stored_hash, str):
                return False
            
            # Extract salt and hash
            if ':' not in stored_hash:
                return False
            
            salt_hex, hash_hex = stored_hash.split(':', 1)
            salt = bytes.fromhex(salt_hex)
            stored_pwd_hash = bytes.fromhex(hash_hex)
            
            # Hash the provided password with the same salt
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            
            # Constant-time comparison
            return self._constant_time_compare(pwd_hash, stored_pwd_hash)
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False
    
    def _constant_time_compare(self, a: bytes, b: bytes) -> bool:
        """Compare two byte strings in constant time."""
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        return result == 0


class SecureTokenGenerator:
    """Generates cryptographically secure tokens."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_session_token(self, length: int = 32) -> str:
        """
        Generate a secure session token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            URL-safe base64 encoded token
            
        Raises:
            TokenGenerationError: If token generation fails
        """
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            self.logger.error(f"Session token generation error: {e}")
            raise TokenGenerationError("Failed to generate session token")
    
    def generate_api_key(self, prefix: str = "qm", length: int = 32) -> str:
        """
        Generate a secure API key with prefix.
        
        Args:
            prefix: Key prefix
            length: Random part length in bytes
            
        Returns:
            API key with prefix
            
        Raises:
            TokenGenerationError: If API key generation fails
        """
        try:
            random_part = secrets.token_urlsafe(length)
            return f"{prefix}_{random_part}"
        except Exception as e:
            self.logger.error(f"API key generation error: {e}")
            raise TokenGenerationError("Failed to generate API key")
    
    def generate_temporary_password(self, length: int = 16) -> str:
        """
        Generate a secure temporary password.
        
        Args:
            length: Password length
            
        Returns:
            Temporary password meeting security requirements
            
        Raises:
            TokenGenerationError: If password generation fails
        """
        try:
            # Ensure we have all required character types
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            special = '!@#$%^&*'
            
            # Start with one of each required type
            password = [
                secrets.choice(lowercase),
                secrets.choice(uppercase),
                secrets.choice(digits),
                secrets.choice(special)
            ]
            
            # Fill the rest randomly
            all_chars = lowercase + uppercase + digits + special
            for _ in range(length - 4):
                password.append(secrets.choice(all_chars))
            
            # Shuffle to randomize positions
            secrets.SystemRandom().shuffle(password)
            
            return ''.join(password)
        except Exception as e:
            self.logger.error(f"Temporary password generation error: {e}")
            raise TokenGenerationError("Failed to generate temporary password")


class InputSanitizer:
    """Sanitizes user input to prevent security vulnerabilities."""
    
    @staticmethod
    def sanitize_html_input(input_str: str) -> str:
        """
        Sanitize HTML input to prevent XSS attacks.
        
        Args:
            input_str: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return ''
        
        # Remove all HTML tags
        sanitized = re.sub(r'<[^>]*>', '', input_str)
        
        # Encode HTML entities
        html_entities = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for char, entity in html_entities.items():
            sanitized = sanitized.replace(char, entity)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        if not isinstance(filename, str):
            return 'unknown'
        
        # Remove directory traversal patterns
        sanitized = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Keep only alphanumeric, dots, hyphens, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', sanitized)
        
        # Ensure filename is not empty and not too long
        if not sanitized:
            sanitized = 'file'
        
        return sanitized[:255]  # Limit to 255 characters


# Global instances
default_password_validator = PasswordValidator()
default_hasher = SecureHasher()
default_token_generator = SecureTokenGenerator()
default_sanitizer = InputSanitizer()