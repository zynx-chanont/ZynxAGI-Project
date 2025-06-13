import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Zap, Globe, Heart, Cpu } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import type { Message } from '../../types/chat';
import toast from 'react-hot-toast';

// Constants
const MAX_TEXTAREA_HEIGHT = 120;
const MIN_TEXTAREA_HEIGHT = 52;
const ERROR_MESSAGES = {
  SEND_FAILED: 'เกิดข้อผิดพลาดในการส่งข้อความ กรุณาลองใหม่อีกครั้ง',
  NETWORK_ERROR: 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต',
  VALIDATION_ERROR: 'กรุณากรอกข้อความก่อนส่ง',
  UNKNOWN_ERROR: 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ กรุณาลองใหม่อีกครั้ง'
} as const;

// Logger utility
const logger = {
  error: (message: string, error?: unknown) => {
    console.error(`[ChatInterface Error] ${message}`, error);
    // Here you can add additional logging services like Sentry, LogRocket, etc.
  },
  info: (message: string, data?: unknown) => {
    console.info(`[ChatInterface Info] ${message}`, data);
  },
  warn: (message: string, data?: unknown) => {
    console.warn(`[ChatInterface Warning] ${message}`, data);
  }
};

// Error boundary component
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

// Types
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

// Memoized Components
const Header = memo(({ title, subtitle }: HeaderProps) => (
  <div className="bg-gradient-to-r from-zynx-blue to-zynx-purple text-white p-6 shadow-lg">
    <div className="flex items-center justify-between max-w-7xl mx-auto">
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
          <Bot className="w-7 h-7" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          <p className="text-blue-100 text-sm">{subtitle}</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-blue-100">
          <Globe className="w-5 h-5" />
          <span className="text-sm">Thai-English Bridge</span>
        </div>
        <div className="flex items-center space-x-2 text-blue-100">
          <Heart className="w-5 h-5" />
          <span className="text-sm">Emotional Intelligence</span>
        </div>
        <div className="flex items-center space-x-2 text-blue-100">
          <Cpu className="w-5 h-5" />
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
    gemini: 'bg-blue-100 text-blue-800',
    deeja: 'bg-purple-100 text-purple-800'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-xs lg:max-w-md xl:max-w-2xl ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-6 py-4 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-r from-zynx-blue to-zynx-purple text-white'
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
                    {message.aiPlatform?.toUpperCase()}
                  </span>
                </div>
                
                <div className="flex items-center space-x-4">
                  {message.culturalScore && (
                    <div className="flex items-center space-x-1 text-thai-gold">
                      <Globe className="w-3 h-3" />
                      <span className="font-medium">{Math.round(message.culturalScore * 100)}%</span>
                    </div>
                  )}
                  {message.emotionalScore && (
                    <div className="flex items-center space-x-1 text-pink-600">
                      <Heart className="w-3 h-3" />
                      <span className="font-medium">{Math.round(message.emotionalScore * 100)}%</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className={`text-xs text-gray-500 mt-2 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString('th-TH', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
      
      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isUser ? 'order-1 mr-4' : 'order-2 ml-4'}`}>
        {isUser ? (
          <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
    </motion.div>
  );
});

const TypingIndicator = memo(() => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="flex justify-start"
  >
    <div className="flex items-center space-x-4">
      <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="bg-white border border-gray-200 rounded-2xl px-6 py-4 shadow-sm">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  </motion.div>
));

const ChatInterface: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { messages, sendMessage, isLoading, error } = useChat();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    try {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
      logger.error('Failed to scroll to bottom', error);
    }
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    try {
      const textarea = textareaRef.current;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
      }
    } catch (error) {
      logger.error('Failed to resize textarea', error);
    }
  }, [inputMessage]);

  // Show error toast if API call fails
  useEffect(() => {
    if (error) {
      const errorMessage = typeof error === 'string' ? error : ERROR_MESSAGES.UNKNOWN_ERROR;
      logger.error('API call failed', error);
      toast.error(errorMessage);
    }
  }, [error]);

  // Reset retry count when message is sent successfully
  useEffect(() => {
    if (!isLoading && !error) {
      setRetryCount(0);
    }
  }, [isLoading, error]);

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
      logger.info('Sending message', { messageLength: inputMessage.length });
      
      await sendMessage(inputMessage);
      
      setInputMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
      }
      
      logger.info('Message sent successfully');
    } catch (error) {
      const isNetworkError = error instanceof TypeError && error.message.includes('fetch');
      const errorMessage = isNetworkError ? ERROR_MESSAGES.NETWORK_ERROR : ERROR_MESSAGES.SEND_FAILED;
      
      logger.error('Failed to send message', error);
      toast.error(errorMessage);

      // Implement retry logic
      if (retryCount < 3) {
        setRetryCount(prev => prev + 1);
        logger.info('Retrying message send', { retryCount: retryCount + 1 });
        setTimeout(handleSendMessage, 1000 * Math.pow(2, retryCount)); // Exponential backoff
      }
    } finally {
      setIsSending(false);
    }
  }, [inputMessage, isLoading, isSending, sendMessage, retryCount]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    try {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    } catch (error) {
      logger.error('Error in key press handler', error);
    }
  }, [handleSendMessage]);

  const quickInfoItems = [
    { icon: Zap, text: 'Smart AI Selection', color: 'text-zynx-purple' },
    { icon: Globe, text: 'Cultural Intelligence', color: 'text-thai-gold' },
    { icon: Heart, text: 'Emotional Awareness', color: 'text-pink-500' }
  ];

  return (
    <ChatErrorBoundary>
      <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header 
          title="ZynxAGI"
          subtitle="Universal AI with Cultural Intelligence • น้องดีจ้า"
        />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full">
          <div className="space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </AnimatePresence>
            
            {(isLoading || isSending) && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-6 shadow-lg">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message... (คุณสามารถพิมพ์เป็นภาษาไทยหรือภาษาอังกฤษได้เลยค่ะ) 💬"
                  className="w-full resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-zynx-blue focus:border-transparent transition-all duration-200 thai-text"
                  rows={1}
                  style={{ minHeight: `${MIN_TEXTAREA_HEIGHT}px`, maxHeight: `${MAX_TEXTAREA_HEIGHT}px` }}
                  disabled={isLoading || isSending}
                  aria-label="Message input"
                />
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading || isSending}
                className="bg-gradient-to-r from-zynx-blue to-zynx-purple text-white p-3 rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 min-w-[52px] h-[52px] flex items-center justify-center"
                aria-label="Send message"
              >
                {(isLoading || isSending) ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" role="status">
                    <span className="sr-only">Sending...</span>
                  </div>
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </motion.button>
            </div>
            
            <QuickInfo items={quickInfoItems} />
          </div>
        </div>
      </div>
    </ChatErrorBoundary>
  );
};

export default memo(ChatInterface); 