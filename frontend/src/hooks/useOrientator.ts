/**
 * React hooks for Orientator AI integration
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import orientatorService, {
  SendMessageRequest,
  OrientatorMessage,
  SaveComponentRequest,
  SaveComponentResponse,
  UserJourney,
  ConversationSummary,
  ToolAnalytics,
  FeedbackRequest,
  MessageComponent
} from '../services/orientatorService';

/**
 * Hook for sending messages to Orientator AI
 */
export const useOrientatorMessage = (conversationId: number) => {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: (message: string) => 
      orientatorService.sendMessage({ message, conversation_id: conversationId }),
    onSuccess: (data) => {
      // Invalidate conversation queries to update UI
      queryClient.invalidateQueries({ queryKey: ['orientator', 'conversations'] });
      queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] });
    },
  });

  return {
    sendMessage: mutation.mutate,
    sendMessageAsync: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};

/**
 * Hook for saving components
 */
export const useSaveComponent = () => {
  const queryClient = useQueryClient();
  const [savedComponents, setSavedComponents] = useState<Set<string>>(new Set());

  const mutation = useMutation({
    mutationFn: (request: SaveComponentRequest) => 
      orientatorService.saveComponent(request),
    onSuccess: (data, variables) => {
      // Mark component as saved
      setSavedComponents(prev => new Set(prev).add(variables.component_id));
      
      // Invalidate user journey query
      queryClient.invalidateQueries({ queryKey: ['orientator', 'journey'] });
      
      // Show success notification (integrate with your notification system)
      console.log('Component saved successfully:', data.message);
    },
  });

  const isComponentSaved = useCallback((componentId: string) => {
    return savedComponents.has(componentId);
  }, [savedComponents]);

  return {
    saveComponent: mutation.mutate,
    saveComponentAsync: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error,
    isComponentSaved,
    savedComponents: Array.from(savedComponents),
  };
};

/**
 * Hook for fetching user journey
 */
export const useUserJourney = (userId: number) => {
  return useQuery({
    queryKey: ['orientator', 'journey', userId],
    queryFn: () => orientatorService.getUserJourney(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook for fetching Orientator conversations
 */
export const useOrientatorConversations = (limit: number = 20, offset: number = 0) => {
  return useQuery({
    queryKey: ['orientator', 'conversations', { limit, offset }],
    queryFn: () => orientatorService.getConversations(limit, offset),
    staleTime: 60 * 1000, // 1 minute
  });
};

/**
 * Hook for fetching tool analytics
 */
export const useToolAnalytics = () => {
  return useQuery({
    queryKey: ['orientator', 'analytics'],
    queryFn: () => orientatorService.getToolAnalytics(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Hook for submitting feedback
 */
export const useSubmitFeedback = () => {
  const mutation = useMutation({
    mutationFn: (request: FeedbackRequest) => 
      orientatorService.submitFeedback(request),
    onSuccess: (data) => {
      console.log('Feedback submitted:', data.message);
    },
  });

  return {
    submitFeedback: mutation.mutate,
    isLoading: mutation.isPending,
    error: mutation.error,
  };
};

/**
 * Hook for managing Orientator chat state
 */
export const useOrientatorChat = (conversationId: number) => {
  const [messages, setMessages] = useState<OrientatorMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { sendMessageAsync, isLoading } = useOrientatorMessage(conversationId);
  const { saveComponent, isComponentSaved } = useSaveComponent();

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Send message handler
  const handleSendMessage = useCallback(async (message: string) => {
    try {
      setIsTyping(true);
      
      // Add user message immediately
      const userMessage: OrientatorMessage = {
        message_id: Date.now(), // Temporary ID
        role: 'user',
        content: message,
        components: [],
        metadata: {},
        created_at: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Send to API and get response
      const response = await sendMessageAsync(message);
      
      // Add AI response
      setMessages(prev => [...prev, response]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error (show notification, etc.)
    } finally {
      setIsTyping(false);
    }
  }, [sendMessageAsync]);

  // Handle component save
  const handleSaveComponent = useCallback((component: MessageComponent, note?: string) => {
    saveComponent({
      component_id: component.id,
      component_type: component.type,
      component_data: component.data,
      source_tool: component.metadata.tool_source || 'unknown',
      conversation_id: conversationId,
      note,
    });
  }, [saveComponent, conversationId]);

  return {
    messages,
    setMessages,
    isTyping,
    isLoading,
    messagesEndRef,
    handleSendMessage,
    handleSaveComponent,
    isComponentSaved,
    scrollToBottom,
  };
};

/**
 * Hook for streaming messages (future feature)
 */
export const useOrientatorStream = (conversationId: number) => {
  const [currentMessage, setCurrentMessage] = useState<Partial<OrientatorMessage> | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (message: string) => {
    try {
      setIsStreaming(true);
      setCurrentMessage(null);
      
      abortControllerRef.current = new AbortController();
      
      const stream = orientatorService.streamMessage({ 
        message, 
        conversation_id: conversationId 
      });
      
      for await (const chunk of stream) {
        if (abortControllerRef.current?.signal.aborted) {
          break;
        }
        
        setCurrentMessage(prev => ({
          ...prev,
          ...chunk,
          content: (prev?.content || '') + (chunk.content || ''),
        }));
      }
    } catch (error) {
      console.error('Stream error:', error);
    } finally {
      setIsStreaming(false);
    }
  }, [conversationId]);

  const stopStream = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return {
    currentMessage,
    isStreaming,
    startStream,
    stopStream,
  };
};

/**
 * Hook for managing component actions
 */
export const useComponentActions = () => {
  const queryClient = useQueryClient();

  const executeAction = useCallback(async (
    action: any,
    componentData?: any,
    onSuccess?: (data: any) => void
  ) => {
    try {
      const result = await orientatorService.executeAction(action, componentData);
      
      // Invalidate relevant queries based on action type
      if (action.type === 'save') {
        queryClient.invalidateQueries({ queryKey: ['orientator', 'journey'] });
      }
      
      onSuccess?.(result);
      return result;
    } catch (error) {
      console.error('Error executing action:', error);
      throw error;
    }
  }, [queryClient]);

  return { executeAction };
};

/**
 * Hook for checking Orientator health
 */
export const useOrientatorHealth = () => {
  return useQuery({
    queryKey: ['orientator', 'health'],
    queryFn: () => orientatorService.checkHealth(),
    staleTime: 60 * 1000, // 1 minute
    retry: 3,
  });
};