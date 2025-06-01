/**
 * UserForm component with intentional issues for Qodo Merge testing
 * 
 * INTENTIONAL ISSUES:
 * - Missing form validation
 * - Type safety problems
 * - Accessibility issues
 * - Performance anti-patterns
 * - Security vulnerabilities
 * - No error boundaries
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';

// INTENTIONAL ISSUE: No proper TypeScript interfaces
interface User {
  id?: number;
  username: string;
  email: string;
  password?: string;
}

// INTENTIONAL ISSUE: Any type usage
const UserForm: React.FC<{ onSubmit: (data: any) => void }> = ({ onSubmit }) => {
  // INTENTIONAL ISSUE: No initial state typing
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  // INTENTIONAL ISSUE: Storing sensitive data in state without protection
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState(''); // Storing API key in component state!
  
  // OPTIMIZED: Added dependency array and error handling
  useEffect(() => {
    axios.get('/api/users').then(response => {
      setUsers(response.data);
    }).catch(error => {
      console.error('Failed to fetch users:', error);
    });
  }, []); // Empty dependency array - only run once
  
  // OPTIMIZED: Proper immutable state updates with useCallback
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  }, []);
  
  // INTENTIONAL ISSUE: No form validation before submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // INTENTIONAL ISSUE: No client-side validation
      // INTENTIONAL ISSUE: Sending password in plain text
      const response = await axios.post('/api/users', {
        ...formData,
        apiKey: apiKey // Including API key in request body
      });
      
      // INTENTIONAL ISSUE: No success feedback to user
      onSubmit(response.data);
      
      // INTENTIONAL ISSUE: Not clearing sensitive data after submission
    } catch (error: any) {
      // INTENTIONAL ISSUE: Exposing full error details to user
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  // OPTIMIZED: Memoized user list rendering without XSS vulnerability
  const userList = useMemo(() => {
    return users.map((user: any) => (
      <div key={user.id}>
        {user.username} {/* Safe rendering without dangerouslySetInnerHTML */}
      </div>
    ));
  }, [users]);
  
  // INTENTIONAL ISSUE: No error boundary, will crash on errors
  return (
    <div className="user-form">
      <h2>User Registration</h2>
      
      {/* INTENTIONAL ISSUE: Missing accessibility attributes */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            // INTENTIONAL ISSUE: No required attribute, no validation
          />
        </div>
        
        <div>
          <label>Email:</label>
          <input
            type="text" // INTENTIONAL ISSUE: Should be type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            // INTENTIONAL ISSUE: No email validation
          />
        </div>
        
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            // INTENTIONAL ISSUE: No password strength requirements
            autoComplete="new-password" // INTENTIONAL ISSUE: Potential security issue
          />
        </div>
        
        <div>
          <label>Confirm Password:</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            // INTENTIONAL ISSUE: No password confirmation validation
          />
        </div>
        
        <div>
          {/* INTENTIONAL ISSUE: Exposing API key in form */}
          <label>API Key:</label>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
          />
        </div>
        
        {/* INTENTIONAL ISSUE: No loading state indication */}
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit'}
        </button>
      </form>
      
      {/* OPTIMIZED: Safe rendering of user data */}
      <div className="user-list">
        <h3>Existing Users:</h3>
        {userList}
      </div>
      
      {/* INTENTIONAL ISSUE: Debug information exposed in production */}
      <div style={{ display: 'block' }}>
        <h4>Debug Info:</h4>
        <pre>{JSON.stringify(formData, null, 2)}</pre>
        <p>API Key: {apiKey}</p>
      </div>
    </div>
  );
};

// OPTIMIZED: Wrapped with React.memo to prevent unnecessary re-renders
export default React.memo(UserForm);