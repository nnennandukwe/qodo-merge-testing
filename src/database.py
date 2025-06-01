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
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            self.connections.append(conn)
            return conn
        except psycopg2.Error as e:
            # Log the PostgreSQL error and fall back to SQLite
            import logging
            logging.warning(f"PostgreSQL connection failed: {str(e)}, falling back to SQLite")
            try:
                return sqlite3.connect('fallback.db')
            except sqlite3.Error as sqlite_e:
                logging.error(f"SQLite connection also failed: {str(sqlite_e)}")
                raise Exception("Unable to establish database connection")
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in database connection: {str(e)}")
            raise Exception("Database connection error")
    
    def get_users_with_posts(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Use JOIN to solve N+1 problem
            query = """
                SELECT u.id, u.username, p.title
                FROM users u
                LEFT JOIN posts p ON u.id = p.user_id
                ORDER BY u.id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Group results by user
            result = {}
            for row in rows:
                user_id, username, post_title = row
                if user_id not in result:
                    result[user_id] = {
                        "id": user_id,
                        "username": username,
                        "posts": []
                    }
                if post_title:
                    result[user_id]["posts"].append(post_title)
            
            return list(result.values())
        except (psycopg2.Error, sqlite3.Error) as e:
            import logging
            logging.error(f"Database error in get_users_with_posts: {str(e)}")
            raise Exception("Failed to retrieve users with posts")
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in get_users_with_posts: {str(e)}")
            raise Exception("Failed to retrieve users with posts")
        finally:
            if conn:
                conn.close()
    
    def transfer_funds(self, from_account: int, to_account: int, amount: float):
        conn = None
        try:
            # Input validation
            if amount <= 0:
                raise ValueError("Transfer amount must be positive")
            if from_account == to_account:
                raise ValueError("Cannot transfer to the same account")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Start transaction
            conn.autocommit = False
            
            # Check if from_account has sufficient balance
            cursor.execute("SELECT balance FROM accounts WHERE id = %s", (from_account,))
            result = cursor.fetchone()
            if not result or result[0] < amount:
                raise ValueError("Insufficient funds")
            
            # Perform transfer with proper transaction handling
            cursor.execute(
                "UPDATE accounts SET balance = balance - %s WHERE id = %s",
                (amount, from_account)
            )
            
            cursor.execute(
                "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                (amount, to_account)
            )
            
            # Commit transaction
            conn.commit()
            return True
        except ValueError as e:
            if conn:
                conn.rollback()
            raise e
        except (psycopg2.Error, sqlite3.Error) as e:
            if conn:
                conn.rollback()
            import logging
            logging.error(f"Database error in transfer_funds: {str(e)}")
            raise Exception("Transfer failed due to database error")
        except Exception as e:
            if conn:
                conn.rollback()
            import logging
            logging.error(f"Unexpected error in transfer_funds: {str(e)}")
            raise Exception("Transfer failed")
        finally:
            if conn:
                conn.close()
    
    def search_products(self, search_term: str, category: str):
        conn = None
        try:
            # Input validation
            if not search_term or len(search_term.strip()) < 2:
                raise ValueError("Search term must be at least 2 characters")
            if not category or len(category.strip()) == 0:
                raise ValueError("Category cannot be empty")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Use parameterized query to prevent SQL injection
            query = """
                SELECT * FROM products 
                WHERE name LIKE %s 
                AND category = %s
                ORDER BY price
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, category))
            results = cursor.fetchall()
            return results
        except ValueError as e:
            raise e
        except (psycopg2.Error, sqlite3.Error) as e:
            import logging
            logging.error(f"Database error in search_products: {str(e)}")
            raise Exception("Product search failed")
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in search_products: {str(e)}")
            raise Exception("Product search failed")
        finally:
            if conn:
                conn.close()
    
    # INTENTIONAL ISSUE: Inefficient query - missing index consideration
    def get_recent_orders(self, days: int = 30):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # INTENTIONAL ISSUE: No index on created_at, inefficient for large tables
        query = f"""
            SELECT o.id, o.total, u.username, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.created_at > datetime('now', '-{days} days')
            ORDER BY o.created_at DESC
        """
        
        cursor.execute(query)
        # INTENTIONAL ISSUE: Fetching all results at once - memory issue for large datasets
        return cursor.fetchall()
    
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
    
    # INTENTIONAL ISSUE: Default admin user with weak credentials
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, email, password) 
        VALUES (1, 'admin', 'admin@example.com', 'admin123')
    ''')
    
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