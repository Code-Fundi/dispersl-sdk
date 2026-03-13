import {
  AuthenticationError,
  ConflictError,
  NotFoundError,
  RateLimitError,
  ServerError,
  TimeoutError,
  ValidationError
} from "./errors";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export interface HttpRequestOptions extends RequestInit {
  timeoutMs?: number;
  retryAttempts?: number;
}

export class HttpClient {
  constructor(
    private readonly baseUrl: string,
    private readonly apiKey: string,
    private readonly defaultTimeoutMs = 120_000,
    private readonly defaultRetryAttempts = 3
  ) {}

  async request<T>(path: string, options: HttpRequestOptions = {}): Promise<T> {
    const timeoutMs = options.timeoutMs ?? this.defaultTimeoutMs;
    const retryAttempts = options.retryAttempts ?? this.defaultRetryAttempts;
    const url = `${this.baseUrl}${path}`;
    const headers: HeadersInit = {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    };

    let lastError: unknown;

    for (let attempt = 0; attempt <= retryAttempts; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), timeoutMs);

      try {
        const response = await fetch(url, { ...options, headers, signal: controller.signal });
        clearTimeout(timeout);

        if (response.ok) {
          const contentType = response.headers.get("content-type") ?? "";
          if (contentType.includes("application/json")) {
            return (await response.json()) as T;
          }
          return (response.body as T) ?? ((await response.text()) as T);
        }

        const responseText = await response.text();
        const retryable = response.status === 408 || response.status === 429 || response.status >= 500;
        if (retryable && attempt < retryAttempts) {
          const delay = Math.min(300 * 2 ** attempt + Math.floor(Math.random() * 100), 10_000);
          await sleep(delay);
          continue;
        }

        if (response.status === 401 || response.status === 403) throw new AuthenticationError(responseText);
        if (response.status === 404) throw new NotFoundError(responseText);
        if (response.status === 409) throw new ConflictError(responseText);
        if (response.status === 429) throw new RateLimitError(responseText);
        if (response.status >= 400 && response.status < 500) throw new ValidationError(responseText);
        throw new ServerError(responseText);
      } catch (error) {
        clearTimeout(timeout);
        if (error instanceof DOMException && error.name === "AbortError") {
          lastError = new TimeoutError(`Request timed out after ${timeoutMs}ms`);
        } else {
          lastError = error;
        }
        if (attempt < retryAttempts) {
          const delay = Math.min(300 * 2 ** attempt + Math.floor(Math.random() * 100), 10_000);
          await sleep(delay);
          continue;
        }
      }
    }

    throw lastError;
  }
}
