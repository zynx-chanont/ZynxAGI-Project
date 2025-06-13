export type MessageRole = 'assistant' | 'user'

export interface CulturalContext {
  context: string
  explanation: string
}

export interface EmotionalIntelligence {
  sentiment: 'positive' | 'negative' | 'neutral'
  empathy: number
}

export interface Message {
  id: string
  content: string
  role: MessageRole
  timestamp: Date
  culturalContext: CulturalContext
  emotionalIntelligence: EmotionalIntelligence
}

export interface UseChatReturn {
  messages: Message[]
  isLoading: boolean
  error: string | null
  sendMessage: (content: string) => Promise<void>
  clearChat: () => void
  retryLastMessage: () => Promise<void>
  lastMessageId: string
}

export interface ChatRequest {
  message: string;
  conversationHistory: Message[];
  culturalContext?: CulturalContext;
}

export interface ChatResponse {
  message: string;
  aiPlatform: string;
  culturalContext: CulturalContext;
  culturalAccuracyScore: number;
  emotionalIntelligenceScore: number;
  processingTime: number;
}

// Additional types for enhanced functionality
export type FormalityLevel = 'formal' | 'semi-formal' | 'informal';
export type CommunicationStyle = 'direct' | 'indirect' | 'contextual';
export type CulturalMarker = 'kreng_jai' | 'sanuk' | 'mai_pen_rai' | 'greng_jai' | 'bun_khun';

export interface CulturalAnalysis {
  detectedCulture: string;
  confidence: number;
  markers: {
    marker: CulturalMarker;
    confidence: number;
    context: string;
  }[];
  suggestions: string[];
}

export interface EmotionalAnalysis {
  sentiment: 'positive' | 'neutral' | 'negative';
  intensity: number;
  emotions: {
    emotion: string;
    score: number;
  }[];
}

export interface MessageMetadata {
  language: string;
  detectedLanguage: string;
  languageConfidence: number;
  culturalAnalysis?: CulturalAnalysis;
  emotionalAnalysis?: EmotionalAnalysis;
  processingMetadata: {
    startTime: Date;
    endTime: Date;
    platform: string;
    model: string;
  };
}

// Extended Message interface with metadata
export interface EnhancedMessage extends Message {
  metadata?: MessageMetadata;
}

// API Response types
export interface APIResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  metadata: {
    timestamp: Date;
    processingTime: number;
    apiVersion: string;
  };
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'message' | 'typing' | 'error' | 'system';
  payload: Message | string | Error;
  timestamp: Date;
}

// Error types
export interface ChatError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: Date;
  context?: {
    messageId?: string;
    conversationId?: string;
    platform?: string;
  };
}

// Configuration types
export interface ChatConfig {
  apiEndpoint: string;
  wsEndpoint: string;
  defaultCulture: string;
  supportedLanguages: string[];
  maxHistoryLength: number;
  timeout: number;
  retryAttempts: number;
  culturalAnalysisEnabled: boolean;
  emotionalAnalysisEnabled: boolean;
}

// State management types
export interface ChatState {
  messages: EnhancedMessage[];
  isLoading: boolean;
  error: ChatError | null;
  lastMessageId: string | null;
  conversationId: string;
  culturalContext: CulturalContext;
  metadata: {
    startTime: Date;
    lastUpdate: Date;
    messageCount: number;
    averageResponseTime: number;
  };
} 