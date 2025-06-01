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

# INTENTIONAL ISSUE: Hardcoded database credentials
DB_CONFIG = {
    "host": "localhost",
    "database": "testdb",
    "user": "admin",
    "password": "password123"  # Hardcoded password!
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
    
    # OPTIMIZED: Fixed N+1 query problem with JOIN
    def get_users_with_posts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Single query with JOIN to get all data at once
        cursor.execute("""
            SELECT u.id, u.username, p.title
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            ORDER BY u.id
        """)
        rows = cursor.fetchall()
        
        # Group results by user
        users_dict = {}
        for row in rows:
            user_id, username, post_title = row
            if user_id not in users_dict:
                users_dict[user_id] = {
                    "id": user_id,
                    "username": username,
                    "posts": []
                }
            if post_title:
                users_dict[user_id]["posts"].append(post_title)
        
        result = list(users_dict.values())
        conn.close()  # Properly close connection
        return result
    
    # INTENTIONAL ISSUE: No transaction management
    def transfer_funds(self, from_account: int, to_account: int, amount: float):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # INTENTIONAL ISSUE: No transaction - if second update fails, data is inconsistent
        cursor.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE id = {from_account}")
        
        # Simulate potential failure point
        time.sleep(0.1)
        
        cursor.execute(f"UPDATE accounts SET balance = balance + {amount} WHERE id = {to_account}")
        
        conn.commit()
        # INTENTIONAL ISSUE: Connection not closed
    
    # INTENTIONAL ISSUE: SQL injection vulnerability
    def search_products(self, search_term: str, category: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Direct string interpolation - SQL injection risk!
        query = f"""
            SELECT * FROM products 
            WHERE name LIKE '%{search_term}%' 
            AND category = '{category}'
            ORDER BY price
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        # INTENTIONAL ISSUE: Connection leak
        return results
    
    # OPTIMIZED: Added proper indexing considerations and memory management
    def get_recent_orders(self, days: int = 30):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure proper indexes exist for performance
        self._ensure_indexes(conn)
        
        query = f"""
            SELECT o.id, o.total, u.username, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.created_at > datetime('now', '-{days} days')
            ORDER BY o.created_at DESC
            LIMIT 1000
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()  # Properly close connection
        return results
    
    def _ensure_indexes(self, conn):
        """Ensure necessary indexes exist for optimal performance"""
        cursor = conn.cursor()
        
        # Create indexes if they don't exist
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.commit()
        except Exception as e:
            # Silently handle if indexes already exist or other DB-specific issues
            pass
    
    # INTENTIONAL ISSUE: No input validation
    def create_user_unsafe(self, username: str, email: str, password: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # INTENTIONAL ISSUE: No validation, potential for malicious input
        query = f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{password}')"
        
        try:
            cursor.execute(query)
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
        
        # INTENTIONAL ISSUE: Complex query without timeout, can block indefinitely
        query = f"""
            SELECT 
                u.username,
                COUNT(DISTINCT o.id) as order_count,
                SUM(o.total) as total_spent,
                COUNT(DISTINCT r.id) as review_count,
                AVG(r.rating) as avg_rating
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN reviews r ON u.id = r.user_id
            WHERE u.id = {user_id}
            GROUP BY u.id, u.username
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        # INTENTIONAL ISSUE: Connection not closed
        return result

# INTENTIONAL ISSUE: Global database instance - thread safety issues
db_manager = DatabaseManager()

# INTENTIONAL ISSUE: Function with SQL injection vulnerability
def get_user_by_email(email: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Direct string formatting - SQL injection risk!
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    # INTENTIONAL ISSUE: Connection not properly closed
    return user

# OPTIMIZED: Database initialization with proper indexing and constraints
def initialize_database():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create tables with proper constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Create performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)")
    
    # Create orders table with proper indexing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
    
    conn.commit()
    conn.close()

# INTENTIONAL ISSUE: Batch operation without proper transaction handling
def bulk_insert_products(products: List[Dict]):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # INTENTIONAL ISSUE: No transaction, if one fails, partial data remains
    for product in products:
        query = f"""
            INSERT INTO products (name, price, category) 
            VALUES ('{product['name']}', {product['price']}, '{product['category']}')
        """
        cursor.execute(query)
    
    conn.commit()
    # INTENTIONAL ISSUE: Connection not closed