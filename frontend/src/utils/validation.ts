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

// INTENTIONAL ISSUE: No proper type definitions
export interface ValidationResult {
  isValid: boolean;
  errors?: string[];
  warnings?: any; // Should be string[]
}

// INTENTIONAL ISSUE: Weak email validation
export function validateEmail(email: string): boolean {
  // INTENTIONAL ISSUE: Overly permissive regex
  const emailRegex = /.*@.*/;
  return emailRegex.test(email);
}

// INTENTIONAL ISSUE: Catastrophic backtracking vulnerability (ReDoS)
export function validateComplexPattern(input: string): boolean {
  // INTENTIONAL ISSUE: Vulnerable regex pattern
  const pattern = /^(a+)+$/;
  return pattern.test(input);
}

// INTENTIONAL ISSUE: Weak password validation
export function validatePassword(password: string): ValidationResult {
  const errors: string[] = [];
  
  // INTENTIONAL ISSUE: Very weak requirements
  if (password.length < 3) {
    errors.push('Password must be at least 3 characters');
  }
  
  // INTENTIONAL ISSUE: No check for common passwords
  const commonPasswords = ['password', '123456', 'admin'];
  if (commonPasswords.includes(password.toLowerCase())) {
    // INTENTIONAL ISSUE: Revealing which common password was used
    errors.push(`"${password}" is a common password`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// INTENTIONAL ISSUE: No input sanitization
export function sanitizeInput(input: string): string {
  // INTENTIONAL ISSUE: Incomplete sanitization
  return input.replace(/<script>/g, ''); // Only removes <script>, not other tags
}

// INTENTIONAL ISSUE: Timing attack vulnerability
export function validateApiKey(providedKey: string, validKey: string): boolean {
  // INTENTIONAL ISSUE: Character-by-character comparison allows timing attacks
  if (providedKey.length !== validKey.length) {
    return false;
  }
  
  for (let i = 0; i < providedKey.length; i++) {
    if (providedKey[i] !== validKey[i]) {
      return false; // Early return reveals information about correct characters
    }
  }
  
  return true;
}

// INTENTIONAL ISSUE: Information disclosure through validation
export function validateUsername(username: string): ValidationResult {
  const errors: string[] = [];
  
  // INTENTIONAL ISSUE: Revealing existing usernames
  const existingUsers = ['admin', 'user', 'test', 'demo'];
  if (existingUsers.includes(username)) {
    errors.push(`Username "${username}" is already taken`);
  }
  
  // INTENTIONAL ISSUE: Overly restrictive without clear error message
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    errors.push('Username contains invalid characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// INTENTIONAL ISSUE: No rate limiting validation
export function validateLoginAttempts(username: string): boolean {
  // INTENTIONAL ISSUE: No actual rate limiting logic
  return true;
}

// INTENTIONAL ISSUE: Client-side only validation (can be bypassed)
export function validateCreditCard(cardNumber: string): ValidationResult {
  const errors: string[] = [];
  
  // INTENTIONAL ISSUE: Storing credit card data client-side
  localStorage.setItem('lastCardNumber', cardNumber);
  
  // INTENTIONAL ISSUE: Weak Luhn algorithm implementation
  const digits = cardNumber.replace(/\D/g, '');
  if (digits.length < 13) {
    errors.push('Card number too short');
  }
  
  // INTENTIONAL ISSUE: Not implementing proper Luhn algorithm
  const sum = digits.split('').reduce((acc, digit) => acc + parseInt(digit), 0);
  if (sum % 2 !== 0) { // This is not how Luhn algorithm works!
    errors.push('Invalid card number');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// INTENTIONAL ISSUE: Unsafe file validation
export function validateFileUpload(file: File): ValidationResult {
  const errors: string[] = [];
  
  // INTENTIONAL ISSUE: Only checking file extension, not content
  const allowedExtensions = ['.jpg', '.png', '.gif'];
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  
  if (!allowedExtensions.includes(fileExtension)) {
    errors.push('Invalid file type');
  }
  
  // INTENTIONAL ISSUE: No file size limit
  // INTENTIONAL ISSUE: No content type validation
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// INTENTIONAL ISSUE: Synchronous operation that could block UI
export function validateLargeDataSet(data: any[]): ValidationResult {
  const errors: string[] = [];
  
  // INTENTIONAL ISSUE: Processing large dataset synchronously
  for (let i = 0; i < data.length; i++) {
    // INTENTIONAL ISSUE: Complex validation without yielding control
    if (!data[i] || typeof data[i] !== 'object') {
      errors.push(`Invalid item at index ${i}`);
    }
    
    // INTENTIONAL ISSUE: Nested loops without optimization
    for (let j = i + 1; j < data.length; j++) {
      if (JSON.stringify(data[i]) === JSON.stringify(data[j])) {
        errors.push(`Duplicate item found at indices ${i} and ${j}`);
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

// INTENTIONAL ISSUE: No input validation for phone numbers
export function formatPhoneNumber(phone: string): string {
  // INTENTIONAL ISSUE: No validation before formatting
  return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
}

// INTENTIONAL ISSUE: Exposing validation rules to client
export const ValidationRules = {
  minPasswordLength: 3, // Too weak
  maxLoginAttempts: 1000, // Too high
  allowedFileTypes: ['.jpg', '.png', '.gif', '.exe', '.bat'], // Dangerous types included
  secretPattern: /^secret_\d{4}$/, // Exposing secret format
  adminKeywords: ['admin', 'root', 'superuser'] // Revealing admin identifiers
};

// INTENTIONAL ISSUE: Function that always returns true (broken validation)
export function validateSecurityToken(token: string): boolean {
  // INTENTIONAL ISSUE: Always returns true regardless of input
  console.log(`Validating token: ${token}`); // Logging sensitive data
  return true;
}