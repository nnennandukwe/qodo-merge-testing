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
    try:
        # Input validation
        if not user_id.isdigit():
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        conn = get_db_connection()
        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM users WHERE id = ?"
        cursor = conn.execute(query, (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "username": user[1], "email": user[2]}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in get_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logging.error(f"Unexpected error in get_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# INTENTIONAL ISSUE: SQL injection in search
@app.get("/users/search/{query}")
async def search_users(query: str):
    try:
        # Input validation
        if len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        conn = get_db_connection()
        # Use parameterized query to prevent SQL injection
        sql_query = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"
        search_term = f"%{query}%"
        cursor = conn.execute(sql_query, (search_term, search_term))
        users = cursor.fetchall()
        conn.close()
        
        return [{"id": user[0], "username": user[1], "email": user[2]} for user in users]
    except HTTPException:
        raise
    except sqlite3.Error as e:
        logging.error(f"Database error in search_users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logging.error(f"Unexpected error in search_users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# INTENTIONAL ISSUE: Weak password hashing and no validation
@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    try:
        # Input validation
        if len(user.username.strip()) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        if "@" not in user.email or len(user.email.strip()) < 5:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        check_query = "SELECT id FROM users WHERE username = ? OR email = ?"
        cursor = conn.execute(check_query, (user.username, user.email))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Use bcrypt for password hashing (better than MD5)
        import bcrypt
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Use parameterized query to prevent SQL injection
        cursor = conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return UserResponse(id=user_id, username=user.username, email=user.email)
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error in create_user: {str(e)}")
        raise HTTPException(status_code=400, detail="User creation failed due to data constraints")
    except sqlite3.Error as e:
        logging.error(f"Database error in create_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logging.error(f"Unexpected error in create_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    try:
        # Input validation
        if not filename or len(filename.strip()) == 0:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")
        
        # Sanitize filename to prevent directory traversal
        import os.path
        import re
        safe_filename = re.sub(r'[^\w\-_\.]', '', filename)
        if not safe_filename or '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Validate file size (limit to 1MB)
        if len(content) > 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 1MB)")
        
        # Validate file extension
        allowed_extensions = {'.txt', '.csv', '.json', '.md'}
        file_ext = os.path.splitext(safe_filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        file_path = f"uploads/{safe_filename}"
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"message": f"File {safe_filename} uploaded successfully"}
    except HTTPException:
        raise
    except OSError as e:
        logging.error(f"File system error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")
    except Exception as e:
        logging.error(f"Unexpected error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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