/**
 * Base data models for the Dispersl SDK.
 * 
 * This module contains the base model classes and common data structures
 * used throughout the SDK.
 */

import { z } from 'zod';

/**
 * Base response model for all API responses.
 * 
 * Provides common fields that appear in most API responses.
 */
export const BaseResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
});

export type BaseResponse = z.infer<typeof BaseResponseSchema>;

/**
 * Error response model.
 * 
 * Used for API error responses with additional error details.
 */
export const ErrorResponseSchema = BaseResponseSchema.extend({
  status: z.literal('error'),
  error: z.object({
    code: z.number().optional(),
    message: z.string(),
  }).optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

/**
 * Pagination parameters for list endpoints.
 * 
 * Provides common pagination fields used across the API.
 */
export const PaginationParamsSchema = z.object({
  page: z.number().int().min(1).optional(),
  pageSize: z.number().int().min(1).max(100).optional(),
});

export type PaginationParams = z.infer<typeof PaginationParamsSchema>;

/**
 * Pagination metadata model.
 * 
 * Contains pagination information for paginated responses.
 */
export const PaginationSchema = z.object({
  page: z.number().int(),
  pageSize: z.number().int(),
  total: z.number().int(),
  totalPages: z.number().int(),
  hasNext: z.boolean(),
  hasPrev: z.boolean(),
});

export type Pagination = z.infer<typeof PaginationSchema>;

/**
 * Paginated response model.
 * 
 * Used for responses that contain paginated data.
 */
export const PaginatedResponseSchema = BaseResponseSchema.extend({
  data: z.array(z.unknown()),
  pagination: PaginationSchema,
});

export type PaginatedResponse<T = unknown> = z.infer<typeof PaginatedResponseSchema> & {
  data: T[];
};

/**
 * Metadata model for API responses.
 * 
 * Contains additional information about the response.
 */
export const MetadataSchema = z.object({
  tokens: z.number().int().optional(),
  cost: z.number().optional(),
  language: z.string().optional(),
  files_processed: z.number().int().optional(),
  request_id: z.string().optional(),
  timestamp: z.string().datetime().optional(),
});

export type Metadata = z.infer<typeof MetadataSchema>;

/**
 * Standard NDJSON streaming response model.
 * 
 * Used for streaming responses from agent endpoints.
 */
export const StandardNdjsonResponseSchema = BaseResponseSchema.extend({
  content: z.string().optional(),
  knowledge: z.array(z.string()).optional(),
  tools: z.array(z.unknown()).optional(),
  audio: z.string().optional(),
  error: z.object({
    code: z.number().int(),
    message: z.string(),
  }).optional(),
  metadata: MetadataSchema.optional(),
});

export type StandardNdjsonResponse = z.infer<typeof StandardNdjsonResponseSchema>;

/**
 * Base model with timestamp fields.
 * 
 * Provides created_at and updated_at fields for models
 * that track creation and modification times.
 */
export const TimestampedModelSchema = z.object({
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export type TimestampedModel = z.infer<typeof TimestampedModelSchema>;

/**
 * Base model with ID field.
 * 
 * Provides an id field for models that have unique identifiers.
 */
export const IdentifiableModelSchema = z.object({
  id: z.string(),
});

export type IdentifiableModel = z.infer<typeof IdentifiableModelSchema>;

/**
 * Base model with name field.
 * 
 * Provides a name field for models that have human-readable names.
 */
export const NamedModelSchema = z.object({
  name: z.string(),
});

export type NamedModel = z.infer<typeof NamedModelSchema>;
