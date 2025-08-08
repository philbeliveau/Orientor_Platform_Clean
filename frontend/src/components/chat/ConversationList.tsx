import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { format } from 'date-fns';
import { 
  ChatBubbleLeftIcon, 
  StarIcon, 
  ArchiveBoxIcon,
  MagnifyingGlassIcon,
  FolderIcon,
  PlusIcon 
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

interface Conversation {
  id: number;
  title: string;
  auto_generated_title: boolean;
  category_id: number | null;
  is_favorite: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
  message_count: number;
  total_tokens_used: number;
}

interface ConversationListProps {
  selectedConversationId?: number;
  onSelectConversation: (conversation: Conversation) => void;
  onCreateNew: () => void;
  refreshTrigger?: number;
}

export default function ConversationList({ 
  selectedConversationId, 
  onSelectConversation,
  onCreateNew,
  refreshTrigger 
}: ConversationListProps) {
  const { getToken } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'favorites' | 'archived'>('all');

  useEffect(() => {
    fetchConversations();
  }, [filter]);

  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      fetchConversations();
    }
  }, [refreshTrigger]);

  const fetchConversations = async () => {
    try {
      const token = await getToken();
      if (!token) return;
      
      const params = new URLSearchParams();
      if (filter === 'favorites') params.append('is_favorite', 'true');
      if (filter === 'archived') params.append('is_archived', 'true');
      
      console.log('Fetching conversations with filter:', filter);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/conversations?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Conversations fetched:', data.conversations?.length || 0);
        console.log('Conversations data:', data);
        setConversations(data.conversations || data || []);
      } else {
        console.error('Failed to fetch conversations:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (e: React.MouseEvent, conversationId: number) => {
    e.stopPropagation();
    try {
      const token = await getToken();
      if (!token) return;
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}/favorite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        fetchConversations();
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return format(date, 'HH:mm');
    } else if (diffInHours < 168) { // 7 days
      return format(date, 'EEE HH:mm');
    } else {
      return format(date, 'MMM d');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Conversations</h2>
          <button
            onClick={onCreateNew}
            className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
            title="New conversation"
          >
            <PlusIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        
        {/* Filters */}
        <div className="flex space-x-2 mt-3">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              filter === 'all' 
                ? 'bg-primary text-white' 
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('favorites')}
            className={`px-3 py-1 text-xs rounded-full transition-colors flex items-center space-x-1 ${
              filter === 'favorites' 
                ? 'bg-primary text-white' 
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <StarIcon className="w-3 h-3" />
            <span>Favorites</span>
          </button>
          <button
            onClick={() => setFilter('archived')}
            className={`px-3 py-1 text-xs rounded-full transition-colors flex items-center space-x-1 ${
              filter === 'archived' 
                ? 'bg-primary text-white' 
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <ArchiveBoxIcon className="w-3 h-3" />
            <span>Archived</span>
          </button>
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <ChatBubbleLeftIcon className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p className="text-sm">No conversations found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => onSelectConversation(conversation)}
                className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors ${
                  selectedConversationId === conversation.id 
                    ? 'bg-primary/5 border-l-4 border-primary' 
                    : ''
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <h3 className="font-medium text-sm truncate pr-2">
                    {conversation.title}
                  </h3>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => toggleFavorite(e, conversation.id)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                    >
                      {conversation.is_favorite ? (
                        <StarSolidIcon className="w-4 h-4 text-yellow-500" />
                      ) : (
                        <StarIcon className="w-4 h-4 text-gray-400" />
                      )}
                    </button>
                    {conversation.is_archived && (
                      <ArchiveBoxIcon className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-2">
                    <span>{conversation.message_count} messages</span>
                    {conversation.auto_generated_title && (
                      <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full">
                        Auto
                      </span>
                    )}
                  </div>
                  <span>{formatDate(conversation.last_message_at || conversation.updated_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}