/**
 * Utility functions and helpers for the frontend application.
 * 
 * This module contains reusable utility functions for common operations
 * like formatting, validation, API handling, and data manipulation.
 */

import { APIResponse, APIError, SortDirection, FormErrors } from '../types';

// String utilities
export const StringUtils = {
  /**
   * Capitalize the first letter of a string.
   */
  capitalize: (str: string): string => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },

  /**
   * Convert a string to title case.
   */
  toTitleCase: (str: string): string => {
    if (!str) return '';
    return str.replace(/\w\S*/g, (txt) => 
      txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
  },

  /**
   * Convert camelCase to human-readable format.
   */
  camelCaseToTitle: (str: string): string => {
    if (!str) return '';
    return str
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase())
      .trim();
  },

  /**
   * Truncate a string to a specified length.
   */
  truncate: (str: string, maxLength: number, suffix: string = '...'): string => {
    if (!str || str.length <= maxLength) return str;
    return str.slice(0, maxLength - suffix.length) + suffix;
  },

  /**
   * Generate a random string of specified length.
   */
  generateRandomString: (length: number = 8): string => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  },

  /**
   * Remove HTML tags from a string.
   */
  stripHtml: (str: string): string => {
    if (!str) return '';
    return str.replace(/<[^>]*>/g, '');
  }
};

// Number utilities
export const NumberUtils = {
  /**
   * Format a number with thousands separators.
   */
  formatNumber: (num: number, locale: string = 'en-US'): string => {
    return new Intl.NumberFormat(locale).format(num);
  },

  /**
   * Format a number as currency.
   */
  formatCurrency: (
    amount: number, 
    currency: string = 'USD', 
    locale: string = 'en-US'
  ): string => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency
    }).format(amount);
  },

  /**
   * Format a number as a percentage.
   */
  formatPercentage: (
    value: number, 
    decimals: number = 2, 
    locale: string = 'en-US'
  ): string => {
    return new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  },

  /**
   * Clamp a number between min and max values.
   */
  clamp: (value: number, min: number, max: number): number => {
    return Math.min(Math.max(value, min), max);
  },

  /**
   * Round a number to specified decimal places.
   */
  roundTo: (value: number, decimals: number = 2): number => {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
  }
};

// Date utilities
export const DateUtils = {
  /**
   * Format a date using Intl.DateTimeFormat.
   */
  formatDate: (
    date: Date | string, 
    options?: Intl.DateTimeFormatOptions,
    locale: string = 'en-US'
  ): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(locale, options).format(dateObj);
  },

  /**
   * Get relative time string (e.g., "2 hours ago").
   */
  getRelativeTime: (date: Date | string, locale: string = 'en-US'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

    if (diffInSeconds < 60) {
      return rtf.format(-diffInSeconds, 'second');
    } else if (diffInSeconds < 3600) {
      return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
    } else if (diffInSeconds < 86400) {
      return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
    } else if (diffInSeconds < 2592000) {
      return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
    } else if (diffInSeconds < 31536000) {
      return rtf.format(-Math.floor(diffInSeconds / 2592000), 'month');
    } else {
      return rtf.format(-Math.floor(diffInSeconds / 31536000), 'year');
    }
  },

  /**
   * Check if a date is today.
   */
  isToday: (date: Date | string): boolean => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const today = new Date();
    return dateObj.toDateString() === today.toDateString();
  },

  /**
   * Add days to a date.
   */
  addDays: (date: Date, days: number): Date => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  },

  /**
   * Get the start of day for a date.
   */
  startOfDay: (date: Date): Date => {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
  }
};

// Array utilities
export const ArrayUtils = {
  /**
   * Group array items by a key function.
   */
  groupBy: <T, K extends keyof any>(
    array: T[], 
    keyFn: (item: T) => K
  ): Record<K, T[]> => {
    return array.reduce((groups, item) => {
      const key = keyFn(item);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(item);
      return groups;
    }, {} as Record<K, T[]>);
  },

  /**
   * Sort array by multiple criteria.
   */
  sortBy: <T>(
    array: T[], 
    sortFns: Array<(item: T) => any>, 
    directions: SortDirection[] = []
  ): T[] => {
    return [...array].sort((a, b) => {
      for (let i = 0; i < sortFns.length; i++) {
        const aVal = sortFns[i](a);
        const bVal = sortFns[i](b);
        const direction = directions[i] || SortDirection.ASC;
        
        let comparison = 0;
        if (aVal > bVal) comparison = 1;
        if (aVal < bVal) comparison = -1;
        
        if (comparison !== 0) {
          return direction === SortDirection.ASC ? comparison : -comparison;
        }
      }
      return 0;
    });
  },

  /**
   * Remove duplicate items from array.
   */
  unique: <T>(array: T[], keyFn?: (item: T) => any): T[] => {
    if (!keyFn) {
      return [...new Set(array)];
    }
    
    const seen = new Set();
    return array.filter(item => {
      const key = keyFn(item);
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  },

  /**
   * Chunk array into smaller arrays of specified size.
   */
  chunk: <T>(array: T[], size: number): T[][] => {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  },

  /**
   * Shuffle array randomly.
   */
  shuffle: <T>(array: T[]): T[] => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }
};

// Object utilities
export const ObjectUtils = {
  /**
   * Deep merge two objects.
   */
  deepMerge: <T extends Record<string, any>>(target: T, source: Partial<T>): T => {
    const result = { ...target };
    
    for (const key in source) {
      if (source[key] !== null && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = ObjectUtils.deepMerge(result[key] || {}, source[key] as any);
      } else {
        result[key] = source[key] as any;
      }
    }
    
    return result;
  },

  /**
   * Deep clone an object.
   */
  deepClone: <T>(obj: T): T => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime()) as any;
    if (obj instanceof Array) return obj.map(item => ObjectUtils.deepClone(item)) as any;
    if (typeof obj === 'object') {
      const cloned = {} as any;
      for (const key in obj) {
        cloned[key] = ObjectUtils.deepClone(obj[key]);
      }
      return cloned;
    }
    return obj;
  },

  /**
   * Pick specific keys from an object.
   */
  pick: <T extends Record<string, any>, K extends keyof T>(
    obj: T, 
    keys: K[]
  ): Pick<T, K> => {
    const result = {} as Pick<T, K>;
    keys.forEach(key => {
      if (key in obj) {
        result[key] = obj[key];
      }
    });
    return result;
  },

  /**
   * Omit specific keys from an object.
   */
  omit: <T extends Record<string, any>, K extends keyof T>(
    obj: T, 
    keys: K[]
  ): Omit<T, K> => {
    const result = { ...obj };
    keys.forEach(key => {
      delete result[key];
    });
    return result;
  },

  /**
   * Check if an object is empty.
   */
  isEmpty: (obj: any): boolean => {
    if (obj == null) return true;
    if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0;
    if (typeof obj === 'object') return Object.keys(obj).length === 0;
    return false;
  }
};

// API utilities
export const APIUtils = {
  /**
   * Check if a response is successful.
   */
  isSuccessResponse: <T>(response: APIResponse<T>): response is APIResponse<T> & { success: true } => {
    return response.success === true;
  },

  /**
   * Extract error message from API response.
   */
  getErrorMessage: (response: APIResponse<any> | APIError): string => {
    if ('error' in response && response.error) {
      return response.error.message;
    }
    if ('message' in response) {
      return response.message;
    }
    return 'An unexpected error occurred';
  },

  /**
   * Build query string from parameters.
   */
  buildQueryString: (params: Record<string, any>): string => {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(item => searchParams.append(key, String(item)));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });
    
    return searchParams.toString();
  },

  /**
   * Create a debounced function for API calls.
   */
  debounce: <T extends (...args: any[]) => any>(
    func: T, 
    delay: number
  ): (...args: Parameters<T>) => void => {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  },

  /**
   * Create a throttled function for API calls.
   */
  throttle: <T extends (...args: any[]) => any>(
    func: T, 
    delay: number
  ): (...args: Parameters<T>) => void => {
    let isThrottled = false;
    
    return (...args: Parameters<T>) => {
      if (!isThrottled) {
        func(...args);
        isThrottled = true;
        setTimeout(() => {
          isThrottled = false;
        }, delay);
      }
    };
  }
};

// Form utilities
export const FormUtils = {
  /**
   * Extract form data from form element.
   */
  getFormData: (form: HTMLFormElement): Record<string, any> => {
    const formData = new FormData(form);
    const data: Record<string, any> = {};
    
    formData.forEach((value, key) => {
      if (data[key]) {
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    });
    
    return data;
  },

  /**
   * Validate form fields and return errors.
   */
  validateForm: <T extends Record<string, any>>(
    values: T,
    rules: Record<keyof T, (value: any) => string | null>
  ): FormErrors => {
    const errors: FormErrors = {};
    
    Object.entries(rules).forEach(([field, validator]) => {
      const error = validator(values[field]);
      if (error) {
        errors[field] = error;
      }
    });
    
    return errors;
  },

  /**
   * Check if form has any errors.
   */
  hasFormErrors: (errors: FormErrors): boolean => {
    return Object.values(errors).some(error => error != null && error !== '');
  },

  /**
   * Reset form errors.
   */
  resetFormErrors: (errors: FormErrors, fields?: string[]): FormErrors => {
    if (fields) {
      const newErrors = { ...errors };
      fields.forEach(field => {
        delete newErrors[field];
      });
      return newErrors;
    }
    return {};
  }
};

// Local storage utilities
export const StorageUtils = {
  /**
   * Set item in localStorage with JSON serialization.
   */
  setItem: (key: string, value: any): boolean => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
      return false;
    }
  },

  /**
   * Get item from localStorage with JSON parsing.
   */
  getItem: <T = any>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue ?? null;
    } catch (error) {
      console.error('Failed to read from localStorage:', error);
      return defaultValue ?? null;
    }
  },

  /**
   * Remove item from localStorage.
   */
  removeItem: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  },

  /**
   * Clear all items from localStorage.
   */
  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }
};

// URL utilities
export const URLUtils = {
  /**
   * Get query parameter value from URL.
   */
  getQueryParam: (param: string, url?: string): string | null => {
    const searchParams = new URLSearchParams(url ? new URL(url).search : window.location.search);
    return searchParams.get(param);
  },

  /**
   * Set query parameter in URL.
   */
  setQueryParam: (param: string, value: string, url?: string): string => {
    const targetUrl = url ? new URL(url) : new URL(window.location.href);
    targetUrl.searchParams.set(param, value);
    return targetUrl.toString();
  },

  /**
   * Remove query parameter from URL.
   */
  removeQueryParam: (param: string, url?: string): string => {
    const targetUrl = url ? new URL(url) : new URL(window.location.href);
    targetUrl.searchParams.delete(param);
    return targetUrl.toString();
  }
};

// Export all utilities
export {
  StringUtils,
  NumberUtils,
  DateUtils,
  ArrayUtils,
  ObjectUtils,
  APIUtils,
  FormUtils,
  StorageUtils,
  URLUtils
};