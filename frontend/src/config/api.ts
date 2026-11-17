const DEV_FALLBACK_API_URL = 'http://localhost:8000';
export const DEFAULT_API_TIMEOUT_MS = 15000;

function normalizeBaseUrl(rawUrl: string): string {
  const trimmed = rawUrl.trim().replace(/\/+$/, '');
  if (!trimmed) {
    return '';
  }
  // Support callers that set VITE_API_URL with or without a trailing /api/v1 suffix
  return trimmed.replace(/\/api\/v1$/i, '');
}

export function getRawConfiguredApiUrl(): string {
  return normalizeBaseUrl(
    import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || ''
  );
}

export function isApiConfigured(): boolean {
  // Production uses same-origin Netlify Serverless Functions (/api/v1/*) when VITE_API_URL is unset
  return true;
}

export function getApiBaseUrl(): string {
  const configured = getRawConfiguredApiUrl();
  if (configured) {
    return configured;
  }
  if (import.meta.env.DEV) {
    return DEV_FALLBACK_API_URL;
  }
  return '';
}

export function buildApiUrl(path: string): string {
  const baseUrl = getApiBaseUrl();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return baseUrl ? `${baseUrl}${normalizedPath}` : normalizedPath;
}

export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_API_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const timerId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timerId);
  }
}
