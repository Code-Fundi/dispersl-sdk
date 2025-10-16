/**
 * Request/response serialization utilities.
 * 
 * This module handles serialization and deserialization of data
 * for API requests and responses, including datetime handling,
 * null/undefined values, and nested object validation.
 */

import { z } from 'zod';
import { SerializationError } from './exceptions';

// Re-export SerializationError for convenience
export { SerializationError };

/**
 * JSON serializer class for handling JSON serialization/deserialization.
 */
export class JSONSerializer {
  /**
   * Serialize data to JSON string.
   * 
   * @param data - Data to serialize
   * @param options - Serialization options
   * @returns JSON string
   * @throws SerializationError - If serialization fails
   */
  static serialize(data: unknown, options?: { indent?: number }): string {
    try {
      if (options?.indent) {
        return JSON.stringify(data, null, options.indent);
      }
      return JSON.stringify(data);
    } catch (error) {
      throw new SerializationError(
        `Failed to serialize data: ${error}`,
        error as Error
      );
    }
  }

  /**
   * Deserialize JSON string to data.
   * 
   * @param json - JSON string
   * @returns Deserialized data
   * @throws SerializationError - If deserialization fails
   */
  static deserialize<T = unknown>(json: string): T {
    try {
      return JSON.parse(json) as T;
    } catch (error) {
      throw new SerializationError(
        `Failed to deserialize JSON: ${error}`,
        error as Error
      );
    }
  }
}

/**
 * NDJSON (Newline Delimited JSON) parser for streaming responses.
 */
export class NDJSONParser {
  private buffer: string = '';

  /**
   * Parse a chunk of NDJSON data.
   * 
   * @param chunk - Data chunk to parse
   * @param options - Parsing options
   * @returns Array of parsed objects
   */
  parse(chunk: string, options?: { skipInvalid?: boolean }): unknown[] {
    this.buffer += chunk;
    const lines = this.buffer.split('\n');
    
    // Keep the last incomplete line in the buffer
    this.buffer = lines.pop() || '';
    
    const results: unknown[] = [];
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed) {
        try {
          results.push(JSON.parse(trimmed));
        } catch (error) {
          // Skip invalid JSON if option is set, otherwise throw
          if (options?.skipInvalid) {
            continue;
          }
          throw new SerializationError(
            `Failed to parse NDJSON line: ${trimmed}`,
            error as Error
          );
        }
      }
    }
    
    return results;
  }

  /**
   * Flush remaining buffer content.
   * 
   * @param options - Flush options
   * @returns Final parsed object if any
   */
  flush(options?: { throwOnInvalid?: boolean }): unknown | null {
    if (this.buffer.trim()) {
      try {
        const result = JSON.parse(this.buffer);
        this.buffer = '';
        return result;
      } catch (error) {
        // Clear buffer and return null if option is false, otherwise throw
        this.buffer = '';
        if (options?.throwOnInvalid !== false) {
          throw new SerializationError(
            `Failed to parse remaining NDJSON: ${this.buffer}`,
            error as Error
          );
        }
        return null;
      }
    }
    return null;
  }

  /**
   * Reset the parser state.
   */
  reset(): void {
    this.buffer = '';
  }
}

/**
 * Stream parser for handling streaming API responses.
 */
export class StreamParser {
  private decoder: TextDecoder;
  private parser: NDJSONParser;

  constructor() {
    this.decoder = new TextDecoder();
    this.parser = new NDJSONParser();
  }

  /**
   * Parse a stream chunk.
   * 
   * @param chunk - Stream chunk (Uint8Array or string)
   * @param options - Parsing options
   * @returns Array of parsed objects
   */
  parseChunk(chunk: Uint8Array | string, options?: { skipInvalid?: boolean }): unknown[] {
    const text = typeof chunk === 'string' ? chunk : this.decoder.decode(chunk, { stream: true });
    return this.parser.parse(text, options);
  }

  /**
   * Flush and get remaining data.
   * 
   * @param options - Flush options
   * @returns Final parsed object if any
   */
  flush(options?: { throwOnInvalid?: boolean }): unknown | null {
    return this.parser.flush(options);
  }

  /**
   * Reset the parser state.
   */
  reset(): void {
    this.parser.reset();
  }
}

/**
 * Serialize request data for API calls.
 * 
 * Handles:
 * - Objects -> JSON
 * - Date objects -> ISO 8601 strings
 * - Undefined values -> null
 * - Custom objects -> JSON representation
 * 
 * @param data - Data to serialize
 * @returns Serialized data
 * @throws SerializationError - If serialization fails
 */
export function serializeRequestData(data: unknown): unknown {
  try {
    if (data === null || data === undefined) {
      return {};
    }

    if (typeof data === 'object') {
      // Handle Date objects
      if (data instanceof Date) {
        return data.toISOString();
      }

      // Handle arrays
      if (Array.isArray(data)) {
        return data.map(serializeRequestData);
      }

      // Handle plain objects
      if (data.constructor === Object) {
        const serialized: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(data)) {
          if (value !== undefined) {
            serialized[key] = serializeRequestData(value);
          }
        }
        return serialized;
      }

      // Handle objects with toJSON method
      if ('toJSON' in data && typeof (data as any).toJSON === 'function') {
        return (data as any).toJSON();
      }

      // Handle objects with custom serialization
      if ('serialize' in data && typeof (data as any).serialize === 'function') {
        return (data as any).serialize();
      }
    }

    return data;
  } catch (error) {
    throw new Error(`Failed to serialize request data: ${error}`);
  }
}

/**
 * Deserialize response data from API calls.
 * 
 * Handles:
 * - JSON strings -> JavaScript objects
 * - ISO 8601 strings -> Date objects
 * - Model validation with Zod schemas
 * 
 * @param responseData - Raw response data
 * @param schema - Optional Zod schema for validation
 * @returns Deserialized data
 * @throws SerializationError - If deserialization fails
 */
export function deserializeResponseData<T = unknown>(
  responseData: string | unknown,
  schema?: z.ZodSchema<T>
): T {
  try {
    let data: unknown;

    // Parse JSON if needed
    if (typeof responseData === 'string') {
      data = JSON.parse(responseData);
    } else {
      data = responseData;
    }

    // Validate with Zod schema if provided
    if (schema) {
      return schema.parse(data);
    }

    return data as T;
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(`Validation failed: ${error.message}`);
    }
    throw new Error(`Failed to deserialize response data: ${error}`);
  }
}

/**
 * Serialize datetime object to ISO 8601 string.
 * 
 * @param date - Date object to serialize
 * @returns ISO 8601 formatted string
 */
export function serializeDateTime(date: Date): string {
  return date.toISOString();
}

/**
 * Deserialize ISO 8601 string to Date object.
 * 
 * @param dateString - ISO 8601 formatted string
 * @returns Date object
 * @throws SerializationError - If parsing fails
 */
export function deserializeDateTime(dateString: string): Date {
  try {
    // Handle various ISO 8601 formats
    if (dateString.includes('T')) {
      // Full datetime
      if (dateString.endsWith('Z')) {
        dateString = dateString.slice(0, -1) + '+00:00';
      }
      return new Date(dateString);
    } else {
      // Date only
      return new Date(dateString + 'T00:00:00');
    }
  } catch (error) {
    throw new Error(`Failed to parse datetime: ${dateString}`);
  }
}

/**
 * Remove null/undefined values from object recursively.
 * 
 * @param data - Object to clean
 * @returns Object with null/undefined values removed
 */
export function cleanNullValues<T extends Record<string, unknown>>(data: T): Partial<T> {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  const cleaned: Partial<T> = {};
  for (const [key, value] of Object.entries(data)) {
    if (value === null || value === undefined) {
      continue;
    }

    if (typeof value === 'object' && !Array.isArray(value)) {
      const cleanedValue = cleanNullValues(value as Record<string, unknown>);
      if (Object.keys(cleanedValue).length > 0) {
        cleaned[key as keyof T] = cleanedValue as T[keyof T];
      }
    } else if (Array.isArray(value)) {
      const cleanedArray = value
        .map(item => typeof item === 'object' && item !== null ? cleanNullValues(item as Record<string, unknown>) : item)
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
 * Validate that required fields are present in data.
 * 
 * @param data - Data to validate
 * @param requiredFields - List of required field names
 * @param context - Context for error messages
 * @throws ValidationError - If required fields are missing
 */
export function validateRequiredFields(
  data: Record<string, unknown>,
  requiredFields: string[],
  context: string = 'request'
): void {
  const missingFields: string[] = [];
  for (const field of requiredFields) {
    if (!(field in data) || data[field] === null || data[field] === undefined) {
      missingFields.push(field);
    }
  }

  if (missingFields.length > 0) {
    throw new Error(
      `Missing required fields in ${context}: ${missingFields.join(', ')}`
    );
  }
}

/**
 * Convert camelCase keys to snake_case recursively.
 * 
 * @param data - Object with camelCase keys
 * @returns Object with snake_case keys
 */
export function convertCamelToSnake<T extends Record<string, unknown>>(data: T): Record<string, unknown> {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  const converted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(data)) {
    // Convert camelCase to snake_case
    const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);

    // Recursively convert nested objects
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      converted[snakeKey] = convertCamelToSnake(value as Record<string, unknown>);
    } else if (Array.isArray(value)) {
      converted[snakeKey] = value.map(item =>
        typeof item === 'object' && item !== null
          ? convertCamelToSnake(item as Record<string, unknown>)
          : item
      );
    } else {
      converted[snakeKey] = value;
    }
  }

  return converted;
}

/**
 * Convert snake_case keys to camelCase recursively.
 * 
 * @param data - Object with snake_case keys
 * @returns Object with camelCase keys
 */
export function convertSnakeToCamel<T extends Record<string, unknown>>(data: T): Record<string, unknown> {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  const converted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(data)) {
    // Convert snake_case to camelCase
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());

    // Recursively convert nested objects
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      converted[camelKey] = convertSnakeToCamel(value as Record<string, unknown>);
    } else if (Array.isArray(value)) {
      converted[camelKey] = value.map(item =>
        typeof item === 'object' && item !== null
          ? convertSnakeToCamel(item as Record<string, unknown>)
          : item
      );
    } else {
      converted[camelKey] = value;
    }
  }

  return converted;
}

/**
 * Common Zod schemas for API data validation.
 */
export const CommonSchemas = {
  /**
   * ISO 8601 datetime string schema.
   */
  datetime: z.string().datetime(),

  /**
   * UUID string schema.
   */
  uuid: z.string().uuid(),

  /**
   * Email string schema.
   */
  email: z.string().email(),

  /**
   * URL string schema.
   */
  url: z.string().url(),

  /**
   * Positive integer schema.
   */
  positiveInt: z.number().int().positive(),

  /**
   * Non-negative integer schema.
   */
  nonNegativeInt: z.number().int().min(0),

  /**
   * Pagination parameters schema.
   */
  pagination: z.object({
    limit: z.number().int().min(1).max(1000).optional(),
    offset: z.number().int().min(0).optional(),
    cursor: z.string().optional(),
  }),

  /**
   * Error response schema.
   */
  errorResponse: z.object({
    status: z.literal('error'),
    message: z.string(),
    error: z.object({
      code: z.number().optional(),
      message: z.string(),
    }).optional(),
  }),
} as const;
