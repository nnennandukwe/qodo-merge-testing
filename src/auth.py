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
from datetime import datetime, timedelta
from typing import Optional, Dict

# INTENTIONAL ISSUE: Weak secret key
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# INTENTIONAL ISSUE: Global session storage (not scalable, no persistence)
active_sessions = {}
failed_login_attempts = {}

class AuthManager:
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
    
    # INTENTIONAL ISSUE: Weak password hashing using MD5
    def hash_password(self, password: str) -> str:
        return hashlib.md5(password.encode()).hexdigest()
    
    # INTENTIONAL ISSUE: No password complexity validation
    def validate_password(self, password: str) -> bool:
        return len(password) > 0  # Extremely weak validation
    
    # INTENTIONAL ISSUE: Timing attack vulnerability
    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        provided_hash = self.hash_password(provided_password)
        
        # INTENTIONAL ISSUE: Direct comparison allows timing attacks
        return stored_hash == provided_hash
    
    # INTENTIONAL ISSUE: Insecure JWT implementation
    def create_jwt_token(self, user_id: int, username: str) -> str:
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            # INTENTIONAL ISSUE: Including sensitive data in JWT
            'admin': True if username == 'admin' else False,
            'secret_key': SECRET_KEY  # Never include secrets in tokens!
        }
        
        # INTENTIONAL ISSUE: Using weak secret
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # INTENTIONAL ISSUE: Poor JWT validation
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        try:
            # INTENTIONAL ISSUE: No algorithm verification
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            # INTENTIONAL ISSUE: Generic error handling
            return None
        except Exception:
            # INTENTIONAL ISSUE: Swallowing all exceptions
            return None
    
    # INTENTIONAL ISSUE: Insecure session management
    def create_session(self, user_id: int) -> str:
        # INTENTIONAL ISSUE: Predictable session ID
        session_id = f"session_{user_id}_{int(time.time())}"
        
        active_sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        
        return session_id
    
    # INTENTIONAL ISSUE: No session cleanup
    def validate_session(self, session_id: str) -> bool:
        if session_id not in active_sessions:
            return False
        
        session = active_sessions[session_id]
        current_time = time.time()
        
        # INTENTIONAL ISSUE: No automatic session cleanup for expired sessions
        if current_time - session['created_at'] > self.session_timeout:
            return False
        
        # Update last accessed time
        session['last_accessed'] = current_time
        return True
    
    # INTENTIONAL ISSUE: No rate limiting on login attempts
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        # INTENTIONAL ISSUE: No protection against brute force attacks
        
        # Simulate database lookup (with SQL injection vulnerability)
        from .database import get_user_by_email
        user = get_user_by_email(username)  # Assuming email as username
        
        if user and self.verify_password(user[3], password):  # user[3] is password hash
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        
        # INTENTIONAL ISSUE: Information disclosure
        if user:
            return {'error': 'Invalid password'}
        else:
            return {'error': 'User not found'}
    
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

# INTENTIONAL ISSUE: Insecure password generation
def generate_temporary_password() -> str:
    # INTENTIONAL ISSUE: Weak random password
    return ''.join(random.choices(string.ascii_letters, k=8))

# INTENTIONAL ISSUE: Unsafe user registration
def register_user(username: str, email: str, password: str) -> Dict:
    # INTENTIONAL ISSUE: No input validation
    if not username or not email or not password:
        return {'error': 'Missing required fields'}
    
    # INTENTIONAL ISSUE: No duplicate check
    password_hash = auth_manager.hash_password(password)
    
    # INTENTIONAL ISSUE: Direct database insertion without proper error handling
    from .database import db_manager
    try:
        user_id = db_manager.create_user_unsafe(username, email, password_hash)
        return {'success': True, 'user_id': user_id}
    except Exception as e:
        # INTENTIONAL ISSUE: Exposing internal error details
        return {'error': f'Registration failed: {str(e)}'}

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