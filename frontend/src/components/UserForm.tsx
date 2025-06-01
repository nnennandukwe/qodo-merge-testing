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

import React, { useState, useEffect } from 'react';
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
  
  // INTENTIONAL ISSUE: No cleanup, potential memory leak
  useEffect(() => {
    // INTENTIONAL ISSUE: No error handling for failed requests
    axios.get('/api/users').then(response => {
      setUsers(response.data);
    });
    
    // INTENTIONAL ISSUE: Missing dependency array causes infinite re-renders
  });
  
  // INTENTIONAL ISSUE: No input validation
  const handleInputChange = (e: any) => {
    const { name, value } = e.target;
    
    // INTENTIONAL ISSUE: Direct state mutation
    formData[name] = value;
    setFormData(formData);
  };
  
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
  
  // INTENTIONAL ISSUE: Unsafe innerHTML usage
  const renderUserList = () => {
    return users.map((user: any) => (
      <div 
        key={user.id} 
        // INTENTIONAL ISSUE: XSS vulnerability
        dangerouslySetInnerHTML={{ __html: user.username }}
      />
    ));
  };
  
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
      
      {/* INTENTIONAL ISSUE: Rendering user data without proper escaping */}
      <div className="user-list">
        <h3>Existing Users:</h3>
        {renderUserList()}
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

// INTENTIONAL ISSUE: Component not properly memoized, will re-render unnecessarily
export default UserForm;