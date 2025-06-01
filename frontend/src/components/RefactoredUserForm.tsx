/**
 * Refactored UserForm component with improved code quality.
 * 
 * This component demonstrates:
 * - Proper TypeScript interfaces and types
 * - Form validation with clear error handling
 * - Separated validation logic and form state management
 * - Better accessibility and user experience
 * - Security best practices
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios, { CancelTokenSource } from 'axios';
import {
  User,
  UserCreateRequest,
  APIResponse,
  FormField,
  FormFieldType,
  FormState,
  FormErrors,
  LoadingState,
  ErrorState
} from '../types';
import { FormUtils, APIUtils, StringUtils } from '../utils';

interface UserFormProps {
  onSubmit: (userData: User) => void;
  onCancel?: () => void;
  initialValues?: Partial<UserCreateRequest>;
  submitButtonText?: string;
  showExistingUsers?: boolean;
  className?: string;
}

interface UserFormState extends FormState<UserCreateRequest> {
  users: User[];
  submitAttempted: boolean;
}

// Form field configuration
const USER_FORM_FIELDS: FormField[] = [
  {
    name: 'username',
    label: 'Username',
    type: FormFieldType.TEXT,
    required: true,
    placeholder: 'Enter username (3-30 characters)',
    helpText: 'Username can contain letters, numbers, underscores, and hyphens',
    validation: {
      required: true,
      minLength: 3,
      maxLength: 30,
      pattern: /^[a-zA-Z0-9_-]+$/,
      customValidator: (value: string) => {
        if (!value.match(/^[a-zA-Z0-9]/)) {
          return 'Username must start with a letter or number';
        }
        return null;
      }
    }
  },
  {
    name: 'email',
    label: 'Email Address',
    type: FormFieldType.EMAIL,
    required: true,
    placeholder: 'Enter your email address',
    helpText: 'We will never share your email with anyone else',
    validation: {
      required: true,
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      customValidator: (value: string) => {
        if (value && value.length > 254) {
          return 'Email address is too long';
        }
        return null;
      }
    }
  },
  {
    name: 'password',
    label: 'Password',
    type: FormFieldType.PASSWORD,
    required: true,
    placeholder: 'Enter a strong password',
    helpText: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character',
    validation: {
      required: true,
      minLength: 8,
      maxLength: 128,
      customValidator: (value: string) => {
        if (!value) return null;
        
        const errors = [];
        if (!/(?=.*[a-z])/.test(value)) {
          errors.push('one lowercase letter');
        }
        if (!/(?=.*[A-Z])/.test(value)) {
          errors.push('one uppercase letter');
        }
        if (!/(?=.*\d)/.test(value)) {
          errors.push('one number');
        }
        if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?])/.test(value)) {
          errors.push('one special character');
        }
        
        if (errors.length > 0) {
          return `Password must contain ${errors.join(', ')}`;
        }
        
        // Check for common weak passwords
        const commonPasswords = ['password', '123456', 'admin', 'qwerty', 'letmein'];
        if (commonPasswords.includes(value.toLowerCase())) {
          return 'This password is too common. Please choose a more secure password.';
        }
        
        return null;
      }
    }
  },
  {
    name: 'confirmPassword',
    label: 'Confirm Password',
    type: FormFieldType.PASSWORD,
    required: true,
    placeholder: 'Confirm your password',
    helpText: 'Enter the same password again',
    validation: {
      required: true,
      customValidator: (value: string, formValues?: UserCreateRequest) => {
        if (!value) return null;
        if (value !== formValues?.password) {
          return 'Passwords do not match';
        }
        return null;
      }
    }
  }
];

// Custom hooks for form management
const useFormValidation = (fields: FormField[], values: UserCreateRequest) => {
  const validateField = useCallback((field: FormField, value: any, allValues?: UserCreateRequest): string | null => {
    const validation = field.validation;
    if (!validation) return null;

    // Required validation
    if (validation.required && (!value || String(value).trim() === '')) {
      return `${field.label} is required`;
    }

    if (!value) return null; // Skip other validations if value is empty

    const stringValue = String(value);

    // Length validation
    if (validation.minLength && stringValue.length < validation.minLength) {
      return `${field.label} must be at least ${validation.minLength} characters`;
    }

    if (validation.maxLength && stringValue.length > validation.maxLength) {
      return `${field.label} cannot exceed ${validation.maxLength} characters`;
    }

    // Pattern validation
    if (validation.pattern && !validation.pattern.test(stringValue)) {
      return `${field.label} format is invalid`;
    }

    // Custom validation
    if (validation.customValidator) {
      return validation.customValidator(value, allValues);
    }

    return null;
  }, []);

  const validateForm = useCallback((formValues: UserCreateRequest): FormErrors => {
    const errors: FormErrors = {};

    fields.forEach(field => {
      const error = validateField(field, (formValues as any)[field.name], formValues);
      if (error) {
        errors[field.name] = error;
      }
    });

    return errors;
  }, [fields, validateField]);

  const validateSingleField = useCallback((fieldName: string, value: any): string | null => {
    const field = fields.find(f => f.name === fieldName);
    if (!field) return null;

    return validateField(field, value, values);
  }, [fields, validateField, values]);

  return {
    validateForm,
    validateSingleField
  };
};

const useUserFormState = (initialValues: Partial<UserCreateRequest> = {}) => {
  const [state, setState] = useState<UserFormState>({
    values: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      ...initialValues
    },
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: false,
    isDirty: false,
    users: [],
    submitAttempted: false
  });

  const updateState = useCallback((updates: Partial<UserFormState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const updateField = useCallback((name: string, value: any) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, [name]: value },
      touched: { ...prev.touched, [name]: true },
      isDirty: true
    }));
  }, []);

  const updateFieldError = useCallback((name: string, error: string | null) => {
    setState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [name]: error || undefined
      }
    }));
  }, []);

  const resetForm = useCallback(() => {
    setState(prev => ({
      ...prev,
      values: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        ...initialValues
      },
      errors: {},
      touched: {},
      isDirty: false,
      submitAttempted: false
    }));
  }, [initialValues]);

  return {
    state,
    updateState,
    updateField,
    updateFieldError,
    resetForm
  };
};

const useExistingUsers = (shouldFetch: boolean) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    if (!shouldFetch) return;

    try {
      setLoading(true);
      setError(null);

      const response = await axios.get<APIResponse<User[]>>('/api/users', {
        timeout: 5000
      });

      if (APIUtils.isSuccessResponse(response.data)) {
        setUsers(response.data.data || []);
      } else {
        throw new Error(APIUtils.getErrorMessage(response.data));
      }
    } catch (error: any) {
      if (!axios.isCancel(error)) {
        setError(error.message || 'Failed to load existing users');
        console.error('Failed to fetch users:', error);
      }
    } finally {
      setLoading(false);
    }
  }, [shouldFetch]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, loading, error, refetch: fetchUsers };
};

// Form field components
const FormFieldComponent: React.FC<{
  field: FormField;
  value: any;
  error?: string;
  touched?: boolean;
  disabled?: boolean;
  onChange: (name: string, value: any) => void;
  onBlur: (name: string) => void;
}> = ({ field, value, error, touched, disabled, onChange, onBlur }) => {
  const fieldId = `field-${field.name}`;
  const errorId = `${fieldId}-error`;
  const helpId = `${fieldId}-help`;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(field.name, e.target.value);
  };

  const handleBlur = () => {
    onBlur(field.name);
  };

  return (
    <div className="form-field">
      <label htmlFor={fieldId} className="form-label">
        {field.label}
        {field.required && <span className="required-indicator" aria-label="required">*</span>}
      </label>
      
      <input
        id={fieldId}
        type={field.type}
        name={field.name}
        value={value || ''}
        placeholder={field.placeholder}
        disabled={disabled}
        required={field.required}
        className={`form-input ${error && touched ? 'error' : ''}`}
        onChange={handleChange}
        onBlur={handleBlur}
        aria-invalid={error && touched ? 'true' : 'false'}
        aria-describedby={`${error && touched ? errorId : ''} ${field.helpText ? helpId : ''}`.trim()}
        autoComplete={field.type === FormFieldType.PASSWORD ? 'new-password' : 'on'}
      />

      {field.helpText && (
        <div id={helpId} className="form-help-text">
          {field.helpText}
        </div>
      )}

      {error && touched && (
        <div id={errorId} className="form-error" role="alert">
          {error}
        </div>
      )}
    </div>
  );
};

const ExistingUsersList: React.FC<{ users: User[]; loading: boolean; error: string | null }> = ({
  users,
  loading,
  error
}) => {
  if (loading) {
    return (
      <div className="existing-users-loading" aria-live="polite">
        Loading existing users...
      </div>
    );
  }

  if (error) {
    return (
      <div className="existing-users-error" role="alert">
        Failed to load existing users
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="existing-users-empty">
        No existing users found
      </div>
    );
  }

  return (
    <div className="existing-users-list">
      <h3>Existing Users</h3>
      <div className="users-grid" role="list">
        {users.slice(0, 10).map(user => (
          <div key={user.id} className="user-item" role="listitem">
            <div className="user-name">{StringUtils.truncate(user.username, 20)}</div>
            <div className="user-email">{StringUtils.truncate(user.email, 30)}</div>
          </div>
        ))}
        {users.length > 10 && (
          <div className="more-users">
            +{users.length - 10} more users
          </div>
        )}
      </div>
    </div>
  );
};

// Main component
const RefactoredUserForm: React.FC<UserFormProps> = ({
  onSubmit,
  onCancel,
  initialValues = {},
  submitButtonText = 'Create User',
  showExistingUsers = false,
  className = ''
}) => {
  const {
    state,
    updateState,
    updateField,
    updateFieldError,
    resetForm
  } = useUserFormState(initialValues);

  const { validateForm, validateSingleField } = useFormValidation(USER_FORM_FIELDS, state.values);
  const { users, loading: usersLoading, error: usersError } = useExistingUsers(showExistingUsers);

  // Update form validity when values or errors change
  useEffect(() => {
    const errors = validateForm(state.values);
    const isValid = !FormUtils.hasFormErrors(errors);
    
    updateState({
      errors,
      isValid
    });
  }, [state.values, validateForm, updateState]);

  const handleFieldChange = useCallback((name: string, value: any) => {
    updateField(name, value);

    // Clear field error when user starts typing
    if (state.errors[name]) {
      updateFieldError(name, null);
    }

    // Validate confirm password when password changes
    if (name === 'password' && state.values.confirmPassword) {
      const confirmPasswordError = validateSingleField('confirmPassword', state.values.confirmPassword);
      updateFieldError('confirmPassword', confirmPasswordError);
    }
  }, [updateField, updateFieldError, validateSingleField, state.errors, state.values.confirmPassword]);

  const handleFieldBlur = useCallback((name: string) => {
    if (!state.touched[name]) {
      updateState({
        touched: { ...state.touched, [name]: true }
      });
    }

    // Validate field on blur
    const error = validateSingleField(name, (state.values as any)[name]);
    updateFieldError(name, error);
  }, [state.touched, state.values, validateSingleField, updateFieldError, updateState]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched and attempt submitted
    const allTouched = USER_FORM_FIELDS.reduce((acc, field) => {
      acc[field.name] = true;
      return acc;
    }, {} as { [key: string]: boolean });

    updateState({
      touched: allTouched,
      submitAttempted: true
    });

    // Validate form
    const errors = validateForm(state.values);
    const isValid = !FormUtils.hasFormErrors(errors);

    if (!isValid) {
      updateState({ errors });
      return;
    }

    try {
      updateState({ isSubmitting: true });

      const response = await axios.post<APIResponse<User>>('/api/users', {
        username: state.values.username.trim(),
        email: state.values.email.trim().toLowerCase(),
        password: state.values.password
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (APIUtils.isSuccessResponse(response.data)) {
        onSubmit(response.data.data!);
        resetForm();
      } else {
        throw new Error(APIUtils.getErrorMessage(response.data));
      }
    } catch (error: any) {
      let errorMessage = 'An unexpected error occurred. Please try again.';

      if (error.response?.status === 400) {
        errorMessage = error.response.data?.message || 'Invalid form data. Please check your inputs.';
      } else if (error.response?.status === 409) {
        errorMessage = 'Username or email already exists.';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      }

      updateState({
        errors: { general: errorMessage }
      });
    } finally {
      updateState({ isSubmitting: false });
    }
  }, [state.values, state.touched, validateForm, updateState, onSubmit, resetForm]);

  const isFormDisabled = state.isSubmitting;

  return (
    <div className={`refactored-user-form ${className}`}>
      <div className="form-container">
        <h2>User Registration</h2>

        {state.errors.general && (
          <div className="form-general-error" role="alert">
            {state.errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {USER_FORM_FIELDS.map(field => (
            <FormFieldComponent
              key={field.name}
              field={field}
              value={(state.values as any)[field.name]}
              error={state.errors[field.name]}
              touched={state.touched[field.name] || state.submitAttempted}
              disabled={isFormDisabled}
              onChange={handleFieldChange}
              onBlur={handleFieldBlur}
            />
          ))}

          <div className="form-actions">
            <button
              type="submit"
              disabled={isFormDisabled || !state.isValid}
              className="submit-button"
              aria-describedby={!state.isValid ? 'form-validation-summary' : undefined}
            >
              {state.isSubmitting ? 'Creating...' : submitButtonText}
            </button>

            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={isFormDisabled}
                className="cancel-button"
              >
                Cancel
              </button>
            )}
          </div>

          {!state.isValid && state.submitAttempted && (
            <div id="form-validation-summary" className="form-validation-summary" role="alert">
              Please correct the errors above before submitting.
            </div>
          )}
        </form>
      </div>

      {showExistingUsers && (
        <div className="existing-users-section">
          <ExistingUsersList
            users={users}
            loading={usersLoading}
            error={usersError}
          />
        </div>
      )}

      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <details>
            <summary>Form Debug Information</summary>
            <pre>
              {JSON.stringify({
                values: state.values,
                errors: state.errors,
                touched: state.touched,
                isValid: state.isValid,
                isDirty: state.isDirty,
                isSubmitting: state.isSubmitting,
                submitAttempted: state.submitAttempted
              }, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default React.memo(RefactoredUserForm);