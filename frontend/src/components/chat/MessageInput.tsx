'use client';
import { useState, FormEvent, KeyboardEvent, useRef, useEffect } from 'react';

interface MessageInputProps {
    onSendMessage: (message: string) => void;
    placeholder?: string;
    className?: string;
    disabled?: boolean;
}

export default function MessageInput({ 
    onSendMessage, 
    placeholder = 'Type a message...', 
    className = '',
    disabled = false
}: MessageInputProps) {
    const [message, setMessage] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSendMessage(message.trim());
            setMessage('');
            // Reset textarea height after sending
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey && !disabled) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    // Auto-resize the textarea as user types
    const adjustHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
        }
    };

    useEffect(() => {
        adjustHeight();
    }, [message]);

    return (
        <form onSubmit={handleSubmit} className={`flex items-end space-x-2 p-3 sm:p-4 ${className}`}>
            <div className="relative flex-1">
                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={placeholder}
                    className="w-full resize-none rounded-lg border border-neutral-700 bg-neutral-800 p-3 pr-10
                    text-neutral-50 placeholder-neutral-400
                    focus:border-primary-teal focus:outline-none focus:ring-1 focus:ring-primary-teal
                    disabled:opacity-60 disabled:cursor-not-allowed"
                    rows={1}
                    disabled={disabled}
                    style={{ minHeight: '48px', maxHeight: '120px' }}
                />
            </div>
            <button
                type="submit"
                disabled={!message.trim() || disabled}
                className="rounded-lg bg-gradient-primary px-4 py-3 h-12 min-w-[64px]
                text-white shadow-sm transition-all duration-300
                hover:shadow-glow-purple
                disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center justify-center"
                aria-label="Send message"
            >
                <span className="hidden sm:inline mr-1">Send</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
            </button>
        </form>
    );
} 