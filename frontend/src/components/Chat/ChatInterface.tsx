import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import { useChat } from '../../hooks/useChat';
import type { Message } from '../../types/chat';
import toast from 'react-hot-toast';

const MAX_TEXTAREA_HEIGHT = 120;
const MIN_TEXTAREA_HEIGHT = 52;
const ERROR_MESSAGES = {
  SEND_FAILED: 'เกิดข้อผิดพลาดในการส่งข้อความ กรุณาลองใหม่อีกครั้ง',
  NETWORK_ERROR: 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต',
  VALIDATION_ERROR: 'กรุณากรอกข้อความก่อนส่ง',
  UNKNOWN_ERROR: 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ กรุณาลองใหม่อีกครั้ง',
} as const;

const logger = {
  error: (message: string, error?: unknown) => {
    console.error(`[ChatInterface Error] ${message}`, error);
  },
  info: (message: string, data?: unknown) => {
    console.info(`[ChatInterface Info] ${message}`, data);
  },
  warn: (message: string, data?: unknown) => {
    console.warn(`[ChatInterface Warning] ${message}`, data);
  },
};

const GlobeIcon = ({ className = 'w-4 h-4' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
);

const HeartIcon = ({ className = 'w-4 h-4' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

const CpuIcon = ({ className = 'w-4 h-4' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <rect x="4" y="4" width="16" height="16" rx="2" />
    <rect x="9" y="9" width="6" height="6" />
  </svg>
);

const ZapIcon = ({ className = 'w-4 h-4' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

const BotIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <rect x="3" y="8" width="18" height="12" rx="2" />
    <path d="M12 2v6M9 14h.01M15 14h.01" />
  </svg>
);

const UserIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const SendIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

class ChatErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error('Chat interface crashed', { error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-screen bg-red-50">
          <div className="p-6 bg-white rounded-lg shadow-lg max-w-md">
            <h2 className="text-xl font-bold text-red-600 mb-4">ขออภัย เกิดข้อผิดพลาด</h2>
            <p className="text-gray-600 mb-4">
              ระบบกำลังประสบปัญหา กรุณารีเฟรชหน้าเว็บหรือลองใหม่อีกครั้ง
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              รีเฟรชหน้าเว็บ
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

interface HeaderProps {
  title: string;
  subtitle: string;
}

interface QuickInfoItem {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
  color: string;
}

interface QuickInfoProps {
  items: QuickInfoItem[];
}

const Header = memo(({ title, subtitle }: HeaderProps) => (
  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-lg">
    <div className="flex items-center justify-between max-w-7xl mx-auto">
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
          <BotIcon className="w-7 h-7" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          <p className="text-blue-100 text-sm">{subtitle}</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-blue-100">
          <GlobeIcon className="w-5 h-5" />
          <span className="text-sm">Thai-English Bridge</span>
        </div>
        <div className="flex items-center space-x-2 text-blue-100">
          <HeartIcon className="w-5 h-5" />
          <span className="text-sm">Emotional Intelligence</span>
        </div>
        <div className="flex items-center space-x-2 text-blue-100">
          <CpuIcon className="w-5 h-5" />
          <span className="text-sm">Multi-AI Orchestration</span>
        </div>
      </div>
    </div>
  </div>
));

const QuickInfo = memo(({ items }: QuickInfoProps) => (
  <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
    <div className="flex items-center space-x-6">
      {items.map((item, index) => {
        const Icon = item.icon;
        return (
          <span key={index} className="flex items-center space-x-2">
            <Icon className={`w-4 h-4 ${item.color}`} />
            <span>{item.text}</span>
          </span>
        );
      })}
    </div>

    <div className="text-xs text-gray-400">
      Press Enter to send • Shift+Enter for new line
    </div>
  </div>
));

const MessageBubble = memo(({ message }: { message: Message }) => {
  const isUser = message.role === 'user';

  const aiPlatformColors = {
    claude: 'bg-orange-100 text-orange-800',
    openai: 'bg-green-100 text-green-800',
    google: 'bg-blue-100 text-blue-800',
    deeja: 'bg-purple-100 text-purple-800',
    mock: 'bg-amber-100 text-amber-800',
  };

  return (
    <div className={`flex slide-up ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-2xl ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-6 py-4 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
              : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
          }`}
        >
          <div className="whitespace-pre-wrap thai-text leading-relaxed">{message.content}</div>

          {!isUser && message.aiPlatform && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      aiPlatformColors[message.aiPlatform as keyof typeof aiPlatformColors] ||
                      'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {message.aiPlatform.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className={`text-xs text-gray-500 mt-2 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString('th-TH', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center ${
          isUser ? 'order-1 mr-4' : 'order-2 ml-4'
        }`}
      >
        {isUser ? (
          <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
            <UserIcon className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
            <BotIcon className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
    </div>
  );
});

const TypingIndicator = memo(() => (
  <div className="flex justify-start slide-up">
    <div className="flex items-center space-x-4">
      <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
        <BotIcon className="w-5 h-5 text-white" />
      </div>
      <div className="bg-white border border-gray-200 rounded-2xl px-6 py-4 shadow-sm">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  </div>
));

const ChatInterface: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { messages, sendMessage, isLoading, error } = useChat();

  useEffect(() => {
    try {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      logger.error('Failed to scroll to bottom', err);
    }
  }, [messages]);

  useEffect(() => {
    try {
      const textarea = textareaRef.current;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
      }
    } catch (err) {
      logger.error('Failed to resize textarea', err);
    }
  }, [inputMessage]);

  useEffect(() => {
    if (error) {
      const messageText = typeof error === 'string' ? error : ERROR_MESSAGES.UNKNOWN_ERROR;
      logger.error('API call failed', error);
      toast.error(messageText);
    }
  }, [error]);

  const handleSendMessage = useCallback(async () => {
    if (!inputMessage.trim()) {
      logger.warn('Attempted to send empty message');
      toast.error(ERROR_MESSAGES.VALIDATION_ERROR);
      return;
    }

    if (isLoading || isSending) {
      logger.warn('Attempted to send message while another is in progress');
      return;
    }

    try {
      setIsSending(true);
      await sendMessage(inputMessage);
      setInputMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
      }
    } catch (err) {
      const isNetworkError = err instanceof TypeError;
      toast.error(isNetworkError ? ERROR_MESSAGES.NETWORK_ERROR : ERROR_MESSAGES.SEND_FAILED);
    } finally {
      setIsSending(false);
    }
  }, [inputMessage, isLoading, isSending, sendMessage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        void handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  const quickInfoItems = [
    { icon: ZapIcon, text: 'Smart AI Selection', color: 'text-purple-600' },
    { icon: GlobeIcon, text: 'Cultural Intelligence', color: 'text-amber-600' },
    { icon: HeartIcon, text: 'Emotional Awareness', color: 'text-pink-500' },
  ];

  return (
    <ChatErrorBoundary>
      <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header
          title="ZynxAGI"
          subtitle="Universal AI with Cultural Intelligence • น้องดีจ้า"
        />

        <div className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full">
          <div className="space-y-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {(isLoading || isSending) && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="border-t bg-white p-6 shadow-lg">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message... (คุณสามารถพิมพ์เป็นภาษาไทยหรือภาษาอังกฤษได้เลยค่ะ) 💬"
                  className="w-full resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 thai-text"
                  rows={1}
                  style={{ minHeight: `${MIN_TEXTAREA_HEIGHT}px`, maxHeight: `${MAX_TEXTAREA_HEIGHT}px` }}
                  disabled={isLoading || isSending}
                  aria-label="Message input"
                />
              </div>

              <button
                type="button"
                onClick={() => void handleSendMessage()}
                disabled={!inputMessage.trim() || isLoading || isSending}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 min-w-[52px] h-[52px] flex items-center justify-center"
                aria-label="Send message"
              >
                {isLoading || isSending ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" role="status">
                    <span className="sr-only">Sending...</span>
                  </div>
                ) : (
                  <SendIcon className="w-5 h-5" />
                )}
              </button>
            </div>

            <QuickInfo items={quickInfoItems} />
          </div>
        </div>
      </div>
    </ChatErrorBoundary>
  );
};

export default memo(ChatInterface);
