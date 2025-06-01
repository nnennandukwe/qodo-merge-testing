"""
Database connection utilities and management.

This module provides centralized database connection handling,
connection pooling, and transaction management.
"""

import sqlite3
import psycopg2
import logging
from typing import Optional, Dict, Any, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    database: str
    user: str
    password: str
    port: int = 5432
    timeout: int = 30


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class DatabaseTransactionError(Exception):
    """Raised when database transaction fails."""
    pass


class DatabaseConnectionManager:
    """Manages database connections with proper error handling and cleanup."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config
        self.fallback_db_path = 'fallback.db'
        self.logger = logging.getLogger(__name__)
    
    def get_primary_connection(self) -> psycopg2.extensions.connection:
        """
        Get a PostgreSQL connection.
        
        Returns:
            PostgreSQL connection
            
        Raises:
            DatabaseConnectionError: If connection fails
        """
        if not self.config:
            raise DatabaseConnectionError("Database configuration not provided")
        
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                port=self.config.port,
                connect_timeout=self.config.timeout
            )
            return conn
        except psycopg2.Error as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            raise DatabaseConnectionError(f"Failed to connect to PostgreSQL: {e}")
    
    def get_fallback_connection(self) -> sqlite3.Connection:
        """
        Get a SQLite fallback connection.
        
        Returns:
            SQLite connection
            
        Raises:
            DatabaseConnectionError: If fallback connection fails
        """
        try:
            conn = sqlite3.connect(
                self.fallback_db_path,
                timeout=self.config.timeout if self.config else 30
            )
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"SQLite fallback connection failed: {e}")
            raise DatabaseConnectionError(f"Failed to connect to SQLite: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with automatic fallback.
        
        Tries PostgreSQL first, falls back to SQLite if unavailable.
        
        Returns:
            Database connection
            
        Raises:
            DatabaseConnectionError: If both connections fail
        """
        try:
            if self.config:
                return self.get_primary_connection()
            else:
                return self.get_fallback_connection()
        except DatabaseConnectionError:
            self.logger.warning("Primary database unavailable, using fallback")
            try:
                return self.get_fallback_connection()
            except DatabaseConnectionError as e:
                self.logger.error("Both primary and fallback connections failed")
                raise e
    
    @contextmanager
    def get_connection_context(self) -> ContextManager[sqlite3.Connection]:
        """
        Get a database connection as a context manager.
        
        Automatically handles connection cleanup.
        
        Yields:
            Database connection
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")
    
    @contextmanager
    def get_transaction_context(self) -> ContextManager[sqlite3.Connection]:
        """
        Get a database connection with transaction management.
        
        Automatically commits on success or rolls back on error.
        
        Yields:
            Database connection with transaction
            
        Raises:
            DatabaseTransactionError: If transaction fails
        """
        conn = None
        try:
            conn = self.get_connection()
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {rollback_error}")
            self.logger.error(f"Transaction failed: {e}")
            raise DatabaseTransactionError(f"Transaction failed: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")


def create_database_manager(config: Optional[Dict[str, Any]] = None) -> DatabaseConnectionManager:
    """
    Factory function to create a DatabaseConnectionManager.
    
    Args:
        config: Database configuration dictionary
        
    Returns:
        DatabaseConnectionManager instance
    """
    if config:
        db_config = DatabaseConfig(
            host=config.get('host', 'localhost'),
            database=config.get('database', 'testdb'),
            user=config.get('user', 'admin'),
            password=config.get('password', ''),
            port=config.get('port', 5432),
            timeout=config.get('timeout', 30)
        )
        return DatabaseConnectionManager(db_config)
    else:
        return DatabaseConnectionManager()


# Global database manager instance
default_db_manager = create_database_manager()