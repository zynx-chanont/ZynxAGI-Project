import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Toaster } from 'react-hot-toast';
import {
  buildApiUrl,
  DEFAULT_API_TIMEOUT_MS,
  fetchWithTimeout,
  isApiConfigured,
} from './config/api';
import './index.css';

type ConnectionStatus = 'checking' | 'live' | 'mock' | 'unavailable' | 'unconfigured';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  mode?: 'live' | 'mock' | 'fallback';
  isMock?: boolean;
  aiPlatform?: string;
}

interface ChatApiResponse {
  message?: string;
  aiPlatform?: string;
  model?: string;
  mode?: 'live' | 'mock' | 'fallback';
  isMock?: boolean;
  providerError?: string | null;
}

interface HealthApiResponse {
  status?: string;
  mode?: 'live' | 'mock';
  ai_provider?: {
    provider?: string;
    configured?: boolean;
  };
}

function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        'สวัสดีค่ะ! ยินดีต้อนรับสู่ ZynxAGI 🌟 ฉันคือ Deeja น้องดีจ้า พร้อมช่วยเหลือคุณด้วยความฉลาดทางวัฒนธรรม! ลองพิมพ์อะไรมาดูสิคะ ✨',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastFailedInput, setLastFailedInput] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(
    isApiConfigured() ? 'checking' : 'unconfigured'
  );
  const [activeProvider, setActiveProvider] = useState<string>('mock');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkBackendHealth = useCallback(async () => {
    if (!isApiConfigured()) {
      setConnectionStatus('unconfigured');
      return;
    }

    try {
      const response = await fetchWithTimeout(
        buildApiUrl('/api/v1/health'),
        { method: 'GET' },
        5000
      );
      if (!response.ok) {
        setConnectionStatus('unavailable');
        return;
      }
      const data = (await response.json()) as HealthApiResponse;
      if (data.mode === 'live' && data.ai_provider?.configured) {
        setConnectionStatus('live');
        setActiveProvider(data.ai_provider.provider || 'live');
      } else {
        setConnectionStatus('mock');
        setActiveProvider(data.ai_provider?.provider || 'mock');
      }
    } catch {
      setConnectionStatus('unavailable');
    }
  }, []);

  useEffect(() => {
    void checkBackendHealth();
  }, [checkBackendHealth]);

  const submitMessage = async (rawText: string, appendUserBubble: boolean) => {
    const trimmed = rawText.trim();
    if (!trimmed || isLoading) return;

    if (!isApiConfigured()) {
      setConnectionStatus('unconfigured');
      setErrorMessage(
        'ยังไม่ได้ตั้งค่า Backend URL (VITE_API_URL) ในสภาพแวดล้อมการ Deploy กรุณาตั้งค่า VITE_API_URL ใน Netlify'
      );
      setLastFailedInput(trimmed);
      return;
    }

    if (appendUserBubble) {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: trimmed,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setMessage('');
    }

    setErrorMessage(null);
    setLastFailedInput(null);
    setIsLoading(true);

    try {
      const response = await fetchWithTimeout(
        buildApiUrl('/api/v1/chat/message'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: trimmed,
            conversation_history: messages.slice(-10).map((item) => ({
              role: item.role,
              content: item.content,
            })),
          }),
        },
        DEFAULT_API_TIMEOUT_MS
      );

      if (!response.ok) {
        let serverDetail = `HTTP ${response.status}`;
        try {
          const errPayload = (await response.json()) as { detail?: string };
          if (errPayload.detail) {
            serverDetail = `${serverDetail}: ${errPayload.detail}`;
          }
        } catch {
          // Keep status-based detail when body is not JSON
        }
        throw new Error(`เซิร์ฟเวอร์ตอบกลับผิดพลาด (${serverDetail})`);
      }

      const data = (await response.json()) as ChatApiResponse;
      const resolvedMode: 'live' | 'mock' | 'fallback' =
        data.mode || (data.isMock ? 'mock' : 'live');
      const isMockReply = Boolean(data.isMock ?? resolvedMode !== 'live');

      setConnectionStatus(isMockReply ? 'mock' : 'live');
      if (data.aiPlatform) {
        setActiveProvider(data.aiPlatform);
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || 'ขออภัยค่ะ ไม่สามารถสร้างคำตอบได้ในขณะนี้',
        timestamp: new Date(),
        mode: resolvedMode,
        isMock: isMockReply,
        aiPlatform: data.aiPlatform,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const isTimeout = error instanceof DOMException && error.name === 'AbortError';
      const isNetworkFailure = error instanceof TypeError;

      if (isNetworkFailure || isTimeout) {
        setConnectionStatus('unavailable');
      }

      const friendlyError = isTimeout
        ? 'การเชื่อมต่อ Backend หมดเวลา (Timeout) กรุณาลองใหม่อีกครั้ง'
        : isNetworkFailure
          ? 'ไม่สามารถเชื่อมต่อกับ Backend ได้ในขณะนี้ กรุณาตรวจสอบสถานะ Backend หรือการตั้งค่า VITE_API_URL และ CORS'
          : error instanceof Error
            ? error.message
            : 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุในการส่งข้อความ';

      setErrorMessage(friendlyError);
      setLastFailedInput(trimmed);

      const fallbackNotice: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `ขออภัยค่ะ ${friendlyError} 🙏`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, fallbackNotice]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    await submitMessage(message, true);
  };

  const retryLastMessage = async () => {
    if (lastFailedInput && !isLoading) {
      await submitMessage(lastFailedInput, false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  };

  const statusBadge = (() => {
    switch (connectionStatus) {
      case 'live':
        return {
          className: 'status-badge status-live',
          label: `Live AI (${activeProvider})`,
        };
      case 'mock':
        return {
          className: 'status-badge status-mock',
          label: 'Backend Mock Mode',
        };
      case 'unavailable':
        return {
          className: 'status-badge status-error',
          label: 'Backend Unavailable',
        };
      case 'unconfigured':
        return {
          className: 'status-badge status-error',
          label: 'API URL Not Configured',
        };
      default:
        return {
          className: 'status-badge',
          label: 'Checking Backend...',
        };
    }
  })();

  return (
    <div>
      <header className="header">
        <div className="container header-row">
          <div>
            <h1>ZynxAGI</h1>
            <p>
              Beyond Intelligence. Into Understanding. • น้องดีจ้า 🤖💫
            </p>
          </div>
          <div className={statusBadge.className} role="status" aria-live="polite">
            <span>●</span>
            <span>{statusBadge.label}</span>
          </div>
        </div>
      </header>

      <main className="chat-container">
        {errorMessage && (
          <div className="error-banner" role="alert">
            <span>{errorMessage}</span>
            {lastFailedInput && (
              <button
                type="button"
                className="retry-button"
                onClick={() => void retryLastMessage()}
                disabled={isLoading}
              >
                ลองใหม่
              </button>
            )}
          </div>
        )}

        <div className="messages-area" aria-label="Chat messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role} slide-up`}>
              <div
                className={`message-avatar ${
                  msg.role === 'user' ? 'avatar-user' : 'avatar-assistant'
                }`}
                aria-hidden="true"
              >
                {msg.role === 'user' ? 'U' : 'D'}
              </div>

              <div
                className={`message-bubble ${
                  msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'
                }`}
              >
                <div className="thai-text">{msg.content}</div>
                <div className="message-meta">
                  <span className="message-time">
                    {msg.timestamp.toLocaleTimeString('th-TH', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                  {msg.role === 'assistant' && msg.mode && (
                    <span
                      className={`mode-pill ${
                        msg.isMock ? 'mode-pill-mock' : 'mode-pill-live'
                      }`}
                    >
                      {msg.mode === 'live'
                        ? `AI: ${msg.aiPlatform || 'live'}`
                        : msg.mode === 'fallback'
                          ? 'Fallback Mode'
                          : 'Mock Mode'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant" aria-label="Assistant is typing">
              <div className="message-avatar avatar-assistant" aria-hidden="true">
                D
              </div>
              <div className="message-bubble bubble-assistant">
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-container">
            <textarea
              className="message-input thai-text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="พิมพ์ข้อความ... Type your message..."
              aria-label="Message input"
              disabled={isLoading}
              rows={1}
            />
            <button
              type="button"
              className="send-button"
              onClick={() => void sendMessage()}
              disabled={!message.trim() || isLoading}
              aria-label="Send message"
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>

          <div className="input-info">
            <div className="features">
              <span className="feature">🌍 Cultural Intelligence</span>
              <span className="feature">💝 Emotional Awareness</span>
              <span className="feature">⚡ Multi-AI</span>
            </div>
            <span>Enter to send • Shift+Enter for new line</span>
          </div>
        </div>
      </main>

      <Toaster position="top-right" />
    </div>
  );
}

export default App;
