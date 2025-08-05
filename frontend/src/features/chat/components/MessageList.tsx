import React from 'react';
import { Message, ChatMode } from '../types/chat.types';

interface MessageListProps {
  messages: Message[];
  chatMode: ChatMode;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, chatMode }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <PaperChatMessage
          key={message.id}
          message={message}
          isLast={index === messages.length - 1}
          chatMode={chatMode}
        />
      ))}
    </div>
  );
};

interface PaperChatMessageProps {
  message: Message;
  isLast: boolean;
  chatMode: ChatMode;
}

const PaperChatMessage: React.FC<PaperChatMessageProps> = ({ 
  message, 
  isLast, 
  chatMode 
}) => {
  const isUser = message.role === 'user';
  
  return (
    <div className="space-y-4" id={`message-${message.id}`}>
      {/* AI/System message with mode-specific accent */}
      {!isUser && (
        <div className={`border-l-3 pl-8 py-2 ${
          chatMode === 'claude' 
            ? 'border-purple-500' 
            : 'border-blue-500'
        }`}>
          <p className={`text-xl leading-relaxed font-light tracking-wide ${
            chatMode === 'claude' 
              ? 'text-purple-600' 
              : 'text-blue-600'
          }`}>
            {message.content}
          </p>
          {message.tokens_used && (
            <p className="text-xs text-gray-500 mt-2">
              Tokens: {message.tokens_used}
            </p>
          )}
        </div>
      )}
      
      {/* User message as elegant plain text */}
      {isUser && (
        <div className="pl-4 py-1">
          <p className="text-xl leading-relaxed text-gray-800 font-light tracking-wide">
            {message.content}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {new Date(message.created_at).toLocaleTimeString()}
          </p>
        </div>
      )}
    </div>
  );
};