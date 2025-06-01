"""
FastAPI application with intentional security and performance issues

INTENTIONAL ISSUES:
- SQL injection vulnerabilities
- Missing rate limiting
- No authentication/authorization
- Poor error responses that leak information
- No input sanitization
- Missing CORS configuration
- Hardcoded secrets
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import hashlib
import os
from pydantic import BaseModel, validator
from typing import List, Optional
import logging
import re
import html
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fixed: Use environment variables for secrets
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

app = FastAPI(title="User Management API")

# INTENTIONAL ISSUE: Overly permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    email: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 characters, alphanumeric and underscore only')
        return html.escape(v)
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return html.escape(v)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

# INTENTIONAL ISSUE: Direct database connection without proper connection pooling
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# INTENTIONAL ISSUE: No proper database initialization
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    conn = get_db_connection()
    # Fixed: Using parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE id = ?"
    try:
        cursor = conn.execute(query, (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "username": user[1], "email": user[2]}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/search/{query}")
async def search_users(query: str):
    # Input sanitization
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    # Sanitize input
    sanitized_query = html.escape(query.strip())
    if len(sanitized_query) > 50:
        raise HTTPException(status_code=400, detail="Search query too long")
    
    conn = get_db_connection()
    # Fixed: Using parameterized query to prevent SQL injection
    sql_query = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"
    search_pattern = f"%{sanitized_query}%"
    cursor = conn.execute(sql_query, (search_pattern, search_pattern))
    users = cursor.fetchall()
    conn.close()
    
    return [{"id": user[0], "username": user[1], "email": user[2]} for user in users]

@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    conn = get_db_connection()
    
    # Fixed: Using bcrypt for secure password hashing
    hashed_password = pwd_context.hash(user.password)
    
    try:
        # Fixed: Using parameterized query to prevent SQL injection
        cursor = conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return UserResponse(id=user_id, username=user.username, email=user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create user")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    conn = get_db_connection()
    # Fixed: Using parameterized query to prevent SQL injection
    cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

# INTENTIONAL ISSUE: N+1 query problem
@app.get("/users/")
async def get_all_users():
    conn = get_db_connection()
    cursor = conn.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()
    
    users = []
    for user_id in user_ids:
        # Fixed: Using parameterized query to prevent SQL injection
        user_cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id[0],))
        user = user_cursor.fetchone()
        if user:
            users.append({"id": user[0], "username": user[1], "email": user[2]})
    
    conn.close()
    return users

# INTENTIONAL ISSUE: Unsafe file operations
@app.post("/upload/")
async def upload_file(filename: str, content: str):
    # Input validation and sanitization
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Validate file extension
    allowed_extensions = {'.txt', '.json', '.csv'}
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Sanitize filename
    sanitized_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Validate content size
    if len(content) > 1024 * 1024:  # 1MB limit
        raise HTTPException(status_code=400, detail="File too large")
    
    file_path = f"uploads/{sanitized_filename}"
    
    try:
        with open(file_path, 'w') as f:
            f.write(html.escape(content))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    return {"message": f"File {sanitized_filename} uploaded successfully"}

# Removed debug endpoint that exposed sensitive information

# INTENTIONAL ISSUE: No rate limiting on sensitive endpoint
@app.post("/login/")
async def login(username: str, password: str):
    conn = get_db_connection()
    
    # Get user from database first
    user_cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = user_cursor.fetchone()
    
    if user and pwd_context.verify(password, user[3]):  # user[3] is password hash
        conn.close()
        return {"message": "Login successful", "user_id": user[0]}
    else:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

if __name__ == "__main__":
    import uvicorn
    # INTENTIONAL ISSUE: Debug mode in production
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)