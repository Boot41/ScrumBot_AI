import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Chat } from '../Chat';
import { api } from '../../services/api';

// Mock the api service
jest.mock('../../services/api', () => ({
  api: {
    startConversation: jest.fn(),
    sendMessage: jest.fn(),
    processAudio: jest.fn(),
    speak: jest.fn(),
  },
}));

describe('Chat Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock responses
    (api.startConversation as jest.Mock).mockResolvedValue({
      success: true,
      message: 'Hi! What did you work on yesterday?',
      speech_segments: ['Hi!', 'What did you work on yesterday?'],
    });
    
    (api.sendMessage as jest.Mock).mockResolvedValue({
      success: true,
      message: 'Thanks for the update. What are you working on today?',
      stage: 'today',
    });
    
    (api.speak as jest.Mock).mockResolvedValue(new Blob());
  });

  test('renders initial greeting message', async () => {
    render(<Chat />);
    
    await waitFor(() => {
      expect(screen.getByText('Hi! What did you work on yesterday?')).toBeInTheDocument();
    });
    
    expect(api.startConversation).toHaveBeenCalledTimes(1);
  });

  test('handles user message submission', async () => {
    render(<Chat />);
    
    // Wait for initial greeting
    await waitFor(() => {
      expect(api.startConversation).toHaveBeenCalled();
    });
    
    // Find and fill the input
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'I worked on SCRUM-123' } });
    
    // Find and click the send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalledWith('I worked on SCRUM-123', 'greeting');
      expect(screen.getByText('Thanks for the update. What are you working on today?')).toBeInTheDocument();
    });
  });

  test('displays error message on API failure', async () => {
    // Mock API failure
    (api.sendMessage as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    render(<Chat />);
    
    // Wait for initial greeting
    await waitFor(() => {
      expect(api.startConversation).toHaveBeenCalled();
    });
    
    // Send a message
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/error processing your message/i)).toBeInTheDocument();
    });
  });

  test('handles voice recording', async () => {
    (api.processAudio as jest.Mock).mockResolvedValue({
      success: true,
      message: 'Processed audio response',
      transcript: 'Test transcript',
    });
    
    render(<Chat />);
    
    // Find and click the microphone button
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    // Mock audio recording
    const stopButton = await screen.findByRole('button', { name: /stop/i });
    fireEvent.click(stopButton);
    
    await waitFor(() => {
      expect(api.processAudio).toHaveBeenCalled();
      expect(screen.getByText('Processed audio response')).toBeInTheDocument();
    });
  });

  test('shows typing indicator while processing', async () => {
    render(<Chat />);
    
    // Delay the API response
    (api.sendMessage as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    // Send a message
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    // Check for typing indicator
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });

  test('scrolls to bottom on new messages', async () => {
    const scrollIntoViewMock = jest.fn();
    window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;
    
    render(<Chat />);
    
    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalled();
    });
    
    // Send a message
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalledTimes(2);
    });
  });
});
