"""
Authentication module with intentional security vulnerabilities

INTENTIONAL ISSUES:
- Weak password hashing (MD5)
- JWT implementation issues
- Session management problems
- No rate limiting
- Timing attack vulnerabilities
- Missing password complexity requirements
"""

import hashlib
import jwt
import time
import os
import random
import string
import secrets
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

# INTENTIONAL ISSUE: Weak secret key
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# INTENTIONAL ISSUE: Global session storage (not scalable, no persistence)
active_sessions = {}
failed_login_attempts = {}

class AuthManager:
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt (secure)"""
        try:
            if not isinstance(password, str) or len(password) == 0:
                raise ValueError("Password must be a non-empty string")
            
            # Use bcrypt for secure password hashing
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logging.error(f"Password hashing error: {str(e)}")
            raise ValueError("Password hashing failed")
    
    def validate_password(self, password: str) -> Tuple[bool, list]:
        """Validate password complexity"""
        errors = []
        
        if not isinstance(password, str):
            errors.append("Password must be a string")
            return False, errors
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password cannot exceed 128 characters")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456', 'admin', 'qwerty', 'letmein',
            'welcome', 'password123', '12345678'
        ]
        
        if password.lower() in weak_passwords:
            errors.append("Password is too common. Please choose a more secure password.")
        
        return len(errors) == 0, errors
    
    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        """Verify password using constant-time comparison"""
        try:
            if not isinstance(stored_hash, str) or not isinstance(provided_password, str):
                return False
            
            # Use bcrypt's built-in constant-time verification
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception as e:
            logging.error(f"Password verification error: {str(e)}")
            return False
    
    def create_jwt_token(self, user_id: int, username: str, is_admin: bool = False) -> str:
        """Create a secure JWT token"""
        try:
            if not isinstance(user_id, int) or not isinstance(username, str):
                raise ValueError("Invalid user data for token creation")
            
            # Use environment variable for secret key or generate one
            secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(64))
            
            payload = {
                'user_id': user_id,
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=1),  # Shorter expiration
                'iat': datetime.utcnow(),
                'iss': 'qodo-merge-app',  # Issuer
                'aud': 'qodo-merge-users',  # Audience
                'jti': secrets.token_urlsafe(16),  # JWT ID for tracking
                'is_admin': is_admin
            }
            
            return jwt.encode(payload, secret_key, algorithm='HS256')
        except Exception as e:
            logging.error(f"JWT token creation error: {str(e)}")
            raise ValueError("Token creation failed")
    
    def verify_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Verify JWT token and return (is_valid, payload, error_message)"""
        try:
            if not isinstance(token, str) or not token.strip():
                return False, None, "Invalid token format"
            
            secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(64))
            
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=['HS256'],
                audience='qodo-merge-users',
                issuer='qodo-merge-app',
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True
                }
            )
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError:
            return False, None, "Invalid token"
        except jwt.InvalidSignatureError:
            return False, None, "Invalid token signature"
        except jwt.InvalidAudienceError:
            return False, None, "Invalid token audience"
        except jwt.InvalidIssuerError:
            return False, None, "Invalid token issuer"
        except Exception as e:
            logging.error(f"JWT verification error: {str(e)}")
            return False, None, "Token verification failed"
    
    def create_session(self, user_id: int) -> str:
        """Create a secure session with cryptographically random ID"""
        try:
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValueError("Invalid user ID")
            
            # Generate cryptographically secure session ID
            session_id = secrets.token_urlsafe(32)
            
            current_time = time.time()
            active_sessions[session_id] = {
                'user_id': user_id,
                'created_at': current_time,
                'last_accessed': current_time,
                'ip_address': None,  # Should be set by caller
                'user_agent': None   # Should be set by caller
            }
            
            # Clean up old sessions
            self._cleanup_expired_sessions()
            
            return session_id
        except Exception as e:
            logging.error(f"Session creation error: {str(e)}")
            raise ValueError("Session creation failed")
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate session and return (is_valid, error_message)"""
        try:
            if not isinstance(session_id, str) or not session_id.strip():
                return False, "Invalid session ID format"
            
            if session_id not in active_sessions:
                return False, "Session not found"
            
            session = active_sessions[session_id]
            current_time = time.time()
            
            # Check if session has expired
            if current_time - session['created_at'] > self.session_timeout:
                # Remove expired session
                del active_sessions[session_id]
                return False, "Session has expired"
            
            # Update last accessed time
            session['last_accessed'] = current_time
            return True, None
            
        except Exception as e:
            logging.error(f"Session validation error: {str(e)}")
            return False, "Session validation failed"
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions from memory"""
        try:
            current_time = time.time()
            expired_sessions = [
                session_id for session_id, session in active_sessions.items()
                if current_time - session['created_at'] > self.session_timeout
            ]
            
            for session_id in expired_sessions:
                del active_sessions[session_id]
                
        except Exception as e:
            logging.error(f"Session cleanup error: {str(e)}")
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Tuple[bool, Optional[Dict], str]:
        """Authenticate user with rate limiting and secure error handling"""
        try:
            # Input validation
            if not isinstance(username, str) or not isinstance(password, str):
                return False, None, "Invalid credentials format"
            
            username = username.strip().lower()
            if not username or not password:
                return False, None, "Username and password are required"
            
            # Check rate limiting
            if not self._check_rate_limit(username, ip_address):
                return False, None, "Too many failed attempts. Please try again later."
            
            # Simulate database lookup with proper error handling
            try:
                from .database import get_user_by_email
                user = get_user_by_email(username)
            except Exception as e:
                logging.error(f"Database error during authentication: {str(e)}")
                return False, None, "Authentication service temporarily unavailable"
            
            # Always perform password verification to prevent timing attacks
            # even if user doesn't exist
            if user:
                password_valid = self.verify_password(user[3], password)  # user[3] is password hash
            else:
                # Perform dummy password verification to maintain constant time
                self.verify_password('$2b$12$dummy.hash.to.prevent.timing.attacks', password)
                password_valid = False
            
            if user and password_valid:
                # Reset failed attempts on successful login
                self._reset_rate_limit(username, ip_address)
                
                return True, {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2]
                }, "Authentication successful"
            else:
                # Record failed attempt
                self._record_failed_attempt(username, ip_address)
                
                # Generic error message to prevent username enumeration
                return False, None, "Invalid username or password"
                
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return False, None, "Authentication failed"
    
    def _check_rate_limit(self, username: str, ip_address: str = None) -> bool:
        """Check if user/IP is rate limited"""
        try:
            current_time = time.time()
            window_seconds = 900  # 15 minutes
            max_attempts = 5
            
            # Clean up old attempts
            cutoff_time = current_time - window_seconds
            
            for key in list(failed_login_attempts.keys()):
                failed_login_attempts[key] = [
                    attempt_time for attempt_time in failed_login_attempts[key]
                    if attempt_time > cutoff_time
                ]
                if not failed_login_attempts[key]:
                    del failed_login_attempts[key]
            
            # Check attempts for username
            username_attempts = len(failed_login_attempts.get(f"user:{username}", []))
            
            # Check attempts for IP if provided
            ip_attempts = 0
            if ip_address:
                ip_attempts = len(failed_login_attempts.get(f"ip:{ip_address}", []))
            
            return username_attempts < max_attempts and ip_attempts < max_attempts
            
        except Exception as e:
            logging.error(f"Rate limit check error: {str(e)}")
            return True  # Allow on error to prevent lockout
    
    def _record_failed_attempt(self, username: str, ip_address: str = None):
        """Record a failed login attempt"""
        try:
            current_time = time.time()
            
            # Record for username
            user_key = f"user:{username}"
            if user_key not in failed_login_attempts:
                failed_login_attempts[user_key] = []
            failed_login_attempts[user_key].append(current_time)
            
            # Record for IP if provided
            if ip_address:
                ip_key = f"ip:{ip_address}"
                if ip_key not in failed_login_attempts:
                    failed_login_attempts[ip_key] = []
                failed_login_attempts[ip_key].append(current_time)
                
        except Exception as e:
            logging.error(f"Failed attempt recording error: {str(e)}")
    
    def _reset_rate_limit(self, username: str, ip_address: str = None):
        """Reset rate limit counters on successful login"""
        try:
            user_key = f"user:{username}"
            if user_key in failed_login_attempts:
                del failed_login_attempts[user_key]
            
            if ip_address:
                ip_key = f"ip:{ip_address}"
                if ip_key in failed_login_attempts:
                    del failed_login_attempts[ip_key]
                    
        except Exception as e:
            logging.error(f"Rate limit reset error: {str(e)}")
    
    # INTENTIONAL ISSUE: Weak password reset mechanism
    def generate_reset_token(self, email: str) -> str:
        # INTENTIONAL ISSUE: Predictable reset token
        timestamp = str(int(time.time()))
        return hashlib.md5(f"{email}{timestamp}".encode()).hexdigest()
    
    # INTENTIONAL ISSUE: No token expiration for password reset
    def validate_reset_token(self, token: str, email: str) -> bool:
        # INTENTIONAL ISSUE: Regenerating token to check - timing attack
        current_time = int(time.time())
        for i in range(3600):  # Check last hour
            expected_token = hashlib.md5(f"{email}{current_time - i}".encode()).hexdigest()
            if token == expected_token:
                return True
        return False

# INTENTIONAL ISSUE: Global auth instance
auth_manager = AuthManager()

def generate_temporary_password() -> str:
    """Generate a cryptographically secure temporary password"""
    try:
        # Generate a strong temporary password
        length = 16
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        
        # Ensure we have at least one of each required character type
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice('!@#$%^&*')
        ]
        
        # Fill the rest randomly
        for _ in range(length - 4):
            password.append(secrets.choice(chars))
        
        # Shuffle the password to randomize positions
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    except Exception as e:
        logging.error(f"Temporary password generation error: {str(e)}")
        # Fallback to a simpler but still secure method
        return secrets.token_urlsafe(12)

def register_user(username: str, email: str, password: str) -> Dict:
    """Register a new user with proper validation and error handling"""
    try:
        # Input validation
        if not all(isinstance(x, str) for x in [username, email, password]):
            return {'success': False, 'error': 'All fields must be strings'}
        
        username = username.strip()
        email = email.strip().lower()
        
        if not username or not email or not password:
            return {'success': False, 'error': 'Username, email, and password are required'}
        
        # Validate username
        if len(username) < 3 or len(username) > 30:
            return {'success': False, 'error': 'Username must be between 3 and 30 characters'}
        
        if not all(c.isalnum() or c in '_-' for c in username):
            return {'success': False, 'error': 'Username can only contain letters, numbers, underscores, and hyphens'}
        
        # Validate email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {'success': False, 'error': 'Please enter a valid email address'}
        
        # Validate password
        is_valid, password_errors = auth_manager.validate_password(password)
        if not is_valid:
            return {'success': False, 'error': '; '.join(password_errors)}
        
        # Hash password
        try:
            password_hash = auth_manager.hash_password(password)
        except ValueError as e:
            return {'success': False, 'error': 'Password processing failed'}
        
        # Check for existing users (without revealing which field conflicts)
        from .database import db_manager
        try:
            # This would typically be done with a proper database query
            # For now, we'll simulate the check
            existing_user = None
            try:
                from .database import get_user_by_email
                existing_user = get_user_by_email(email)
            except:
                pass  # User doesn't exist, which is what we want
            
            if existing_user:
                return {'success': False, 'error': 'An account with this information already exists'}
            
            # Create user
            user_id = db_manager.create_user_unsafe(username, email, password_hash)
            
            logging.info(f"New user registered: {username} (ID: {user_id})")
            
            return {
                'success': True, 
                'user_id': user_id,
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            logging.error(f"Database error during registration: {str(e)}")
            return {'success': False, 'error': 'Registration failed. Please try again later.'}
            
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return {'success': False, 'error': 'Registration failed. Please try again later.'}

# INTENTIONAL ISSUE: Insecure permission checking
def check_admin_permission(user_id: int) -> bool:
    # INTENTIONAL ISSUE: Hardcoded admin user ID
    return user_id == 1

# INTENTIONAL ISSUE: No proper logout mechanism
def logout_user(session_id: str) -> bool:
    # INTENTIONAL ISSUE: Session not properly invalidated, just removed from memory
    if session_id in active_sessions:
        del active_sessions[session_id]
        return True
    return False

# INTENTIONAL ISSUE: Insecure API key generation
def generate_api_key(user_id: int) -> str:
    # INTENTIONAL ISSUE: Predictable API key
    return f"api_key_{user_id}_{hashlib.md5(str(user_id).encode()).hexdigest()}"

# INTENTIONAL ISSUE: No API key validation or expiration
def validate_api_key(api_key: str) -> Optional[int]:
    # INTENTIONAL ISSUE: Parsing user ID from API key structure
    try:
        parts = api_key.split('_')
        if len(parts) == 3 and parts[0] == 'api' and parts[1] == 'key':
            user_id = int(parts[2])
            # INTENTIONAL ISSUE: No actual validation, just parsing
            return user_id
    except:
        pass
    return None

# INTENTIONAL ISSUE: Storing passwords in plain text for "debugging"
DEBUG_PASSWORDS = {
    'admin': 'admin123',
    'user': 'password',
    'test': 'test123'
}