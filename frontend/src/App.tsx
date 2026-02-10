import React, { useState, useRef, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { Analytics } from '@vercel/analytics/react';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'สวัสดีค่ะ! ยินดีต้อนรับสู่ ZynxAGI 🌟 ฉันคือ Deeja น้องดีจ้า พร้อมช่วยเหลือคุณด้วยความฉลาดทางวัฒนธรรม! ลองพิมพ์อะไรมาดูสิคะ ✨',
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || 'ขออภัยค่ะ ไม่สามารถตอบได้ในขณะนี้',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาตรวจสอบว่า Backend รันอยู่หรือไม่ 🙏',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="header">
        <div className="container">
          <h1>ZynxAGI</h1>
          <p>Universal AI Orchestration Platform with Cultural Intelligence • น้องดีจ้า 🤖💫</p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role} slide-up`}>
              <div className={`message-avatar ${msg.role === 'user' ? 'avatar-user' : 'avatar-assistant'}`}>
                {msg.role === 'user' ? 'U' : 'D'}
              </div>
              
              <div className={`message-bubble ${msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'}`}>
                <div className="thai-text">{msg.content}</div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString('th-TH', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar avatar-assistant">D</div>
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

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              className="message-input thai-text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="พิมพ์ข้อความ... Type your message..."
              disabled={isLoading}
              rows={1}
            />
            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!message.trim() || isLoading}
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
      </div>

      <Toaster position="top-right" />
      <Analytics />
    </div>
  );
}

export default App;
