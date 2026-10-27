import type { ErrorResponse, ErrorCode } from '../types/contract';

export class ApiError extends Error {
  code: ErrorCode;
  retryAfter: number | null;

  constructor(code: ErrorCode, message: string, retryAfter: number | null = null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.retryAfter = retryAfter;
  }
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  let response: Response;

  try {
    response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });
  } catch (err) {
    if ((err as Error).name === 'AbortError') {
      throw err;
    }
    throw new ApiError('UPSTREAM_ERROR', `Network connection failed: ${(err as Error).message}`);
  }

  if (!response.ok) {
    let errorData: ErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Non-JSON response
    }

    if (errorData?.error) {
      throw new ApiError(
        errorData.error.code,
        errorData.error.message,
        errorData.error.retry_after
      );
    }

    throw new ApiError(
      'UPSTREAM_ERROR',
      `Server responded with HTTP error status: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}
