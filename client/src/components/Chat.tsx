import React, { useState, useEffect, useRef } from 'react';
import './Chat.css';
import { BotIcon, UserIcon } from './ChatIcons';
import { motion, AnimatePresence } from 'framer-motion';
import { VoiceRecorder } from './VoiceRecorder';
import { api, ApiResponse } from '../services/api';
import { ProjectSummary } from './ProjectSummary';
import {
  ChatBubbleLeftIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  CommandLineIcon,
  CpuChipIcon,
  SparklesIcon
} from '@heroicons/react/24/solid';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  transcript?: string;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentStage, setCurrentStage] = useState<string>('greeting');
  const [isProcessing, setIsProcessing] = useState(false);
  const [projectSummary, setProjectSummary] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const audioQueueRef = useRef<Array<() => Promise<void>>>([]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const stopCurrentAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
  };

  const playAudio = async (audioBlob: Blob | null): Promise<void> => {
    return new Promise(async (resolve) => {
      try {
        if (!audioBlob) {
          console.warn('No audio data received');
          resolve();
          return;
        }

        // Stop any currently playing audio first
        stopCurrentAudio();

        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Store the current audio element
        currentAudioRef.current = audio;
        
        // Set up event listeners
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          currentAudioRef.current = null;
          resolve();
        };

        audio.onerror = (e) => {
          console.error('Error playing audio:', e);
          URL.revokeObjectURL(audioUrl);
          currentAudioRef.current = null;
          resolve(); // Resolve even on error to continue with next segment
        };

        // Play the audio
        await audio.play();
      } catch (error) {
        console.error('Error playing audio:', error);
        resolve(); // Resolve even on error to continue with next segment
      }
    });
  };

  // Initial greeting
  useEffect(() => {
    const startChat = async () => {
      if (messages.length === 0) {
        try {
          // Get personalized greeting from server
          const response = await api.startConversation();
          
          if (response.success && response.message) {
            // Add initial message to chat
            const botMessage = {
              id: Math.random().toString(36).substr(2, 9),
              text: response.message,
              isUser: false,
              timestamp: new Date()
            };
            setMessages([botMessage]);
            
            // Play greeting audio segments sequentially
            if (response.speech_segments) {
              try {
                // Stop any currently playing audio before starting
                stopCurrentAudio();
                
                for (const segment of response.speech_segments) {
                  const audioBlob = await api.speak(segment);
                  if (audioBlob) {
                    await playAudio(audioBlob);
                    // Add a small pause between segments
                    await new Promise(resolve => setTimeout(resolve, 500));
                  }
                }
              } catch (error) {
                console.error('Error playing greeting:', error);
              }
            }
          }
        } catch (error) {
          console.error('Error starting conversation:', error);
        }
      }
    };
    
    startChat();
  }, []);

  const addMessage = (text: string, isUser: boolean, transcript?: string) => {
    setMessages(prev => [...prev, {
      id: crypto.randomUUID(),
      text,
      isUser,
      timestamp: new Date(),
      transcript
    }]);
  };

  const handleUserMessage = async (text: string) => {
    setIsProcessing(true);
    addMessage(text, true);

    try {
      const response: ApiResponse = await api.sendMessage(text, currentStage);
      if (response.success) {
        if (response.message) {
          handleBotResponse(response.message);
        }
        if (response.stage) {
          setCurrentStage(response.stage);
        }
        if (response.summaryData?.project) {
          setProjectSummary(response.summaryData.project);
        }
      } else {
        handleBotResponse("I'm sorry, I couldn't process your message. Please try again.");
      }
    } catch (error) {
      console.error('Error processing message:', error);
      handleBotResponse("Sorry, there was an error processing your message.");
    }

    setIsProcessing(false);
  };

  const handleAudioMessage = async (audioBlob: Blob) => {
    setIsProcessing(true);

    try {
      const response: ApiResponse = await api.processAudio(audioBlob, currentStage);
      if (response.success) {
        if (response.transcript) {
          addMessage(response.transcript, true);
        }
        if (response.message) {
          handleBotResponse(response.message);
        }
        if (response.stage) {
          setCurrentStage(response.stage);
        }
      } else {
        handleBotResponse("I'm sorry, I couldn't process your audio. Please try again.");
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      handleBotResponse("Sorry, there was an error processing your audio.");
    }

    setIsProcessing(false);
  };

  const handleBotResponse = async (response: string, skipAudio: boolean = false) => {
    try {
      // Add bot message to chat
      const botMessage = {
        id: Math.random().toString(36).substr(2, 9),
        text: response,
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prevMessages => [...prevMessages, botMessage]);

      // Skip audio if requested (for initial greeting)
      if (!skipAudio) {
        // Convert response to speech
        const audioBlob = await api.speak(response);
        if (audioBlob) {
          // Stop any currently playing audio
          if (currentAudioRef.current) {
            currentAudioRef.current.pause();
            currentAudioRef.current = null;
          }
          
          // Play the new audio
          await playAudio(audioBlob);
        }
      }
    } catch (error) {
      console.error('Error handling bot response:', error);
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              variants={messageVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className={`message-group ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`message-bubble ${message.isUser ? 'user' : 'bot'}`}>
                <div className="message-header">
                  {message.isUser ? (
                    <div className="message-sender user">
                      <UserCircleIcon className="w-5 h-5 text-indigo-400" />
                      <span>You</span>
                    </div>
                  ) : (
                    <div className="message-sender bot">
                      <CpuChipIcon className="w-5 h-5 text-blue-400" />
                      <SparklesIcon className="w-4 h-4 text-blue-300 absolute -right-1 -top-1" />
                      <span>AI Assistant</span>
                    </div>
                  )}
                {message.transcript && (
                  <div className="message-text text-gray-300 mb-2">
                    Transcript: {message.transcript}
                  </div>
                )}
                <p className="message-text whitespace-pre-line">{message.text}</p>
                </div>
                <div className="message-time text-gray-400 text-xs">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Project Summary */}
        {projectSummary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <div className="text-xl text-blue-400 font-semibold mb-4">
              Project Status Report
            </div>
            <ProjectSummary data={projectSummary} />
          </motion.div>
        )}
        
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="message-group"
          >
            <div className="typing-indicator">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <VoiceRecorder
          onAudioRecorded={handleAudioMessage}
          onTextSubmitted={handleUserMessage}
          isProcessing={isProcessing}
        />
      </div>
    </div>
  );
};
