/**
 * Validation utilities with intentional security and logic issues
 * 
 * INTENTIONAL ISSUES:
 * - Weak validation patterns
 * - ReDoS vulnerabilities
 * - Information disclosure
 * - Poor type safety
 * - Logic errors
 */

export interface ValidationResult {
  isValid: boolean;
  errors?: string[];
  warnings?: string[];
}

export interface FormValidationResult {
  isValid: boolean;
  fieldErrors: Record<string, string>;
  generalErrors: string[];
}

export function validateEmail(email: string): ValidationResult {
  const errors: string[] = [];
  
  if (!email || typeof email !== 'string') {
    errors.push('Email is required');
    return { isValid: false, errors };
  }
  
  const trimmedEmail = email.trim();
  
  if (trimmedEmail.length === 0) {
    errors.push('Email cannot be empty');
  } else if (trimmedEmail.length > 254) {
    errors.push('Email is too long');
  } else {
    // RFC 5322 compliant email regex (simplified but secure)
    const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    
    if (!emailRegex.test(trimmedEmail)) {
      errors.push('Please enter a valid email address');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validateComplexPattern(input: string): ValidationResult {
  const errors: string[] = [];
  
  if (!input || typeof input !== 'string') {
    errors.push('Input is required');
    return { isValid: false, errors };
  }
  
  // Safe regex pattern without catastrophic backtracking
  const pattern = /^[a]+$/;
  
  if (input.length > 1000) {
    errors.push('Input is too long');
  } else if (!pattern.test(input)) {
    errors.push('Input must contain only the letter "a"');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validatePassword(password: string): ValidationResult {
  const errors: string[] = [];
  
  if (!password || typeof password !== 'string') {
    errors.push('Password is required');
    return { isValid: false, errors };
  }
  
  // Strong password requirements
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (password.length > 128) {
    errors.push('Password cannot exceed 128 characters');
  }
  
  if (!/(?=.*[a-z])/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/(?=.*[A-Z])/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/(?=.*\d)/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  // Check for common passwords without revealing which one
  const commonPasswords = [
    'password', '123456', 'admin', 'qwerty', 'letmein',
    'welcome', 'monkey', '1234567890', 'password123'
  ];
  
  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push('This password is too common. Please choose a more secure password.');
  }
  
  // Check for repeated characters
  if (/(..).*\1/.test(password)) {
    const warnings = ['Avoid using repeated patterns in your password'];
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function sanitizeInput(input: string): string {
  if (!input || typeof input !== 'string') {
    return '';
  }
  
  // Remove all HTML tags
  let sanitized = input.replace(/<[^>]*>/g, '');
  
  // Encode HTML entities
  sanitized = sanitized
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
  
  // Remove control characters except tab, newline, and carriage return
  sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  
  return sanitized.trim();
}

export function validateApiKey(providedKey: string, validKey: string): boolean {
  if (!providedKey || !validKey || typeof providedKey !== 'string' || typeof validKey !== 'string') {
    return false;
  }
  
  // Constant-time comparison to prevent timing attacks
  if (providedKey.length !== validKey.length) {
    // Still perform a comparison to maintain constant time
    let dummy = 0;
    for (let i = 0; i < providedKey.length; i++) {
      dummy |= providedKey.charCodeAt(i) ^ 42; // arbitrary constant
    }
    return false;
  }
  
  let result = 0;
  for (let i = 0; i < providedKey.length; i++) {
    result |= providedKey.charCodeAt(i) ^ validKey.charCodeAt(i);
  }
  
  return result === 0;
}

export function validateUsername(username: string): ValidationResult {
  const errors: string[] = [];
  
  if (!username || typeof username !== 'string') {
    errors.push('Username is required');
    return { isValid: false, errors };
  }
  
  const trimmedUsername = username.trim();
  
  if (trimmedUsername.length < 3) {
    errors.push('Username must be at least 3 characters long');
  }
  
  if (trimmedUsername.length > 30) {
    errors.push('Username cannot exceed 30 characters');
  }
  
  // Allow letters, numbers, underscores, and hyphens
  if (!/^[a-zA-Z0-9_-]+$/.test(trimmedUsername)) {
    errors.push('Username can only contain letters, numbers, underscores, and hyphens');
  }
  
  // Must start with a letter or number
  if (!/^[a-zA-Z0-9]/.test(trimmedUsername)) {
    errors.push('Username must start with a letter or number');
  }
  
  // Reserved usernames (without revealing the exact list)
  const reservedPatterns = [
    /^admin/i, /^root/i, /^system/i, /^test/i, /^demo/i,
    /^api/i, /^www/i, /^mail/i, /^support/i
  ];
  
  if (reservedPatterns.some(pattern => pattern.test(trimmedUsername))) {
    errors.push('This username is not available');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// Simple client-side rate limiting (should be supplemented with server-side)
const loginAttempts = new Map<string, { count: number; lastAttempt: number }>();

export function validateLoginAttempts(username: string): ValidationResult {
  const errors: string[] = [];
  
  if (!username || typeof username !== 'string') {
    errors.push('Username is required for rate limiting check');
    return { isValid: false, errors };
  }
  
  const now = Date.now();
  const windowMs = 15 * 60 * 1000; // 15 minutes
  const maxAttempts = 5;
  
  const userAttempts = loginAttempts.get(username) || { count: 0, lastAttempt: 0 };
  
  // Reset counter if window has passed
  if (now - userAttempts.lastAttempt > windowMs) {
    userAttempts.count = 0;
  }
  
  if (userAttempts.count >= maxAttempts) {
    const timeRemaining = Math.ceil((windowMs - (now - userAttempts.lastAttempt)) / 1000 / 60);
    errors.push(`Too many login attempts. Please try again in ${timeRemaining} minutes.`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function recordLoginAttempt(username: string): void {
  if (!username || typeof username !== 'string') return;
  
  const now = Date.now();
  const userAttempts = loginAttempts.get(username) || { count: 0, lastAttempt: 0 };
  
  userAttempts.count++;
  userAttempts.lastAttempt = now;
  
  loginAttempts.set(username, userAttempts);
}

// Client-side credit card validation (for UX only - server validation required)
export function validateCreditCard(cardNumber: string): ValidationResult {
  const errors: string[] = [];
  
  if (!cardNumber || typeof cardNumber !== 'string') {
    errors.push('Card number is required');
    return { isValid: false, errors };
  }
  
  // Remove spaces and dashes
  const digits = cardNumber.replace(/[\s-]/g, '');
  
  // Check if contains only digits
  if (!/^\d+$/.test(digits)) {
    errors.push('Card number must contain only digits');
  }
  
  // Check length (13-19 digits for most cards)
  if (digits.length < 13 || digits.length > 19) {
    errors.push('Invalid card number length');
  }
  
  // Proper Luhn algorithm implementation
  if (digits.length >= 13 && digits.length <= 19) {
    let sum = 0;
    let isEven = false;
    
    // Process digits from right to left
    for (let i = digits.length - 1; i >= 0; i--) {
      let digit = parseInt(digits[i]);
      
      if (isEven) {
        digit *= 2;
        if (digit > 9) {
          digit -= 9;
        }
      }
      
      sum += digit;
      isEven = !isEven;
    }
    
    if (sum % 10 !== 0) {
      errors.push('Invalid card number');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings: ['Credit card validation should always be verified server-side']
  };
}

export function validateFileUpload(file: File): ValidationResult {
  const errors: string[] = [];
  
  if (!file) {
    errors.push('No file selected');
    return { isValid: false, errors };
  }
  
  // File size validation (5MB limit)
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    errors.push('File size cannot exceed 5MB');
  }
  
  // File type validation (both extension and MIME type)
  const allowedTypes = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'text/plain': ['.txt'],
    'application/pdf': ['.pdf']
  };
  
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  const mimeType = file.type.toLowerCase();
  
  const allowedMimeTypes = Object.keys(allowedTypes);
  if (!allowedMimeTypes.includes(mimeType)) {
    errors.push('File type not allowed');
  } else {
    const expectedExtensions = allowedTypes[mimeType as keyof typeof allowedTypes];
    if (!expectedExtensions.includes(fileExtension)) {
      errors.push('File extension does not match file type');
    }
  }
  
  // File name validation
  if (file.name.length > 255) {
    errors.push('File name is too long');
  }
  
  // Check for potentially dangerous file names
  if (/[\/\\:*?"<>|]/.test(file.name)) {
    errors.push('File name contains invalid characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// Async validation for large datasets to prevent UI blocking
export async function validateLargeDataSet(data: any[]): Promise<ValidationResult> {
  const errors: string[] = [];
  
  if (!Array.isArray(data)) {
    return {
      isValid: false,
      errors: ['Data must be an array']
    };
  }
  
  // Limit dataset size to prevent performance issues
  if (data.length > 10000) {
    return {
      isValid: false,
      errors: ['Dataset too large (maximum 10,000 items)']
    };
  }
  
  const seen = new Set();
  const batchSize = 100;
  
  for (let i = 0; i < data.length; i++) {
    // Yield control every batch to prevent blocking
    if (i % batchSize === 0 && i > 0) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    
    const item = data[i];
    
    if (!item || typeof item !== 'object') {
      errors.push(`Invalid item at index ${i}`);
      continue;
    }
    
    // Use Set for efficient duplicate detection
    const itemKey = JSON.stringify(item);
    if (seen.has(itemKey)) {
      errors.push(`Duplicate item found at index ${i}`);
    } else {
      seen.add(itemKey);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validatePhoneNumber(phone: string): ValidationResult {
  const errors: string[] = [];
  
  if (!phone || typeof phone !== 'string') {
    errors.push('Phone number is required');
    return { isValid: false, errors };
  }
  
  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');
  
  // US phone number validation (10 digits)
  if (digits.length !== 10) {
    errors.push('Phone number must be 10 digits');
  }
  
  // Area code cannot start with 0 or 1
  if (digits.length >= 3 && (digits[0] === '0' || digits[0] === '1')) {
    errors.push('Invalid area code');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export function formatPhoneNumber(phone: string): string {
  const validation = validatePhoneNumber(phone);
  if (!validation.isValid) {
    return phone; // Return original if invalid
  }
  
  const digits = phone.replace(/\D/g, '');
  return digits.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
}

// Secure validation configuration
export const ValidationConfig = {
  password: {
    minLength: 8,
    maxLength: 128,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true
  },
  username: {
    minLength: 3,
    maxLength: 30,
    allowedPattern: /^[a-zA-Z0-9_-]+$/
  },
  file: {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'text/plain', 'application/pdf']
  }
};

export function validateSecurityToken(token: string): ValidationResult {
  const errors: string[] = [];
  
  if (!token || typeof token !== 'string') {
    errors.push('Security token is required');
    return { isValid: false, errors };
  }
  
  // Basic token format validation (without revealing the exact format)
  if (token.length < 16 || token.length > 256) {
    errors.push('Invalid token format');
  }
  
  // Check for valid characters (alphanumeric + some special chars)
  if (!/^[a-zA-Z0-9._-]+$/.test(token)) {
    errors.push('Token contains invalid characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}