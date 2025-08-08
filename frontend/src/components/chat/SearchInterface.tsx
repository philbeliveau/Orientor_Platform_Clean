import React, { useState, useCallback, useRef } from 'react';
import { useAuth } from '@clerk/nextjs';
import { 
  MagnifyingGlassIcon, 
  XMarkIcon,
  ClockIcon,
  ChatBubbleLeftIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import debounce from 'lodash/debounce';
import { format } from 'date-fns';
import { getAuthHeader, endpoint } from '@/services/api';

interface SearchResult {
  conversation_id: number;
  conversation_title: string;
  message_id: number;
  message_content: string;
  message_role: string;
  created_at: string;
  relevance_score: number;
  context_snippet: string;
}

interface SearchInterfaceProps {
  onSelectResult: (conversationId: number, messageId: number) => void;
  onClose: () => void;
}

export default function SearchInterface({ onSelectResult, onClose }: SearchInterfaceProps) {
  const { getToken } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: 'all' as 'all' | 'today' | 'week' | 'month',
    role: 'all' as 'all' | 'user' | 'assistant'
  });
  const [showFilters, setShowFilters] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const searchConversations = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const params = new URLSearchParams({
          query: searchQuery,
          date_range: filters.dateRange,
          role_filter: filters.role
        });

        const headers = await getAuthHeader(getToken);
        const response = await fetch(endpoint(`/chat/search?${params}`), {
          headers
        });

        if (response.ok) {
          const data = await response.json();
          setResults(data.results);
        }
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setLoading(false);
      }
    }, 300),
    [filters]
  );

  React.useEffect(() => {
    searchConversations(query);
  }, [query, filters, searchConversations]);

  React.useEffect(() => {
    searchInputRef.current?.focus();
  }, []);

  const highlightText = (text: string, highlight: string) => {
    if (!highlight.trim()) return text;
    
    const regex = new RegExp(`(${highlight})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-4xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <MagnifyingGlassIcon className="w-6 h-6 text-gray-400" />
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search your conversations..."
              className="flex-1 text-lg bg-transparent focus:outline-none"
            />
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg transition-colors ${
                showFilters 
                  ? 'bg-primary text-white' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <FunnelIcon className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="mt-4 flex flex-wrap gap-4">
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Date Range
                </label>
                <select
                  value={filters.dateRange}
                  onChange={(e) => setFilters({ ...filters, dateRange: e.target.value as any })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm"
                >
                  <option value="all">All time</option>
                  <option value="today">Today</option>
                  <option value="week">Past week</option>
                  <option value="month">Past month</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Message Type
                </label>
                <select
                  value={filters.role}
                  onChange={(e) => setFilters({ ...filters, role: e.target.value as any })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm"
                >
                  <option value="all">All messages</option>
                  <option value="user">Your messages</option>
                  <option value="assistant">Assistant messages</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              {query ? (
                <>
                  <MagnifyingGlassIcon className="w-16 h-16 mx-auto mb-4 opacity-20" />
                  <p>No results found for "{query}"</p>
                  <p className="text-sm mt-2">Try different keywords or adjust your filters</p>
                </>
              ) : (
                <>
                  <MagnifyingGlassIcon className="w-16 h-16 mx-auto mb-4 opacity-20" />
                  <p>Start typing to search your conversations</p>
                </>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {results.map((result) => (
                <button
                  key={`${result.conversation_id}-${result.message_id}`}
                  onClick={() => onSelectResult(result.conversation_id, result.message_id)}
                  className="w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-800 text-left transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-sm flex items-center">
                      <ChatBubbleLeftIcon className="w-4 h-4 mr-2 text-gray-400" />
                      {result.conversation_title}
                    </h3>
                    <span className="text-xs text-gray-500 flex items-center">
                      <ClockIcon className="w-3 h-3 mr-1" />
                      {format(new Date(result.created_at), 'MMM d, yyyy')}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium mr-2 ${
                      result.message_role === 'user' 
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                        : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                    }`}>
                      {result.message_role === 'user' ? 'You' : 'Assistant'}
                    </span>
                    <span className="line-clamp-2">
                      {highlightText(result.context_snippet || result.message_content, query)}
                    </span>
                  </div>
                  
                  {result.relevance_score > 0 && (
                    <div className="mt-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">Relevance</span>
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                          <div 
                            className="bg-primary h-1 rounded-full"
                            style={{ width: `${result.relevance_score * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500">
          <div className="flex items-center justify-between">
            <span>
              {results.length > 0 && `Found ${results.length} results`}
            </span>
            <div className="flex items-center space-x-4 text-xs">
              <span>Press ESC to close</span>
              <span>↑↓ to navigate</span>
              <span>Enter to select</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}