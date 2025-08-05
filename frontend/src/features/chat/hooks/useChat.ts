import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { Message, Conversation, ChatState, ChatActions } from '../types/chat.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useChat = (currentUserId: number) => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    currentConversation: null,
    selectedCategory: null,
    isTyping: false,
    chatMode: 'default'
  });

  const router = useRouter();

  // Load conversation messages
  const loadConversationMessages = useCallback(async (conversationId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      setState(prev => ({
        ...prev,
        messages: response.data.messages || []
      }));
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || state.isTyping) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    setState(prev => ({ ...prev, isTyping: true }));

    try {
      // Create conversation if needed
      if (!state.currentConversation) {
        const createResponse = await axios.post(
          `${API_BASE_URL}/api/chat/conversations`,
          { initial_message: message },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );
        
        const newConversation = createResponse.data.conversation;
        setState(prev => ({
          ...prev,
          currentConversation: newConversation,
          messages: createResponse.data.messages || []
        }));
        
        router.push(`/chat?conversation=${newConversation.id}`);
      } else {
        // Send message to existing conversation
        const response = await axios.post(
          `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}/messages`,
          { 
            content: message,
            mode: state.chatMode 
          },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );

        const newMessages: Message[] = [
          {
            id: Date.now(),
            role: 'user',
            content: message,
            created_at: new Date().toISOString(),
          },
          response.data.message
        ];

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, ...newMessages]
        }));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg: Message = {
        id: Date.now(),
        role: 'system',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      };
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMsg]
      }));
    } finally {
      setState(prev => ({ ...prev, isTyping: false }));
    }
  }, [state.currentConversation, state.isTyping, state.chatMode, router]);

  // Select conversation
  const selectConversation = useCallback((conversation: Conversation) => {
    setState(prev => ({
      ...prev,
      currentConversation: conversation
    }));
    loadConversationMessages(conversation.id);
  }, [loadConversationMessages]);

  // Create new conversation
  const createNewConversation = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentConversation: null,
      messages: []
    }));
    router.push('/chat');
  }, [router]);

  // Archive conversation
  const archiveConversation = useCallback(async () => {
    if (!state.currentConversation) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.patch(
        `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}`,
        { is_archived: true },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      createNewConversation();
    } catch (error) {
      console.error('Error archiving conversation:', error);
    }
  }, [state.currentConversation, createNewConversation]);

  // Delete conversation
  const deleteConversation = useCallback(async () => {
    if (!state.currentConversation) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      createNewConversation();
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  }, [state.currentConversation, createNewConversation]);

  // Update conversation title
  const updateTitle = useCallback(async (title: string) => {
    if (!state.currentConversation || !title.trim()) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.patch(
        `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}`,
        { title },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      setState(prev => ({
        ...prev,
        currentConversation: response.data.conversation
      }));
    } catch (error) {
      console.error('Error updating title:', error);
    }
  }, [state.currentConversation]);

  const actions: ChatActions = {
    sendMessage,
    selectConversation,
    createNewConversation,
    archiveConversation,
    deleteConversation,
    updateTitle
  };

  return {
    ...state,
    actions,
    setState
  };
};