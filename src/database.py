"""
Database operations with intentional issues for Qodo Merge testing

INTENTIONAL ISSUES:
- Connection leaks
- N+1 query problems
- Missing transactions
- Hardcoded credentials
- No connection pooling
- SQL injection vulnerabilities
- Missing indexes considerations
"""

import sqlite3
import psycopg2
from typing import List, Dict, Optional
import os
import time

# Fixed: Use environment variables for database credentials
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "testdb"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "change-this-db-password")
}

class DatabaseManager:
    def __init__(self):
        # INTENTIONAL ISSUE: No connection pooling
        self.connections = []
    
    # INTENTIONAL ISSUE: Connection leak - no proper cleanup
    def get_connection(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            self.connections.append(conn)  # Track connections but never clean up
            return conn
        except:
            # INTENTIONAL ISSUE: Fall back to SQLite without proper error handling
            return sqlite3.connect('fallback.db')
    
    # INTENTIONAL ISSUE: N+1 query problem
    def get_users_with_posts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        
        result = []
        for user in users:
            # Fixed: Using parameterized query to prevent SQL injection
            cursor.execute("SELECT title FROM posts WHERE user_id = ?", (user[0],))
            posts = cursor.fetchall()
            result.append({
                "id": user[0],
                "username": user[1],
                "posts": [post[0] for post in posts]
            })
        
        # INTENTIONAL ISSUE: Connection never closed
        return result
    
    # INTENTIONAL ISSUE: No transaction management
    def transfer_funds(self, from_account: int, to_account: int, amount: float):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fixed: Using parameterized queries to prevent SQL injection
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_account))
        
        # Simulate potential failure point
        time.sleep(0.1)
        
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_account))
        
        conn.commit()
        # INTENTIONAL ISSUE: Connection not closed
    
    # INTENTIONAL ISSUE: SQL injection vulnerability
    def search_products(self, search_term: str, category: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fixed: Using parameterized query to prevent SQL injection
        query = """
            SELECT * FROM products 
            WHERE name LIKE ? 
            AND category = ?
            ORDER BY price
        """
        
        cursor.execute(query, (f"%{search_term}%", category))
        results = cursor.fetchall()
        # INTENTIONAL ISSUE: Connection leak
        return results
    
    # INTENTIONAL ISSUE: Inefficient query - missing index consideration
    def get_recent_orders(self, days: int = 30):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fixed: Using parameterized query to prevent SQL injection
        query = """
            SELECT o.id, o.total, u.username, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.created_at > datetime('now', '-' || ? || ' days')
            ORDER BY o.created_at DESC
        """
        
        cursor.execute(query, (days,))
        # INTENTIONAL ISSUE: Fetching all results at once - memory issue for large datasets
        return cursor.fetchall()
    
    # INTENTIONAL ISSUE: No input validation
    def create_user_unsafe(self, username: str, email: str, password: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fixed: Using parameterized query to prevent SQL injection
        query = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
        
        try:
            cursor.execute(query, (username, email, password))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            # INTENTIONAL ISSUE: Poor error handling, information disclosure
            raise Exception(f"Database error: {str(e)}")
        finally:
            # INTENTIONAL ISSUE: Only cursor closed, connection leaked
            cursor.close()
    
    # INTENTIONAL ISSUE: Blocking operation without timeout
    def get_user_stats(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Fixed: Using parameterized query to prevent SQL injection
        query = """
            SELECT 
                u.username,
                COUNT(DISTINCT o.id) as order_count,
                SUM(o.total) as total_spent,
                COUNT(DISTINCT r.id) as review_count,
                AVG(r.rating) as avg_rating
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN reviews r ON u.id = r.user_id
            WHERE u.id = ?
            GROUP BY u.id, u.username
        """
        
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        # INTENTIONAL ISSUE: Connection not closed
        return result

# INTENTIONAL ISSUE: Global database instance - thread safety issues
db_manager = DatabaseManager()

# INTENTIONAL ISSUE: Function with SQL injection vulnerability
def get_user_by_email(email: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fixed: Using parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE email = ?"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    
    # INTENTIONAL ISSUE: Connection not properly closed
    return user

# INTENTIONAL ISSUE: Database initialization with weak security
def initialize_database():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # INTENTIONAL ISSUE: No foreign key constraints, weak schema design
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Note: Default admin user should be created through proper setup process
    # with secure credentials provided via environment variables
    
    conn.commit()
    conn.close()

# INTENTIONAL ISSUE: Batch operation without proper transaction handling
def bulk_insert_products(products: List[Dict]):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Fixed: Using parameterized queries to prevent SQL injection
    for product in products:
        query = """
            INSERT INTO products (name, price, category) 
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (product['name'], product['price'], product['category']))
    
    conn.commit()
    # INTENTIONAL ISSUE: Connection not closed