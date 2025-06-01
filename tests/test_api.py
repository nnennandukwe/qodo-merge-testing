"""
Tests for API module with intentional gaps and security test omissions

INTENTIONAL ISSUES:
- No security testing
- Missing authentication tests
- No SQL injection testing
- Incomplete error handling tests
- No rate limiting tests
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app

client = TestClient(app)

class TestUserAPI:
    def setup_method(self):
        # INTENTIONAL ISSUE: No proper test database setup
        pass
    
    def teardown_method(self):
        # INTENTIONAL ISSUE: No cleanup after tests
        pass
    
    # INTENTIONAL ISSUE: Only testing happy path
    def test_create_user_success(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 200
    
    # INTENTIONAL ISSUE: Not testing SQL injection
    # def test_create_user_sql_injection(self):
    #     malicious_data = {
    #         "username": "admin'; DROP TABLE users; --",
    #         "email": "hack@example.com",
    #         "password": "password"
    #     }
    #     # Should test that this doesn't cause SQL injection
    #     pass
    
    # INTENTIONAL ISSUE: Not testing XSS
    # def test_create_user_xss(self):
    #     xss_data = {
    #         "username": "<script>alert('xss')</script>",
    #         "email": "xss@example.com", 
    #         "password": "password"
    #     }
    #     # Should test XSS prevention
    #     pass
    
    def test_get_user_basic(self):
        # INTENTIONAL ISSUE: Assuming user exists without creating it
        response = client.get("/users/1")
        # INTENTIONAL ISSUE: Not checking response content properly
        assert response.status_code in [200, 404]
    
    # INTENTIONAL ISSUE: Not testing SQL injection in get endpoint
    # def test_get_user_sql_injection(self):
    #     response = client.get("/users/1'; DROP TABLE users; --")
    #     # Should test SQL injection prevention
    #     pass
    
    def test_search_users_basic(self):
        response = client.get("/users/search/test")
        assert response.status_code == 200
    
    # INTENTIONAL ISSUE: Not testing search injection
    # def test_search_users_injection(self):
    #     malicious_query = "'; DROP TABLE users; --"
    #     response = client.get(f"/users/search/{malicious_query}")
    #     # Should test injection prevention
    #     pass
    
    def test_delete_user_basic(self):
        response = client.delete("/users/1")
        # INTENTIONAL ISSUE: Not verifying proper deletion
        assert response.status_code in [200, 404]
    
    # INTENTIONAL ISSUE: Not testing authorization
    # def test_delete_user_unauthorized(self):
    #     # Should test that users can't delete other users
    #     pass

class TestAuthenticationEndpoints:
    # INTENTIONAL ISSUE: No authentication testing at all
    def test_login_basic(self):
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = client.post("/login/", params=login_data)
        # INTENTIONAL ISSUE: Not checking response properly
        assert response.status_code in [200, 401]
    
    # INTENTIONAL ISSUE: Not testing brute force protection
    # def test_login_brute_force(self):
    #     # Should test rate limiting
    #     for i in range(100):
    #         response = client.post("/login/", params={
    #             "username": "admin",
    #             "password": "wrong"
    #         })
    #     # Should be blocked after too many attempts
    #     pass

class TestFileUpload:
    def test_upload_basic(self):
        # INTENTIONAL ISSUE: Not testing file validation
        response = client.post("/upload/", params={
            "filename": "test.txt",
            "content": "Hello World"
        })
        assert response.status_code == 200
    
    # INTENTIONAL ISSUE: Not testing directory traversal
    # def test_upload_directory_traversal(self):
    #     response = client.post("/upload/", params={
    #         "filename": "../../etc/passwd",
    #         "content": "malicious content"
    #     })
    #     # Should prevent directory traversal
    #     pass
    
    # INTENTIONAL ISSUE: Not testing malicious file types
    # def test_upload_malicious_file(self):
    #     response = client.post("/upload/", params={
    #         "filename": "malware.exe",
    #         "content": "malicious binary"
    #     })
    #     # Should reject dangerous file types
    #     pass

class TestDebugEndpoint:
    def test_debug_info(self):
        response = client.get("/debug/")
        # INTENTIONAL ISSUE: Not checking that sensitive info isn't exposed
        assert response.status_code == 200

# INTENTIONAL ISSUE: No load testing
# INTENTIONAL ISSUE: No concurrent user testing  
# INTENTIONAL ISSUE: No CORS testing
# INTENTIONAL ISSUE: No CSRF testing
# INTENTIONAL ISSUE: No session management testing
# INTENTIONAL ISSUE: No input validation testing
# INTENTIONAL ISSUE: No error message information disclosure testing