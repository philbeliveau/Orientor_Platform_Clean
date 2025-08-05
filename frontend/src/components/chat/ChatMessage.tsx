// import React from 'react';

// type MessageType = 'user' | 'ai';

// interface ChatMessageProps {
//   message: string;
//   type: MessageType;
// }

// export default function ChatMessage({ message, type }: ChatMessageProps) {
//   return (
//     <div className={`flex ${type === 'user' ? 'justify-end' : 'justify-start'}`}>
//       <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
//         type === 'user' 
//           ? 'bg-blue-600 text-white' 
//           : 'bg-gray-700 text-gray-100'
//       }`}>
//         {message}
//       </div>
//     </div>
//   );
// }

// frontend/src/components/chat/ChatMessage.tsx

// frontend/src/components/chat/ChatMessage.tsx

import React from 'react';
import { motion } from 'framer-motion';

type MessageType = 'user' | 'ai';

interface ChatMessageProps {
  message: string;
  type: MessageType;
  userColor?: string; // Optional prop for user message color
  aiColor?: string;   // Optional prop for AI message color
}

export default function ChatMessage({ 
  message, 
  type, 
  userColor = 'bg-gradient-primary', 
  aiColor = 'bg-neutral-800/60 backdrop-blur-md border border-neutral-700/30' 
}: ChatMessageProps) {
  const isUser = type === 'user';
  
  return (
    <motion.div 
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div 
        className={`
          max-w-[90%] sm:max-w-[80%] 
          rounded-2xl 
          px-4 py-3 
          shadow-sm
          ${isUser 
            ? `${userColor} text-white rounded-br-sm` 
            : `${aiColor} text-neutral-100 rounded-bl-sm`
          }
        `}
      >
        <div className="text-sm sm:text-base whitespace-pre-wrap break-words leading-relaxed">
          {message}
        </div>
      </div>
    </motion.div>
  );
}