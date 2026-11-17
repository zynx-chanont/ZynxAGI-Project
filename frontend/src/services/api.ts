import {
  buildApiUrl,
  DEFAULT_API_TIMEOUT_MS,
  fetchWithTimeout,
} from '../config/api';
import type {
  APIResponse,
  ChatError,
  ChatRequest,
  ChatResponse,
  CulturalAnalysis,
} from '../types/chat';

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_API_TIMEOUT_MS
): Promise<T> {
  const response = await fetchWithTimeout(
    buildApiUrl(path),
    {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    },
    timeoutMs
  );

  if (!response.ok) {
    let detail = `HTTP error! status: ${response.status}`;
    try {
      const errBody = (await response.json()) as { detail?: string; message?: string };
      detail = errBody.detail || errBody.message || detail;
    } catch {
      // Ignore non-JSON error responses
    }
    const apiError: ChatError = {
      code: response.status.toString(),
      message: detail,
      timestamp: new Date(),
    };
    throw apiError;
  }

  return (await response.json()) as T;
}

function wrapResponse<T>(payload: T | APIResponse<T>): APIResponse<T> {
  if (
    payload &&
    typeof payload === 'object' &&
    'data' in payload &&
    'success' in payload
  ) {
    return payload as APIResponse<T>;
  }
  return {
    success: true,
    data: payload as T,
    metadata: {
      timestamp: new Date(),
      processingTime: 0,
      apiVersion: 'v1',
    },
  };
}

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<APIResponse<ChatResponse>> {
    const raw = await requestJson<ChatResponse | APIResponse<ChatResponse>>(
      '/api/v1/chat/message',
      {
        method: 'POST',
        body: JSON.stringify({
          message: request.message,
          conversation_history: request.conversationHistory.map((msg) => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
          })),
          cultural_context: request.culturalContext,
        }),
      }
    );
    return wrapResponse(raw);
  },

  async getCulturalAnalysis(text: string): Promise<APIResponse<CulturalAnalysis>> {
    const raw = await requestJson<CulturalAnalysis | APIResponse<CulturalAnalysis>>(
      '/api/v1/cultural/analyze',
      {
        method: 'POST',
        body: JSON.stringify({ text }),
      }
    );
    return wrapResponse(raw);
  },

  async healthCheck(): Promise<APIResponse<{ status: string; version: string; mode?: string }>> {
    const raw = await requestJson<{ status: string; version: string; mode?: string }>(
      '/api/v1/health',
      { method: 'GET' },
      5000
    );
    return wrapResponse(raw);
  },

  async checkApiAvailability(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  },
};

export type { APIResponse, ChatError, ChatRequest, ChatResponse };
