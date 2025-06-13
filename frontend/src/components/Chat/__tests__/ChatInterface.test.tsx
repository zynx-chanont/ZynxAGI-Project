import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInterface from '../ChatInterface'
import { useChat } from '../../../hooks/useChat'
import { toast } from 'react-hot-toast'
import '@testing-library/jest-dom'
import type { Message, UseChatReturn } from '../../../types/chat'

// Mock the useChat hook
jest.mock('../../../hooks/useChat')
const mockUseChat = useChat as jest.MockedFunction<typeof useChat>

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}))

describe('ChatInterface', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      content: 'สวัสดีครับ',
      role: 'assistant' as const,
      timestamp: new Date(),
      culturalContext: {
        context: 'thai',
        explanation: 'คำทักทายแบบไทย',
      },
      emotionalIntelligence: {
        sentiment: 'positive',
        empathy: 0.9,
      },
    },
  ]

  const mockSendMessage = jest.fn()
  const mockClearChat = jest.fn()
  const mockRetryLastMessage = jest.fn()

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks()

    // Setup default mock implementation
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      isLoading: false,
      error: null,
      sendMessage: mockSendMessage,
      clearChat: mockClearChat,
      retryLastMessage: mockRetryLastMessage,
      lastMessageId: '1',
    } as UseChatReturn)
  })

  it('renders chat interface with initial state', () => {
    render(<ChatInterface />)
    
    // Check if header is rendered
    expect(screen.getByText('ZynxAGI')).toBeInTheDocument()
    
    // Check if quick info items are rendered
    expect(screen.getByText('Thai-English Bilingual')).toBeInTheDocument()
    expect(screen.getByText('Cultural Context')).toBeInTheDocument()
    expect(screen.getByText('Emotional Intelligence')).toBeInTheDocument()
    
    // Check if input area is rendered
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('displays messages correctly', () => {
    render(<ChatInterface />)
    
    // Check if message is displayed
    expect(screen.getByText('สวัสดีครับ')).toBeInTheDocument()
    
    // Check if cultural context is displayed
    expect(screen.getByText('คำทักทายแบบไทย')).toBeInTheDocument()
  })

  it('handles sending messages', async () => {
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    // Type and send message
    await userEvent.type(input, 'Hello')
    await userEvent.click(sendButton)
    
    // Check if sendMessage was called
    expect(mockSendMessage).toHaveBeenCalledWith('Hello')
  })

  it('handles empty message validation', async () => {
    render(<ChatInterface />)
    
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    // Try to send empty message
    await userEvent.click(sendButton)
    
    // Check if error toast was shown
    expect(toast.error).toHaveBeenCalledWith('กรุณากรอกข้อความก่อนส่ง')
    expect(mockSendMessage).not.toHaveBeenCalled()
  })

  it('handles loading state', () => {
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      isLoading: true,
      error: null,
      sendMessage: mockSendMessage,
      clearChat: mockClearChat,
      retryLastMessage: mockRetryLastMessage,
      lastMessageId: '1',
    } as UseChatReturn)

    render(<ChatInterface />)
    
    // Check if input is disabled
    expect(screen.getByPlaceholderText('Type your message...')).toBeDisabled()
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled()
  })

  it('handles error state', () => {
    const errorMessage = 'Network error'
    mockUseChat.mockReturnValue({
      messages: mockMessages,
      isLoading: false,
      error: errorMessage,
      sendMessage: mockSendMessage,
      clearChat: mockClearChat,
      retryLastMessage: mockRetryLastMessage,
      lastMessageId: '1',
    } as UseChatReturn)

    render(<ChatInterface />)
    
    // Check if error toast was shown
    expect(toast.error).toHaveBeenCalledWith(errorMessage)
  })

  it('handles clear chat', async () => {
    render(<ChatInterface />)
    
    const clearButton = screen.getByRole('button', { name: /clear/i })
    await userEvent.click(clearButton)
    
    expect(mockClearChat).toHaveBeenCalled()
  })

  it('handles retry last message', async () => {
    render(<ChatInterface />)
    
    const retryButton = screen.getByRole('button', { name: /retry/i })
    await userEvent.click(retryButton)
    
    expect(mockRetryLastMessage).toHaveBeenCalled()
  })

  it('handles textarea auto-resize', async () => {
    render(<ChatInterface />)
    
    const textarea = screen.getByPlaceholderText('Type your message...')
    
    // Type a long message
    const longMessage = 'a'.repeat(1000)
    await userEvent.type(textarea, longMessage)
    
    // Check if textarea height is adjusted
    expect(textarea.style.height).not.toBe('')
  })

  it('handles keyboard shortcuts', async () => {
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    
    // Type message and press Enter
    await userEvent.type(input, 'Hello{enter}')
    
    expect(mockSendMessage).toHaveBeenCalledWith('Hello')
  })

  it('handles copy message', async () => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(),
      },
    })

    render(<ChatInterface />)
    
    const copyButton = screen.getByRole('button', { name: /copy/i })
    await userEvent.click(copyButton)
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('สวัสดีครับ')
    expect(toast.success).toHaveBeenCalledWith('คัดลอกข้อความแล้ว')
  })
}) 