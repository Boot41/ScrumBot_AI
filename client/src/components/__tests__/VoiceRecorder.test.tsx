import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { VoiceRecorder } from '../VoiceRecorder';

// Mock MediaRecorder and getUserMedia
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: jest.fn(),
  onstop: jest.fn(),
};

const mockMediaStream = {
  getTracks: () => [{
    stop: jest.fn()
  }]
};

const mockAudioContext = {
  createMediaStreamSource: jest.fn().mockReturnValue({
    connect: jest.fn()
  }),
  createAnalyser: jest.fn().mockReturnValue({
    connect: jest.fn(),
    frequencyBinCount: 1024,
    getByteFrequencyData: jest.fn()
  })
};

describe('VoiceRecorder Component', () => {
  beforeAll(() => {
    // Mock global objects
    global.MediaRecorder = jest.fn().mockImplementation(() => mockMediaRecorder);
    global.AudioContext = jest.fn().mockImplementation(() => mockAudioContext);
    global.navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue(mockMediaStream)
    };
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockProps = {
    onAudioRecorded: jest.fn(),
    onTextSubmitted: jest.fn(),
    isProcessing: false
  };

  test('renders input field and buttons', () => {
    render(<VoiceRecorder {...mockProps} />);
    
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /microphone/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('handles text input and submission', () => {
    render(<VoiceRecorder {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    expect(mockProps.onTextSubmitted).toHaveBeenCalledWith('Test message');
  });

  test('handles voice recording', async () => {
    render(<VoiceRecorder {...mockProps} />);
    
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    expect(global.navigator.mediaDevices.getUserMedia).toHaveBeenCalled();
    expect(global.MediaRecorder).toHaveBeenCalled();
    expect(mockMediaRecorder.start).toHaveBeenCalled();
    
    const stopButton = await screen.findByRole('button', { name: /stop/i });
    fireEvent.click(stopButton);
    
    expect(mockMediaRecorder.stop).toHaveBeenCalled();
  });

  test('disables controls while processing', () => {
    render(<VoiceRecorder {...mockProps} isProcessing={true} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    const micButton = screen.getByRole('button', { name: /microphone/i });
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    expect(input).toBeDisabled();
    expect(micButton).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  test('shows recording duration', async () => {
    jest.useFakeTimers();
    
    render(<VoiceRecorder {...mockProps} />);
    
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    // Advance timer by 2 seconds
    jest.advanceTimersByTime(2000);
    
    await waitFor(() => {
      expect(screen.getByText('2.0s')).toBeInTheDocument();
    });
    
    jest.useRealTimers();
  });

  test('stops recording after maximum duration', async () => {
    jest.useFakeTimers();
    
    render(<VoiceRecorder {...mockProps} />);
    
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    // Advance timer beyond 30 seconds
    jest.advanceTimersByTime(31000);
    
    expect(mockMediaRecorder.stop).toHaveBeenCalled();
    
    jest.useRealTimers();
  });

  test('handles audio analysis', async () => {
    render(<VoiceRecorder {...mockProps} />);
    
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    expect(mockAudioContext.createAnalyser).toHaveBeenCalled();
    expect(mockAudioContext.createMediaStreamSource).toHaveBeenCalled();
  });
});
