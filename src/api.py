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
from pydantic import BaseModel
from typing import List, Optional
import logging

# INTENTIONAL ISSUE: Hardcoded secret key
SECRET_KEY = "super-secret-key-123"
DATABASE_URL = "sqlite:///./test.db"

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

# INTENTIONAL ISSUE: SQL injection vulnerability
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    conn = get_db_connection()
    # Direct string interpolation - SQL injection risk!
    query = f"SELECT * FROM users WHERE id = {user_id}"
    try:
        cursor = conn.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "username": user[1], "email": user[2]}
        else:
            # INTENTIONAL ISSUE: Information disclosure
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found in database")
    except Exception as e:
        # INTENTIONAL ISSUE: Exposing internal error details
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# INTENTIONAL ISSUE: SQL injection in search
@app.get("/users/search/{query}")
async def search_users(query: str):
    conn = get_db_connection()
    # Another SQL injection vulnerability
    sql_query = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
    cursor = conn.execute(sql_query)
    users = cursor.fetchall()
    conn.close()
    
    return [{"id": user[0], "username": user[1], "email": user[2]} for user in users]

# INTENTIONAL ISSUE: Weak password hashing and no validation
@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    conn = get_db_connection()
    
    # INTENTIONAL ISSUE: MD5 hashing (weak and deprecated)
    hashed_password = hashlib.md5(user.password.encode()).hexdigest()
    
    try:
        # INTENTIONAL ISSUE: No input validation, potential SQL injection
        cursor = conn.execute(
            f"INSERT INTO users (username, email, password) VALUES ('{user.username}', '{user.email}', '{hashed_password}')"
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return UserResponse(id=user_id, username=user.username, email=user.email)
    except Exception as e:
        # INTENTIONAL ISSUE: Detailed error message
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")

# INTENTIONAL ISSUE: No authentication required for sensitive operations
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.execute(f"DELETE FROM users WHERE id = {user_id}")
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
        # Making separate query for each user - N+1 problem!
        user_cursor = conn.execute(f"SELECT * FROM users WHERE id = {user_id[0]}")
        user = user_cursor.fetchone()
        if user:
            users.append({"id": user[0], "username": user[1], "email": user[2]})
    
    conn.close()
    return users

# INTENTIONAL ISSUE: Unsafe file operations
@app.post("/upload/")
async def upload_file(filename: str, content: str):
    # No path validation - directory traversal vulnerability
    file_path = f"uploads/{filename}"
    
    # INTENTIONAL ISSUE: No file type validation, no size limits
    with open(file_path, 'w') as f:
        f.write(content)
    
    return {"message": f"File {filename} uploaded successfully"}

# INTENTIONAL ISSUE: Information disclosure in debug endpoint
@app.get("/debug/")
async def debug_info():
    return {
        "environment": os.environ,  # Exposes all environment variables
        "secret_key": SECRET_KEY,   # Exposes secret
        "database_url": DATABASE_URL
    }

# INTENTIONAL ISSUE: No rate limiting on sensitive endpoint
@app.post("/login/")
async def login(username: str, password: str):
    conn = get_db_connection()
    
    # INTENTIONAL ISSUE: Timing attack vulnerability
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    cursor = conn.execute(
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_password}'"
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # INTENTIONAL ISSUE: No proper session management
        return {"message": "Login successful", "user_id": user[0]}
    else:
        # INTENTIONAL ISSUE: Information disclosure about which field failed
        cursor = conn.execute(f"SELECT * FROM users WHERE username = '{username}'")
        if cursor.fetchone():
            raise HTTPException(status_code=401, detail="Invalid password")
        else:
            raise HTTPException(status_code=401, detail="Invalid username")

if __name__ == "__main__":
    import uvicorn
    # INTENTIONAL ISSUE: Debug mode in production
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)