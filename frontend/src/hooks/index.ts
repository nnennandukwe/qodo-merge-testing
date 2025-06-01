/**
 * Custom React hooks for common functionality.
 * 
 * This module contains reusable custom hooks that encapsulate
 * common patterns and logic for React components.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios, { CancelTokenSource } from 'axios';
import { APIResponse, LoadingState, ErrorState } from '../types';
import { APIUtils, StorageUtils } from '../utils';

// API Hooks
export const useAPICall = <T>(
  apiCall: () => Promise<APIResponse<T>>,
  dependencies: any[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<LoadingState>({ isLoading: false });
  const [error, setError] = useState<ErrorState>({ hasError: false });
  const cancelTokenRef = useRef<CancelTokenSource | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading({ isLoading: true });
      setError({ hasError: false });

      // Cancel previous request
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('New request initiated');
      }

      // Create new cancel token
      cancelTokenRef.current = axios.CancelToken.source();

      const response = await apiCall();

      if (APIUtils.isSuccessResponse(response)) {
        setData(response.data!);
      } else {
        throw new Error(APIUtils.getErrorMessage(response));
      }
    } catch (error: any) {
      if (!axios.isCancel(error)) {
        setError({
          hasError: true,
          error: error.message || 'An error occurred'
        });
      }
    } finally {
      setLoading({ isLoading: false });
    }
  }, dependencies);

  useEffect(() => {
    execute();

    return () => {
      if (cancelTokenRef.current) {
        cancelTokenRef.current.cancel('Component unmounted');
      }
    };
  }, [execute]);

  const retry = useCallback(() => {
    execute();
  }, [execute]);

  return {
    data,
    loading: loading.isLoading,
    error: error.hasError ? error.error : null,
    retry,
    execute
  };
};

// Local Storage Hook
export const useLocalStorage = <T>(
  key: string,
  defaultValue: T
): [T, (value: T) => void, () => void] => {
  const [value, setValue] = useState<T>(() => {
    return StorageUtils.getItem(key, defaultValue);
  });

  const setStoredValue = useCallback((newValue: T) => {
    setValue(newValue);
    StorageUtils.setItem(key, newValue);
  }, [key]);

  const removeStoredValue = useCallback(() => {
    setValue(defaultValue);
    StorageUtils.removeItem(key);
  }, [key, defaultValue]);

  return [value, setStoredValue, removeStoredValue];
};

// Debounced Value Hook
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Previous Value Hook
export const usePrevious = <T>(value: T): T | undefined => {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  });

  return ref.current;
};

// Window Size Hook
export const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

// Online Status Hook
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};

// Focus Trap Hook
export const useFocusTrap = (isActive: boolean) => {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isActive || !ref.current) return;

    const element = ref.current;
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    const handleEscapeKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // Handle escape key - could call a callback here
      }
    };

    document.addEventListener('keydown', handleTabKey);
    document.addEventListener('keydown', handleEscapeKey);

    // Focus first element when trap becomes active
    firstElement?.focus();

    return () => {
      document.removeEventListener('keydown', handleTabKey);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isActive]);

  return ref;
};

// Click Outside Hook
export const useClickOutside = <T extends HTMLElement>(
  callback: () => void,
  enabled: boolean = true
) => {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!enabled) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [callback, enabled]);

  return ref;
};

// Intersection Observer Hook
export const useIntersectionObserver = (
  options: IntersectionObserverInit = {}
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
      setEntry(entry);
    }, options);

    observer.observe(ref.current);

    return () => observer.disconnect();
  }, [options]);

  return { ref, isIntersecting, entry };
};

// Form Validation Hook
export const useFormValidation = <T extends Record<string, any>>(
  initialValues: T,
  validationRules: Record<keyof T, (value: any, formValues: T) => string | null>
) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<keyof T, string | null>>({} as any);
  const [touched, setTouched] = useState<Record<keyof T, boolean>>({} as any);

  const validateField = useCallback((name: keyof T, value: any) => {
    const validator = validationRules[name];
    if (validator) {
      const error = validator(value, values);
      setErrors(prev => ({ ...prev, [name]: error }));
      return error;
    }
    return null;
  }, [validationRules, values]);

  const validateForm = useCallback(() => {
    const newErrors: Record<keyof T, string | null> = {} as any;
    let isValid = true;

    Object.keys(validationRules).forEach(key => {
      const error = validationRules[key as keyof T](values[key as keyof T], values);
      newErrors[key as keyof T] = error;
      if (error) isValid = false;
    });

    setErrors(newErrors);
    return isValid;
  }, [validationRules, values]);

  const handleChange = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name, value);
  }, [validateField]);

  const handleBlur = useCallback((name: keyof T) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name, values[name]);
  }, [validateField, values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({} as any);
    setTouched({} as any);
  }, [initialValues]);

  const isValid = useMemo(() => {
    return Object.values(errors).every(error => !error);
  }, [errors]);

  const isDirty = useMemo(() => {
    return Object.keys(touched).some(key => touched[key as keyof T]);
  }, [touched]);

  return {
    values,
    errors,
    touched,
    isValid,
    isDirty,
    handleChange,
    handleBlur,
    validateForm,
    reset,
    setValues,
    setErrors
  };
};

// Async Operation Hook
export const useAsyncOperation = <T, P extends any[]>(
  asyncFunction: (...params: P) => Promise<T>
) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const execute = useCallback(async (...params: P) => {
    try {
      setLoading(true);
      setError(null);
      const result = await asyncFunction(...params);
      setData(result);
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [asyncFunction]);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    execute,
    loading,
    error,
    data,
    reset
  };
};

// Export all hooks
export {
  useAPICall,
  useLocalStorage,
  useDebounce,
  usePrevious,
  useWindowSize,
  useOnlineStatus,
  useFocusTrap,
  useClickOutside,
  useIntersectionObserver,
  useFormValidation,
  useAsyncOperation
};