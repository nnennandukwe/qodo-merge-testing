/**
 * TypeScript type definitions for the application.
 * 
 * This module contains all interface definitions, types, and enums
 * used throughout the frontend application for type safety.
 */

// Base interfaces
export interface BaseEntity {
  id: number;
  createdAt?: string;
  updatedAt?: string;
}

// User-related types
export interface User extends BaseEntity {
  username: string;
  email: string;
  isActive?: boolean;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  role?: UserRole;
}

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword?: string;
  firstName?: string;
  lastName?: string;
}

export interface UserUpdateRequest {
  username?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  isActive?: boolean;
}

export interface UserLoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface UserLoginResponse {
  user: User;
  token: string;
  refreshToken?: string;
  expiresAt: string;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  MODERATOR = 'moderator',
  GUEST = 'guest'
}

// API Response types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: APIError;
}

export interface APIError {
  id?: string;
  code: string;
  message: string;
  category?: string;
  field?: string;
  validationErrors?: ValidationError[];
  suggestions?: string[];
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// Table/Data Display types
export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
  headerRender?: () => React.ReactNode;
}

export interface SortConfiguration {
  column: string;
  direction: SortDirection;
}

export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc'
}

export interface FilterConfiguration {
  field: string;
  operator: FilterOperator;
  value: any;
}

export enum FilterOperator {
  EQUALS = 'equals',
  CONTAINS = 'contains',
  STARTS_WITH = 'startsWith',
  ENDS_WITH = 'endsWith',
  GREATER_THAN = 'greaterThan',
  LESS_THAN = 'lessThan',
  IN = 'in',
  NOT_IN = 'notIn'
}

export interface TableConfiguration<T = any> {
  columns: TableColumn<T>[];
  sortable?: boolean;
  filterable?: boolean;
  searchable?: boolean;
  paginated?: boolean;
  selectable?: boolean;
  actions?: TableAction<T>[];
}

export interface TableAction<T = any> {
  label: string;
  icon?: string;
  onClick: (row: T) => void;
  disabled?: (row: T) => boolean;
  visible?: (row: T) => boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'warning';
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: FormFieldType;
  required?: boolean;
  placeholder?: string;
  disabled?: boolean;
  options?: FormFieldOption[];
  validation?: FieldValidation;
  defaultValue?: any;
  helpText?: string;
}

export enum FormFieldType {
  TEXT = 'text',
  EMAIL = 'email',
  PASSWORD = 'password',
  NUMBER = 'number',
  TEXTAREA = 'textarea',
  SELECT = 'select',
  MULTI_SELECT = 'multiSelect',
  CHECKBOX = 'checkbox',
  RADIO = 'radio',
  DATE = 'date',
  TIME = 'time',
  DATETIME = 'datetime',
  FILE = 'file'
}

export interface FormFieldOption {
  value: any;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface FieldValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  customValidator?: (value: any) => string | null;
  asyncValidator?: (value: any) => Promise<string | null>;
}

export interface FormErrors {
  [fieldName: string]: string | undefined;
}

export interface FormState<T = any> {
  values: T;
  errors: FormErrors;
  touched: { [fieldName: string]: boolean };
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
}

// Component Props types
export interface BaseComponentProps {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  'data-testid'?: string;
}

export interface LoadingState {
  isLoading: boolean;
  loadingText?: string;
}

export interface ErrorState {
  hasError: boolean;
  error?: Error | APIError | string;
  errorFallback?: React.ComponentType<ErrorFallbackProps>;
}

export interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

// Data fetching types
export interface QueryOptions {
  page?: number;
  pageSize?: number;
  sort?: SortConfiguration[];
  filters?: FilterConfiguration[];
  search?: string;
  include?: string[];
}

export interface MutationOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: APIError) => void;
  onComplete?: () => void;
}

export interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  staleTime?: number;
  refetchOnWindowFocus?: boolean;
  refetchOnReconnect?: boolean;
}

// File upload types
export interface FileUploadOptions {
  maxSize?: number;
  allowedTypes?: string[];
  multiple?: boolean;
  accept?: string;
}

export interface UploadedFile {
  file: File;
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  uploadProgress?: number;
  uploadStatus: UploadStatus;
  error?: string;
}

export enum UploadStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  SUCCESS = 'success',
  ERROR = 'error',
  CANCELLED = 'cancelled'
}

// Navigation types
export interface NavigationItem {
  id: string;
  label: string;
  path?: string;
  icon?: string;
  children?: NavigationItem[];
  permissions?: string[];
  badge?: string | number;
  disabled?: boolean;
  external?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
  isActive?: boolean;
}

// Theme and UI types
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  light: string;
  dark: string;
  muted: string;
}

export interface ThemeConfiguration {
  colors: ThemeColors;
  spacing: { [key: string]: string };
  typography: { [key: string]: React.CSSProperties };
  breakpoints: { [key: string]: string };
  shadows: { [key: string]: string };
  borderRadius: { [key: string]: string };
}

export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  SUCCESS = 'success',
  WARNING = 'warning',
  DANGER = 'danger',
  INFO = 'info',
  LIGHT = 'light',
  DARK = 'dark',
  OUTLINE = 'outline',
  GHOST = 'ghost',
  LINK = 'link'
}

export enum ComponentSize {
  SMALL = 'sm',
  MEDIUM = 'md',
  LARGE = 'lg',
  EXTRA_LARGE = 'xl'
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Event handler types
export type EventHandler<T = any> = (event: T) => void;
export type ChangeHandler<T = any> = (value: T) => void;
export type SubmitHandler<T = any> = (data: T) => void | Promise<void>;
export type ErrorHandler = (error: Error | APIError) => void;

// Generic types for reusable components
export interface SelectOption<T = any> {
  value: T;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: ComponentSize;
  centered?: boolean;
  backdrop?: boolean | 'static';
  keyboard?: boolean;
}

export interface ToastNotification {
  id: string;
  title?: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  persistent?: boolean;
  actions?: Array<{
    label: string;
    onClick: () => void;
  }>;
}

// Application state types
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: ToastNotification[];
  loading: { [key: string]: boolean };
  errors: { [key: string]: APIError | null };
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}