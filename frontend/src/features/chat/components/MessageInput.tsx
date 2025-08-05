import React, { useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isTyping: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  value,
  onChange,
  onSend,
  isTyping
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-end space-x-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="flex-1 resize-none rounded-lg border border-gray-300 p-3 
                     focus:outline-none focus:ring-2 focus:ring-blue-500
                     min-h-[50px] max-h-[200px]"
          disabled={isTyping}
          rows={1}
        />
        <button
          onClick={onSend}
          disabled={isTyping || !value.trim()}
          className="rounded-lg bg-blue-500 p-3 text-white 
                     hover:bg-blue-600 disabled:opacity-50 
                     disabled:cursor-not-allowed transition-colors"
        >
          <Send size={20} />
        </button>
      </div>
      {isTyping && (
        <div className="mt-2 text-sm text-gray-500">
          AI is thinking...
        </div>
      )}
    </div>
  );
};