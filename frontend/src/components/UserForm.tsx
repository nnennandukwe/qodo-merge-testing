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
import ErrorBoundary from './ErrorBoundary';

interface User {
  id?: number;
  username: string;
  email: string;
}

interface FormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface UserFormProps {
  onSubmit: (data: User) => void;
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

const UserForm: React.FC<UserFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitted, setSubmitted] = useState(false);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/users', { timeout: 5000 });
        if (isMounted && Array.isArray(response.data)) {
          setUsers(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch users:', error);
        // Don't set error state for background operations
      }
    };
    
    fetchUsers();
    
    return () => {
      isMounted = false;
    };
  }, []);
  
  const validateField = useCallback((name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'username':
        if (!value.trim()) return 'Username is required';
        if (value.length < 3) return 'Username must be at least 3 characters';
        if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Username can only contain letters, numbers, and underscores';
        break;
      case 'email':
        if (!value.trim()) return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
        break;
      case 'password':
        if (!value) return 'Password is required';
        if (value.length < 6) return 'Password must be at least 6 characters';
        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          return 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
        }
        break;
      case 'confirmPassword':
        if (!value) return 'Please confirm your password';
        if (value !== formData.password) return 'Passwords do not match';
        break;
    }
    return undefined;
  }, [formData.password]);
  
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const fieldName = name as keyof FormData;
    
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
    
    // Validate confirm password when password changes
    if (fieldName === 'password' && formData.confirmPassword) {
      const confirmPasswordError = validateField('confirmPassword', formData.confirmPassword);
      setErrors(prev => ({
        ...prev,
        confirmPassword: confirmPasswordError
      }));
    }
  }, [errors, formData.confirmPassword, validateField]);
  
  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};
    
    Object.keys(formData).forEach((key) => {
      const fieldName = key as keyof FormData;
      const error = validateField(fieldName, formData[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData, validateField]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const userData = {
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password
      };
      
      const response = await axios.post('/api/users', userData, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // Clear form on success
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      });
      setSubmitted(false);
      
      onSubmit(response.data);
      
    } catch (error: any) {
      console.error('Form submission error:', error);
      
      if (error.response?.status === 400) {
        setErrors({ general: error.response.data.detail || 'Invalid form data. Please check your inputs.' });
      } else if (error.response?.status === 409) {
        setErrors({ general: 'Username or email already exists.' });
      } else if (error.code === 'ECONNABORTED') {
        setErrors({ general: 'Request timed out. Please try again.' });
      } else {
        setErrors({ general: 'An unexpected error occurred. Please try again later.' });
      }
    } finally {
      setLoading(false);
    }
  };
  
  const renderUserList = useMemo(() => {
    return users.map((user: User) => (
      <div key={user.id} style={{ padding: '4px 0' }}>
        <strong>{user.username}</strong> - {user.email}
      </div>
    ));
  }, [users]);
  
  return (
    <ErrorBoundary>
      <div className="user-form">
        <h2>User Registration</h2>
        
        {errors.general && (
          <div style={{ color: '#d63031', marginBottom: '16px', padding: '8px', backgroundColor: '#ffe0e0', borderRadius: '4px' }}>
            {errors.general}
          </div>
        )}
        
        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="username" style={{ display: 'block', marginBottom: '4px' }}>Username:</label>
            <input
              id="username"
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              aria-invalid={errors.username ? 'true' : 'false'}
              aria-describedby={errors.username ? 'username-error' : undefined}
              style={{
                borderColor: errors.username ? '#d63031' : '#ddd',
                padding: '8px',
                width: '100%',
                maxWidth: '300px'
              }}
            />
            {errors.username && (
              <div id="username-error" style={{ color: '#d63031', fontSize: '14px', marginTop: '4px' }}>
                {errors.username}
              </div>
            )}
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="email" style={{ display: 'block', marginBottom: '4px' }}>Email:</label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'email-error' : undefined}
              style={{
                borderColor: errors.email ? '#d63031' : '#ddd',
                padding: '8px',
                width: '100%',
                maxWidth: '300px'
              }}
            />
            {errors.email && (
              <div id="email-error" style={{ color: '#d63031', fontSize: '14px', marginTop: '4px' }}>
                {errors.email}
              </div>
            )}
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '4px' }}>Password:</label>
            <input
              id="password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              autoComplete="new-password"
              aria-invalid={errors.password ? 'true' : 'false'}
              aria-describedby={errors.password ? 'password-error' : undefined}
              style={{
                borderColor: errors.password ? '#d63031' : '#ddd',
                padding: '8px',
                width: '100%',
                maxWidth: '300px'
              }}
            />
            {errors.password && (
              <div id="password-error" style={{ color: '#d63031', fontSize: '14px', marginTop: '4px' }}>
                {errors.password}
              </div>
            )}
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '4px' }}>Confirm Password:</label>
            <input
              id="confirmPassword"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              autoComplete="new-password"
              aria-invalid={errors.confirmPassword ? 'true' : 'false'}
              aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
              style={{
                borderColor: errors.confirmPassword ? '#d63031' : '#ddd',
                padding: '8px',
                width: '100%',
                maxWidth: '300px'
              }}
            />
            {errors.confirmPassword && (
              <div id="confirm-password-error" style={{ color: '#d63031', fontSize: '14px', marginTop: '4px' }}>
                {errors.confirmPassword}
              </div>
            )}
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            style={{
              padding: '12px 24px',
              backgroundColor: loading ? '#ccc' : '#74b9ff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </form>
        
        {users.length > 0 && (
          <div className="user-list" style={{ marginTop: '32px' }}>
            <h3>Existing Users:</h3>
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {renderUserList}
            </div>
          </div>
        )}
        
        {process.env.NODE_ENV === 'development' && (
          <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
            <h4>Debug Info:</h4>
            <p>Form submitted: {submitted ? 'Yes' : 'No'}</p>
            <p>Loading: {loading ? 'Yes' : 'No'}</p>
            <p>Errors: {Object.keys(errors).length}</p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default React.memo(UserForm);