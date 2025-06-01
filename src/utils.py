"""
Utility functions with intentional issues for Qodo Merge testing

INTENTIONAL ISSUES:
- Unsafe file operations
- No input validation
- Memory leaks
- Poor error handling
- Security vulnerabilities
"""

import os
import pickle
import json
import subprocess
import tempfile
from typing import Any, Dict, List
import requests

# INTENTIONAL ISSUE: Global cache that grows without bounds
file_cache = {}
request_cache = {}

# INTENTIONAL ISSUE: Unsafe file operations
def read_file_unsafe(file_path: str) -> str:
    # INTENTIONAL ISSUE: No path validation - directory traversal vulnerability
    with open(file_path, 'r') as f:
        content = f.read()
    
    # INTENTIONAL ISSUE: Memory leak - cache grows indefinitely
    file_cache[file_path] = content
    return content

# INTENTIONAL ISSUE: Unsafe pickle usage
def save_object(obj: Any, filename: str) -> None:
    # INTENTIONAL ISSUE: Pickle is unsafe for untrusted data
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def load_object(filename: str) -> Any:
    # INTENTIONAL ISSUE: No validation before unpickling
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Can execute arbitrary code!

# INTENTIONAL ISSUE: Command injection vulnerability
def execute_command(command: str) -> str:
    # INTENTIONAL ISSUE: Direct command execution without sanitization
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# INTENTIONAL ISSUE: Unsafe file creation
def create_temp_file(content: str, filename: str = None) -> str:
    if filename:
        # INTENTIONAL ISSUE: User-controlled filename without validation
        file_path = f"/tmp/{filename}"
    else:
        file_path = tempfile.mktemp()
    
    # INTENTIONAL ISSUE: No permission checks
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path

# INTENTIONAL ISSUE: No input validation
def process_json_data(json_string: str) -> Dict:
    try:
        data = json.loads(json_string)
        # INTENTIONAL ISSUE: No validation of loaded data structure
        return data
    except:
        # INTENTIONAL ISSUE: Silent failure
        return {}

# INTENTIONAL ISSUE: Unsafe HTTP requests
def fetch_url(url: str) -> str:
    # INTENTIONAL ISSUE: No URL validation, SSRF vulnerability
    try:
        response = requests.get(url, timeout=30)
        
        # INTENTIONAL ISSUE: Memory leak - storing all responses
        request_cache[url] = response.text
        
        return response.text
    except:
        # INTENTIONAL ISSUE: Poor error handling
        return ""

# INTENTIONAL ISSUE: Inefficient algorithm
def bubble_sort(arr: List[int]) -> List[int]:
    # INTENTIONAL ISSUE: O(n²) when better algorithms exist
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# INTENTIONAL ISSUE: Memory inefficient string operations
def process_large_text(text: str) -> str:
    result = ""
    # INTENTIONAL ISSUE: String concatenation in loop - inefficient
    for char in text:
        if char.isalnum():
            result += char.upper()  # Creates new string each time
    return result

# INTENTIONAL ISSUE: Unsafe eval usage
def calculate_dynamic(expression: str) -> float:
    # INTENTIONAL ISSUE: eval with user input
    try:
        return eval(expression)
    except:
        return 0.0

# INTENTIONAL ISSUE: No rate limiting or caching for expensive operations
def expensive_calculation(n: int) -> int:
    # INTENTIONAL ISSUE: Expensive recursive operation without memoization
    if n <= 1:
        return 1
    return expensive_calculation(n - 1) + expensive_calculation(n - 2)

# INTENTIONAL ISSUE: Unsafe environment variable access
def get_config_value(key: str) -> str:
    # INTENTIONAL ISSUE: No validation, potential information disclosure
    return os.environ.get(key, "")

# INTENTIONAL ISSUE: Logging sensitive information
def log_user_action(user_id: int, action: str, data: Dict) -> None:
    import logging
    
    # INTENTIONAL ISSUE: Logging potentially sensitive data
    logging.info(f"User {user_id} performed {action}: {data}")

# INTENTIONAL ISSUE: No input sanitization for file operations
def write_log_file(log_data: str, filename: str) -> None:
    # INTENTIONAL ISSUE: Filename not validated
    log_path = f"logs/{filename}"
    
    # INTENTIONAL ISSUE: No directory traversal protection
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a') as f:
        f.write(log_data + '\n')

# INTENTIONAL ISSUE: Hardcoded paths and credentials
CONFIG_FILE = "/etc/app/config.json"
DEFAULT_PASSWORD = "changeme123"
API_ENDPOINT = "http://api.internal.company.com"

# INTENTIONAL ISSUE: Global state modification
def update_global_config(key: str, value: Any) -> None:
    global file_cache
    # INTENTIONAL ISSUE: Modifying global state without synchronization
    file_cache[f"config_{key}"] = value

# INTENTIONAL ISSUE: Resource leak
def process_files_in_directory(directory: str) -> List[str]:
    results = []
    
    # INTENTIONAL ISSUE: Opening files without proper cleanup
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            f = open(file_path, 'r')  # File handle never closed!
            content = f.read()
            results.append(content)
    
    return results

# INTENTIONAL ISSUE: Unsafe regular expression
def validate_input(user_input: str) -> bool:
    import re
    
    # INTENTIONAL ISSUE: ReDoS vulnerability with catastrophic backtracking
    pattern = r'^(a+)+$'
    return bool(re.match(pattern, user_input))

# INTENTIONAL ISSUE: Time-based information disclosure
def check_user_exists(username: str) -> bool:
    import time
    
    # INTENTIONAL ISSUE: Different response times reveal information
    if username == "admin":
        time.sleep(0.1)  # Simulate database lookup
        return True
    elif username.startswith("user_"):
        time.sleep(0.05)  # Different timing
        return True
    else:
        return False