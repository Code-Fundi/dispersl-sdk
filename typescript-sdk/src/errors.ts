export class DisperslError extends Error {
  constructor(message: string, public readonly code?: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class AuthenticationError extends DisperslError {}
export class RateLimitError extends DisperslError {
  constructor(message: string, public readonly retryAfterSeconds?: number) {
    super(message, "RATE_LIMIT");
  }
}
export class ValidationError extends DisperslError {}
export class NotFoundError extends DisperslError {}
export class ConflictError extends DisperslError {}
export class ServerError extends DisperslError {}
export class TimeoutError extends DisperslError {}
export class StreamParseError extends DisperslError {}
export class ToolExecutionError extends DisperslError {}
export class HandoverError extends DisperslError {}
