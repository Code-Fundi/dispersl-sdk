/**
 * Helper utilities for the Dispersl SDK.
 * 
 * This module provides common utility functions used throughout the SDK
 * for data processing, validation, and other operations.
 */

/**
 * Check if a string is a valid URL.
 * 
 * @param url - String to validate as URL
 * @returns True if valid URL, False otherwise
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Build a complete URL from base URL, path, and query parameters.
 * 
 * @param baseUrl - Base URL (e.g., "https://api.example.com")
 * @param path - Path component (e.g., "/users/123")
 * @param params - Query parameters
 * @returns Complete URL string
 */
export function buildUrl(
  baseUrl: string,
  path: string,
  params?: Record<string, unknown>
): string {
  // Ensure baseUrl doesn't end with slash and path starts with slash
  const cleanBaseUrl = baseUrl.replace(/\/$/, '');
  const cleanPath = path.replace(/^\//, '');

  const url = cleanPath ? `${cleanBaseUrl}/${cleanPath}` : cleanBaseUrl;

  if (params) {
    // Filter out null/undefined values
    const filteredParams = Object.entries(params)
      .filter(([, value]) => value !== null && value !== undefined)
      .reduce((acc, [key, value]) => {
        acc[key] = value;
        return acc;
      }, {} as Record<string, unknown>);

    if (Object.keys(filteredParams).length > 0) {
      const searchParams = new URLSearchParams();
      for (const [key, value] of Object.entries(filteredParams)) {
        searchParams.append(key, String(value));
      }
      return `${url}?${searchParams.toString()}`;
    }
  }

  return url;
}

/**
 * Sanitize a filename by removing or replacing invalid characters.
 * 
 * @param filename - Original filename
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string): string {
  // Remove or replace invalid characters
  let sanitized = filename.replace(/[<>:"/\\|?*]/g, '_');

  // Remove leading/trailing dots and spaces
  sanitized = sanitized.replace(/^[\s.]+|[\s.]+$/g, '');

  // Ensure it's not empty
  if (!sanitized) {
    sanitized = 'file';
  }

  // Limit length
  if (sanitized.length > 255) {
    const lastDotIndex = sanitized.lastIndexOf('.');
    if (lastDotIndex > 0) {
      const name = sanitized.substring(0, lastDotIndex);
      const ext = sanitized.substring(lastDotIndex);
      sanitized = name.substring(0, 255 - ext.length) + ext;
    } else {
      sanitized = sanitized.substring(0, 255);
    }
  }

  return sanitized;
}

/**
 * Deep merge two objects, with obj2 values taking precedence.
 * 
 * @param obj1 - First object
 * @param obj2 - Second object (takes precedence)
 * @returns Merged object
 */
export function deepMergeObjects<T extends Record<string, unknown>>(
  obj1: T,
  obj2: Partial<T>
): T {
  const result = { ...obj1 } as Record<string, unknown>;

  for (const [key, value] of Object.entries(obj2)) {
    if (value === null || value === undefined) {
      continue;
    }

    if (key in result && typeof result[key] === 'object' && typeof value === 'object') {
      if (Array.isArray(result[key]) && Array.isArray(value)) {
        result[key] = value;
      } else if (!Array.isArray(result[key]) && !Array.isArray(value)) {
        result[key] = deepMergeObjects(
          result[key] as Record<string, unknown>,
          value as Record<string, unknown>
        );
      } else {
        result[key] = value;
      }
    } else {
      result[key] = value;
    }
  }

  return result as T;
}

/**
 * Flatten a nested object using the specified separator.
 * 
 * @param data - Object to flatten
 * @param separator - Separator to use for nested keys
 * @returns Flattened object
 */
export function flattenObject(
  data: Record<string, unknown>,
  separator: string = '.'
): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  function flatten(obj: unknown, prefix: string = ''): void {
    if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        for (let i = 0; i < obj.length; i++) {
          flatten(obj[i], `${prefix}${separator}${i}`);
        }
      } else {
        for (const [key, value] of Object.entries(obj)) {
          const newKey = prefix ? `${prefix}${separator}${key}` : key;
          flatten(value, newKey);
        }
      }
    } else {
      result[prefix] = obj;
    }
  }

  flatten(data);
  return result;
}

/**
 * Unflatten an object using the specified separator.
 * 
 * @param data - Flattened object
 * @param separator - Separator used for nested keys
 * @returns Unflattened object
 */
export function unflattenObject(
  data: Record<string, unknown>,
  separator: string = '.'
): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(data)) {
    const keys = key.split(separator);
    let current = result;

    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!k) continue;
      
      if (!(k in current) || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k] as Record<string, unknown>;
    }

    const lastKey = keys[keys.length - 1];
    if (lastKey) {
      current[lastKey] = value;
    }
  }

  return result;
}

/**
 * Split an array into chunks of specified size.
 * 
 * @param items - Array to chunk
 * @param chunkSize - Size of each chunk
 * @returns Array of chunks
 */
export function chunkArray<T>(items: T[], chunkSize: number): T[][] {
  if (chunkSize <= 0) {
    throw new Error('Chunk size must be positive');
  }

  const chunks: T[][] = [];
  for (let i = 0; i < items.length; i += chunkSize) {
    chunks.push(items.slice(i, i + chunkSize));
  }

  return chunks;
}

/**
 * Remove null/undefined values from an object recursively.
 * 
 * @param data - Object to clean
 * @returns Object with null/undefined values removed
 */
export function removeNullValues<T extends Record<string, unknown>>(data: T): Partial<T> {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  const cleaned: Partial<T> = {};
  for (const [key, value] of Object.entries(data)) {
    if (value === null || value === undefined) {
      continue;
    }

    if (typeof value === 'object' && !Array.isArray(value)) {
      const cleanedValue = removeNullValues(value as Record<string, unknown>);
      if (Object.keys(cleanedValue).length > 0) {
        cleaned[key as keyof T] = cleanedValue as T[keyof T];
      }
    } else if (Array.isArray(value)) {
      const cleanedArray = value
        .map(item => typeof item === 'object' && item !== null ? removeNullValues(item as Record<string, unknown>) : item)
        .filter(item => item !== null && item !== undefined);
      if (cleanedArray.length > 0) {
        cleaned[key as keyof T] = cleanedArray as T[keyof T];
      }
    } else {
      cleaned[key as keyof T] = value as T[keyof T];
    }
  }

  return cleaned;
}

/**
 * Format bytes value as human-readable string.
 * 
 * @param bytes - Number of bytes
 * @returns Formatted string (e.g., "1.5 MB")
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  if (unitIndex === 0) {
    return `${Math.round(size)} ${units[unitIndex]}`;
  } else {
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }
}

/**
 * Truncate a string to maximum length with optional suffix.
 * 
 * @param text - String to truncate
 * @param maxLength - Maximum length
 * @param suffix - Suffix to add when truncating
 * @returns Truncated string
 */
export function truncateString(text: string, maxLength: number, suffix: string = '...'): string {
  if (text.length <= maxLength) {
    return text;
  }

  return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Extract domain from URL.
 * 
 * @param url - URL to extract domain from
 * @returns Domain string or null if invalid URL
 */
export function extractDomainFromUrl(url: string): string | null {
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

/**
 * Check if a string is a valid email address.
 * 
 * @param email - String to validate as email
 * @returns True if valid email, False otherwise
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

/**
 * Generate a unique request ID.
 * 
 * @returns Unique request ID string
 */
export function generateRequestId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

/**
 * Convert Retry-After header value to seconds.
 * 
 * @param retryAfter - Retry-After header value
 * @returns Seconds to wait
 */
export function retryAfterToSeconds(retryAfter: string | number): number {
  if (typeof retryAfter === 'number') {
    return retryAfter;
  }

  if (typeof retryAfter === 'string') {
    // Try to parse as integer first
    const parsed = parseInt(retryAfter, 10);
    if (!isNaN(parsed)) {
      return parsed;
    }

    // Try to parse as HTTP date
    try {
      const date = new Date(retryAfter);
      if (!isNaN(date.getTime())) {
        const now = new Date();
        return Math.max(0, Math.floor((date.getTime() - now.getTime()) / 1000));
      }
    } catch {
      // Ignore parsing errors
    }
  }

  // Default to 60 seconds if parsing fails
  return 60;
}

/**
 * Type guard to check if a value is a plain object.
 * 
 * @param value - Value to check
 * @returns True if value is a plain object
 */
export function isPlainObject(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value) &&
    Object.prototype.toString.call(value) === '[object Object]'
  );
}

/**
 * Type guard to check if a value is a non-empty string.
 * 
 * @param value - Value to check
 * @returns True if value is a non-empty string
 */
export function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0;
}

/**
 * Type guard to check if a value is a positive number.
 * 
 * @param value - Value to check
 * @returns True if value is a positive number
 */
export function isPositiveNumber(value: unknown): value is number {
  return typeof value === 'number' && value > 0;
}
