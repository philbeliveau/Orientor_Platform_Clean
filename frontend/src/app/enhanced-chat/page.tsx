/**
 * Enhanced Chat Page
 * 
 * Demo page showcasing GraphSage-enhanced LLM conversations with
 * skill relevance analysis and personalized learning recommendations.
 */

'use client';

import React from 'react';
import EnhancedChat from '@/components/chat/EnhancedChat';

const EnhancedChatPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <EnhancedChat />
    </div>
  );
};

export default EnhancedChatPage;