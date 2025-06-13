import axios from 'axios';
import type { AxiosError, AxiosInstance } from 'axios';
import type { 
  ChatRequest, 
  ChatResponse, 
  APIResponse, 
  ChatError,
  CulturalAnalysis,
  EmotionalAnalysis 
} from '../types/chat';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

// API Client Configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error Handler
const handleApiError = (error: unknown): ChatError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string }>;
    return {
      code: axiosError.response?.status?.toString() || 'UNKNOWN_ERROR',
      message: axiosError.response?.data?.message || axiosError.message,
      details: axiosError.response?.data as Record<string, unknown>,
      timestamp: new Date(),
      context: {
        messageId: axiosError.config?.headers?.['x-message-id'] as string,
      },
    };
  }
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred',
    timestamp: new Date(),
  };
};

// API Service
export const chatService = {
  async sendMessage(request: ChatRequest): Promise<APIResponse<ChatResponse>> {
    try {
      const response = await apiClient.post<APIResponse<ChatResponse>>('/chat/message', {
        message: request.message,
        user_profile: {
          user_id: 'demo-user',
          cultural_background: 'thai-international',
          preferred_language: 'auto',
          formality_preference: 'auto',
        },
        conversation_history: request.conversationHistory.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          cultural_context: msg.culturalContext,
        })),
        domain: 'general',
        complexity: 'medium',
        estimated_tokens: Math.ceil(request.message.length * 1.5),
        query_hash: btoa(request.message).substring(0, 32),
        cultural_context: request.culturalContext,
      });

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async getCulturalAnalysis(text: string): Promise<APIResponse<CulturalAnalysis>> {
    try {
      const response = await apiClient.post<APIResponse<CulturalAnalysis>>('/cultural/analyze', {
        text,
        options: {
          detect_language: true,
          analyze_emotions: true,
          include_suggestions: true,
        },
      });

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async getEmotionalAnalysis(text: string): Promise<APIResponse<EmotionalAnalysis>> {
    try {
      const response = await apiClient.post<APIResponse<EmotionalAnalysis>>('/emotional/analyze', {
        text,
        options: {
          detect_sentiment: true,
          analyze_emotions: true,
          include_intensity: true,
        },
      });

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  async healthCheck(): Promise<APIResponse<{ status: string; version: string }>> {
    try {
      const response = await apiClient.get<APIResponse<{ status: string; version: string }>>('/health');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Utility method to check API availability
  async checkApiAvailability(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  },
};

// Export types for convenience
export type { ChatRequest, ChatResponse, APIResponse, ChatError }; 