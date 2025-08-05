'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: number;
  text: string;
  sender: 'mentor' | 'user';
}

const messages: Message[] = [
  {
    id: 1,
    text: "Hi! I'm Orientator, your AI career guide. What brings you here today?",
    sender: 'mentor',
  },
  {
    id: 2,
    text: "I'm not sure what career path to choose. I'm interested in technology but don't know where to start.",
    sender: 'user',
  },
  {
    id: 3,
    text: "That's a great starting point! Let's explore your interests and skills. What aspects of technology excite you the most?",
    sender: 'mentor',
  },
  {
    id: 4,
    text: "I really enjoy problem-solving and creating things. I've done some basic coding and found it interesting!",
    sender: 'user',
  },
  {
    id: 5,
    text: "Sounds like you may enjoy roles where you can build or solve—like software development or product design.",
    sender: 'mentor',
  },
  {
    id: 6,
    text: "That sounds exciting. I’d love to learn more about where that could take me.",
    sender: 'user',
  },
];

export default function DemoChat() {
  const [visibleMessages, setVisibleMessages] = useState<Message[]>([]);
  const [showTyping, setShowTyping] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex >= messages.length) return;

    const showMessage = () => {
      const isMentor = messages[currentIndex].sender === 'mentor';
      setShowTyping(isMentor);

      const delay = isMentor ? 300 : 0;

      setTimeout(() => {
        setVisibleMessages((prev) => [...prev, messages[currentIndex]]);
        setShowTyping(false);
        setCurrentIndex((prev) => prev + 1);
      }, delay);
    };

    const timer = setTimeout(showMessage, 1000);
    return () => clearTimeout(timer);
  }, [currentIndex]);

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-6">

      <div className="space-y-4">
        <AnimatePresence>
          {visibleMessages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.sender === 'mentor' ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 shadow ${
                  message.sender === 'mentor'
                    ? 'bg-blue-100 text-blue-900'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {showTyping && (
          <motion.div
            key="typing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex justify-start"
          >
            <div className="bg-blue-100 px-4 py-2 rounded-2xl shadow inline-block">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
