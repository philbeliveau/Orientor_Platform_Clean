'use client';

import React, { useState, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { useSearchParams } from 'next/navigation';
import { useChat } from '../hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ChatHeader } from './ChatHeader';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Lazy load heavy components
const ConversationList = dynamic(() => import('@/components/chat/ConversationList'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

const SearchInterface = dynamic(() => import('@/components/chat/SearchInterface'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

const CategoryManager = dynamic(() => import('@/components/chat/CategoryManager'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

const AnalyticsDashboard = dynamic(() => import('@/components/chat/AnalyticsDashboard'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

interface ChatInterfaceProps {
  currentUserId: number;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ currentUserId }) => {
  const searchParams = useSearchParams();
  const {
    messages,
    currentConversation,
    selectedCategory,
    isTyping,
    chatMode,
    actions,
    setState
  } = useChat(currentUserId);

  const [inputText, setInputText] = useState('');
  const [showSidebar, setShowSidebar] = useState(false);
  const [sidebarView, setSidebarView] = useState<'conversations' | 'search' | 'categories' | 'analytics'>('conversations');

  // Handle initial message from URL params
  useEffect(() => {
    const initialMessage = searchParams?.get('initial_message');
    const messageType = searchParams?.get('type');
    
    if (initialMessage && !currentConversation) {
      const decodedMessage = decodeURIComponent(initialMessage);
      setInputText(decodedMessage);
      
      // Auto-send for certain message types
      if (messageType === 'career_recommendation' || messageType === 'profile_analysis') {
        setTimeout(() => {
          handleSend();
        }, 500);
      }
    }
  }, [searchParams]);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    await actions.sendMessage(inputText);
    setInputText('');
  };

  const handleSearchResult = (conversationId: number, messageId: number) => {
    // Load conversation and scroll to message
    const conversation = { id: conversationId } as any; // Would fetch full conversation
    actions.selectConversation(conversation);
    
    setTimeout(() => {
      const messageElement = document.getElementById(`message-${messageId}`);
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        messageElement.classList.add('highlight-message');
        setTimeout(() => {
          messageElement.classList.remove('highlight-message');
        }, 2000);
      }
    }, 500);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Suspense fallback={<LoadingSpinner />}>
        <div className={`${
          showSidebar ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-30 w-80 transform bg-white shadow-lg 
          transition-transform duration-300 ease-in-out lg:relative 
          lg:translate-x-0`}>
          
          {/* Sidebar Navigation */}
          <div className="border-b p-4">
            <div className="flex space-x-2">
              <button
                onClick={() => setSidebarView('conversations')}
                className={`flex-1 rounded px-3 py-2 text-sm font-medium 
                  ${sidebarView === 'conversations' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                Chats
              </button>
              <button
                onClick={() => setSidebarView('search')}
                className={`flex-1 rounded px-3 py-2 text-sm font-medium 
                  ${sidebarView === 'search' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                Search
              </button>
              <button
                onClick={() => setSidebarView('categories')}
                className={`flex-1 rounded px-3 py-2 text-sm font-medium 
                  ${sidebarView === 'categories' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                Categories
              </button>
            </div>
          </div>
          
          {/* Sidebar Content */}
          <div className="flex-1 overflow-y-auto">
            {sidebarView === 'conversations' && (
              <ConversationList
                selectedConversationId={currentConversation?.id}
                onSelectConversation={actions.selectConversation}
                onCreateNew={actions.createNewConversation}
                refreshTrigger={0}
              />
            )}
            {sidebarView === 'search' && (
              <SearchInterface
                onSelectResult={handleSearchResult}
                onClose={() => setSidebarView('conversations')}
              />
            )}
            {sidebarView === 'categories' && (
              <CategoryManager
                selectedCategoryId={selectedCategory?.id}
                onSelectCategory={(category) => 
                  setState(prev => ({ ...prev, selectedCategory: category }))
                }
                onClose={() => setSidebarView('conversations')}
              />
            )}
            {sidebarView === 'analytics' && (
              <AnalyticsDashboard />
            )}
          </div>
        </div>
      </Suspense>

      {/* Main Chat Area */}
      <div className="flex flex-1 flex-col">
        <ChatHeader
          conversation={currentConversation}
          chatMode={chatMode}
          onMenuClick={() => setShowSidebar(!showSidebar)}
          onNewChat={actions.createNewConversation}
          onUpdateTitle={actions.updateTitle}
          onModeChange={(mode) => 
            setState(prev => ({ ...prev, chatMode: mode }))
          }
        />
        
        <MessageList messages={messages} chatMode={chatMode} />
        
        <MessageInput
          value={inputText}
          onChange={setInputText}
          onSend={handleSend}
          isTyping={isTyping}
        />
      </div>
    </div>
  );
};