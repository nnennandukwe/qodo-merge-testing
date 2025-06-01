"""
Refactored FastAPI application with improved code quality and organization.

This module demonstrates proper code structure, separation of concerns,
and use of common utilities for better maintainability.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime

# Import refactored common utilities
from .common.database_connection import default_db_manager, DatabaseConnectionError
from .common.security_utils import (
    default_password_validator, 
    default_hasher, 
    default_sanitizer,
    PasswordValidationError
)
from .common.error_handling import (
    default_error_handler,
    ValidationError,
    DatabaseError,
    BusinessLogicError,
    ApplicationError
)

# Configuration management
class APIConfig:
    """Application configuration settings."""
    
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'development-key-change-in-production')
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./users.db')
        self.cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))


# Pydantic models with proper validation
class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    
    username: str = Field(..., min_length=3, max_length=30, description="Username (3-30 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (8-128 characters)")
    
    @validator('username')
    def validate_username(cls, value):
        """Validate username format."""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return value.lower().strip()
    
    @validator('email')
    def validate_email_format(cls, value):
        """Additional email validation."""
        return value.lower().strip()
    
    @validator('password')
    def validate_password_strength(cls, value):
        """Validate password against security requirements."""
        is_valid, errors = default_password_validator.validate_password_strength(value)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return value


class UserResponse(BaseModel):
    """Response model for user data."""
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    is_active: bool = Field(True, description="Account status")


class UserListResponse(BaseModel):
    """Response model for user lists."""
    
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int


class APIResponse(BaseModel):
    """Standard API response format."""
    
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None


# Application factory
def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    config = APIConfig()
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, config.log_level))
    logger = logging.getLogger(__name__)
    
    app = FastAPI(
        title="User Management API",
        description="Refactored API with improved code quality",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS with proper restrictions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Accept", "Authorization", "Content-Type"],
    )
    
    # Error handler middleware
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request, exc: ApplicationError):
        """Handle application-specific errors."""
        error_response = default_error_handler.handle_error(exc)
        return JSONResponse(
            status_code=_get_http_status_code(exc),
            content=error_response
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        error_response = default_error_handler.handle_error(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
    
    return app


# Business logic services
class UserService:
    """Service class for user-related business logic."""
    
    def __init__(self):
        self.db_manager = default_db_manager
        self.hasher = default_hasher
        self.sanitizer = default_sanitizer
    
    async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
        """
        Create a new user with proper validation and error handling.
        
        Args:
            user_data: Validated user creation data
            
        Returns:
            Created user information
            
        Raises:
            ValidationError: If user data is invalid
            BusinessLogicError: If user already exists
            DatabaseError: If database operation fails
        """
        try:
            # Check if user already exists
            if await self._user_exists(user_data.username, user_data.email):
                raise BusinessLogicError(
                    "A user with this username or email already exists",
                    details={'username': user_data.username, 'email': user_data.email}
                )
            
            # Hash password securely
            try:
                password_hash = self.hasher.hash_password(user_data.password)
            except PasswordValidationError as e:
                raise ValidationError(str(e), field='password')
            
            # Insert user into database
            user_id = await self._insert_user(user_data, password_hash)
            
            # Return created user
            return UserResponse(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to create user: {str(e)}", operation="create_user")
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User information if found, None otherwise
            
        Raises:
            ValidationError: If user_id is invalid
            DatabaseError: If database operation fails
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("User ID must be a positive integer", field='user_id')
        
        try:
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.execute(
                    "SELECT id, username, email, created_at, is_active FROM users WHERE id = ?",
                    (user_id,)
                )
                user_row = cursor.fetchone()
                
                if user_row:
                    return UserResponse(
                        id=user_row[0],
                        username=user_row[1],
                        email=user_row[2],
                        created_at=user_row[3] if user_row[3] else None,
                        is_active=bool(user_row[4]) if user_row[4] is not None else True
                    )
                return None
                
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve user: {str(e)}", operation="get_user")
    
    async def search_users(self, query: str, page: int = 1, page_size: int = 20) -> UserListResponse:
        """
        Search users by username or email.
        
        Args:
            query: Search query
            page: Page number (1-based)
            page_size: Number of results per page
            
        Returns:
            Paginated user search results
            
        Raises:
            ValidationError: If search parameters are invalid
            DatabaseError: If database operation fails
        """
        # Validate input parameters
        if not isinstance(query, str) or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters", field='query')
        
        if not isinstance(page, int) or page < 1:
            raise ValidationError("Page must be a positive integer", field='page')
        
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise ValidationError("Page size must be between 1 and 100", field='page_size')
        
        # Sanitize search query
        sanitized_query = self.sanitizer.sanitize_html_input(query.strip())
        search_pattern = f"%{sanitized_query}%"
        
        try:
            with self.db_manager.get_connection_context() as conn:
                # Get total count
                count_cursor = conn.execute(
                    "SELECT COUNT(*) FROM users WHERE username LIKE ? OR email LIKE ?",
                    (search_pattern, search_pattern)
                )
                total_count = count_cursor.fetchone()[0]
                
                # Get paginated results
                offset = (page - 1) * page_size
                results_cursor = conn.execute(
                    """
                    SELECT id, username, email, created_at, is_active 
                    FROM users 
                    WHERE username LIKE ? OR email LIKE ?
                    ORDER BY username
                    LIMIT ? OFFSET ?
                    """,
                    (search_pattern, search_pattern, page_size, offset)
                )
                
                users = []
                for row in results_cursor.fetchall():
                    users.append(UserResponse(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        created_at=row[3] if row[3] else None,
                        is_active=bool(row[4]) if row[4] is not None else True
                    ))
                
                return UserListResponse(
                    users=users,
                    total_count=total_count,
                    page=page,
                    page_size=page_size
                )
                
        except Exception as e:
            raise DatabaseError(f"Failed to search users: {str(e)}", operation="search_users")
    
    async def _user_exists(self, username: str, email: str) -> bool:
        """Check if a user with the given username or email already exists."""
        try:
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM users WHERE username = ? OR email = ?",
                    (username, email)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check user existence: {str(e)}", operation="user_exists_check")
    
    async def _insert_user(self, user_data: UserCreateRequest, password_hash: str) -> int:
        """Insert a new user into the database."""
        try:
            with self.db_manager.get_transaction_context() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, email, password, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_data.username, user_data.email, password_hash, datetime.utcnow(), True)
                )
                return cursor.lastrowid
        except Exception as e:
            raise DatabaseError(f"Failed to insert user: {str(e)}", operation="insert_user")


# Initialize services
user_service = UserService()


# API route handlers
app = create_application()


@app.on_event("startup")
async def initialize_database():
    """Initialize database schema on startup."""
    try:
        await _create_database_schema()
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint."""
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={"status": "ok", "timestamp": datetime.utcnow()}
    )


@app.post("/users", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_data: UserCreateRequest):
    """Create a new user."""
    try:
        created_user = await user_service.create_user(user_data)
        return APIResponse(
            success=True,
            message="User created successfully",
            data=created_user.dict()
        )
    except ApplicationError:
        raise  # Let the error handler deal with it


@app.get("/users/{user_id}", response_model=APIResponse)
async def get_user_endpoint(user_id: int):
    """Get a user by ID."""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise BusinessLogicError("User not found", details={'user_id': user_id})
        
        return APIResponse(
            success=True,
            data=user.dict()
        )
    except ApplicationError:
        raise


@app.get("/users/search/{query}", response_model=APIResponse)
async def search_users_endpoint(
    query: str,
    page: int = 1,
    page_size: int = 20
):
    """Search users by username or email."""
    try:
        results = await user_service.search_users(query, page, page_size)
        return APIResponse(
            success=True,
            data=results.dict()
        )
    except ApplicationError:
        raise


# Helper functions
def _get_http_status_code(error: ApplicationError) -> int:
    """Map application errors to HTTP status codes."""
    from .common.error_handling import ErrorCategory
    
    status_mapping = {
        ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
        ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
        ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
        ErrorCategory.DATABASE: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCategory.BUSINESS_LOGIC: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCategory.NETWORK: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    
    return status_mapping.get(error.error_details.category, status.HTTP_500_INTERNAL_SERVER_ERROR)


async def _create_database_schema():
    """Create database schema if it doesn't exist."""
    try:
        with default_db_manager.get_connection_context() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)')
            
    except Exception as e:
        raise DatabaseError(f"Failed to create database schema: {str(e)}", operation="create_schema")