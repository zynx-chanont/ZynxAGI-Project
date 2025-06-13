import { useState, useCallback, useRef } from 'react';
import type { Message, ChatRequest, ChatResponse, ChatError } from '../types/chat';
import { chatService } from '../services/api';
import toast from 'react-hot-toast';

interface UseChatReturn {
  messages: Message[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  clearChat: () => void;
  retryLastMessage: () => Promise<void>;
  lastMessageId: string | null;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'สวัสดีค่ะ! ยินดีต้อนรับสู่ ZynxAGI 🌟 ฉันคือ Deeja น้องดีจ้าที่จะช่วยคุณเชื่อมต่อกับ AI ที่เหมาะสมที่สุดพร้อมความเข้าใจทางวัฒนธรรม How can I help you today?',
      timestamp: new Date(),
      culturalContext: {
        primaryCulture: 'thai',
        formalityLevel: 'casual',
        politenessLevel: 0.8,
        culturalMarkers: ['ค่ะ', 'kreng_jai'],
        communicationStyle: 'warm_friendly'
      },
      aiPlatform: 'deeja',
      culturalScore: 0.95,
      emotionalScore: 0.88
    }
  ]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastMessageRef = useRef<string | null>(null);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    lastMessageRef.current = null;
  }, []);

  const handleError = useCallback((err: unknown) => {
    let errorMessage: string;
    
    if (err instanceof Error) {
      errorMessage = err.message;
    } else if (typeof err === 'string') {
      errorMessage = err;
    } else {
      errorMessage = 'เกิดข้อผิดพลาดในการส่งข้อความ';
    }

    setError(errorMessage);
    toast.error(errorMessage, {
      duration: 4000,
      position: 'top-center',
      style: {
        background: '#FEE2E2',
        color: '#991B1B',
        padding: '16px',
        borderRadius: '8px',
      },
    });
    console.error('Chat error:', err);
  }, []);

  const sendMessage = useCallback(async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    lastMessageRef.current = messageContent;

    try {
      // Send to ZynxAGI backend
      const response = await chatService.sendMessage({
        message: messageContent,
        conversationHistory: messages,
        culturalContext: {
          primaryCulture: 'thai',
          formalityLevel: 'auto',
          politenessLevel: 0.8,
          culturalMarkers: [],
          communicationStyle: 'auto'
        }
      });

      // Add AI response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(),
        culturalContext: response.data.culturalContext,
        aiPlatform: response.data.aiPlatform,
        culturalScore: response.data.culturalAccuracyScore,
        emotionalScore: response.data.emotionalIntelligenceScore
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Show success toast for cultural accuracy
      if (response.data.culturalAccuracyScore > 0.9) {
        toast.success('Cultural context perfectly matched! 🎯', {
          duration: 2000,
          position: 'top-center',
          style: {
            background: '#ECFDF5',
            color: '#065F46',
            padding: '16px',
            borderRadius: '8px',
          },
        });
      }
      
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading, handleError]);

  const retryLastMessage = useCallback(async () => {
    if (lastMessageRef.current) {
      await sendMessage(lastMessageRef.current);
    }
  }, [sendMessage]);

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    clearChat,
    retryLastMessage,
    lastMessageId: lastMessageRef.current
  };
};

export default useChat; 