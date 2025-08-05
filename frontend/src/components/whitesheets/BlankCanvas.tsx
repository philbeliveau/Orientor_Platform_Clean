'use client';

import React, { useState, useRef, useEffect } from 'react';

interface BlankCanvasProps {
  onContentChange?: (content: string) => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export default function BlankCanvas({
  onContentChange,
  placeholder = "What's on your mind? Start writing your story...",
  className = '',
  autoFocus = false
}: BlankCanvasProps) {
  const [content, setContent] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [autoFocus]);

  useEffect(() => {
    // Blinking cursor effect
    const cursorInterval = setInterval(() => {
      setShowCursor(prev => !prev);
    }, 1000);

    return () => clearInterval(cursorInterval);
  }, []);

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    setIsTyping(true);
    onContentChange?.(newContent);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }

    // Stop typing indicator after a delay
    setTimeout(() => setIsTyping(false), 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle tab key for indentation
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.currentTarget.selectionStart;
      const end = e.currentTarget.selectionEnd;
      const newContent = content.substring(0, start) + '  ' + content.substring(end);
      setContent(newContent);
      onContentChange?.(newContent);
      
      // Set cursor position after tab
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 2;
        }
      }, 0);
    }
  };

  return (
    <div className={`blank-canvas ${className}`}>
      <div className="blank-canvas-container">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="blank-canvas-textarea"
          rows={1}
        />
        
        {content.length === 0 && (
          <div className="blank-canvas-guide">
            <div className={`blank-canvas-cursor ${showCursor ? 'visible' : ''}`} />
            <div className="blank-canvas-hint white-sheet-fade-in">
              <p className="white-sheet-text-subtle">This is your space. Write freely, explore deeply.</p>
            </div>
          </div>
        )}
        
        {isTyping && (
          <div className="blank-canvas-typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
      </div>
    </div>
  );
}

// Blank Canvas specific styles
const blankCanvasStyles = `
.blank-canvas {
  position: relative;
  width: 100%;
  min-height: 300px;
  background: var(--white-sheet-primary);
  border: 1px solid var(--white-sheet-border-subtle);
  border-radius: var(--white-sheet-radius-lg);
  overflow: hidden;
  transition: all var(--white-sheet-transition-medium);
}

.blank-canvas:hover {
  border-color: var(--white-sheet-border);
}

.blank-canvas:focus-within {
  border-color: var(--white-sheet-text-subtle);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.blank-canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  padding: var(--white-sheet-space-lg);
}

.blank-canvas-textarea {
  width: 100%;
  min-height: 250px;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--white-sheet-font-primary);
  font-size: 1rem;
  line-height: 1.8;
  color: var(--white-sheet-text);
  resize: none;
  overflow: hidden;
}

.blank-canvas-textarea::placeholder {
  color: var(--white-sheet-text-subtle);
  opacity: 0.7;
}

.blank-canvas-guide {
  position: absolute;
  top: var(--white-sheet-space-lg);
  left: var(--white-sheet-space-lg);
  pointer-events: none;
}

.blank-canvas-cursor {
  width: 2px;
  height: 24px;
  background: var(--white-sheet-accent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.blank-canvas-cursor.visible {
  opacity: 1;
}

.blank-canvas-hint {
  margin-top: var(--white-sheet-space-md);
  max-width: 400px;
}

.blank-canvas-typing-indicator {
  position: absolute;
  bottom: var(--white-sheet-space-md);
  left: var(--white-sheet-space-lg);
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--white-sheet-text-subtle);
  animation: typingDot 1.5s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.3s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes typingDot {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .blank-canvas-container {
    padding: var(--white-sheet-space-md);
  }
  
  .blank-canvas-textarea {
    font-size: 0.875rem;
    min-height: 200px;
  }
  
  .blank-canvas-guide {
    top: var(--white-sheet-space-md);
    left: var(--white-sheet-space-md);
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = blankCanvasStyles;
  document.head.appendChild(styleSheet);
}