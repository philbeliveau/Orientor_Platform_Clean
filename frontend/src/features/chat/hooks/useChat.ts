import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
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
  const { getToken, isSignedIn, isLoaded } = useAuth();

  // Load conversation messages
  const loadConversationMessages = useCallback(async (conversationId: number) => {
    if (!isLoaded || !isSignedIn) return;
    
    try {
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      
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
    } catch (error: any) {
      console.error('Error loading messages:', error);
      if (error.response?.status === 401) {
        router.push('/sign-in');
      }
    }
  }, [getToken, isLoaded, isSignedIn, router]);

  // Send message
  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || state.isTyping || !isLoaded || !isSignedIn) return;

    const token = await getToken();
    if (!token) {
      router.push('/sign-in');
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
    } catch (error: any) {
      console.error('Error sending message:', error);
      
      if (error.response?.status === 401) {
        router.push('/sign-in');
        return;
      }
      
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
  }, [state.currentConversation, state.isTyping, state.chatMode, router, getToken, isLoaded, isSignedIn]);

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
    if (!state.currentConversation || !isLoaded || !isSignedIn) return;

    try {
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      await axios.patch(
        `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}`,
        { is_archived: true },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      createNewConversation();
    } catch (error: any) {
      console.error('Error archiving conversation:', error);
      if (error.response?.status === 401) {
        router.push('/sign-in');
      }
    }
  }, [state.currentConversation, createNewConversation, getToken, isLoaded, isSignedIn, router]);

  // Delete conversation
  const deleteConversation = useCallback(async () => {
    if (!state.currentConversation || !isLoaded || !isSignedIn) return;

    try {
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      await axios.delete(
        `${API_BASE_URL}/api/chat/conversations/${state.currentConversation.id}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      createNewConversation();
    } catch (error: any) {
      console.error('Error deleting conversation:', error);
      if (error.response?.status === 401) {
        router.push('/sign-in');
      }
    }
  }, [state.currentConversation, createNewConversation, getToken, isLoaded, isSignedIn, router]);

  // Update conversation title
  const updateTitle = useCallback(async (title: string) => {
    if (!state.currentConversation || !title.trim() || !isLoaded || !isSignedIn) return;

    try {
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
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
    } catch (error: any) {
      console.error('Error updating title:', error);
      if (error.response?.status === 401) {
        router.push('/sign-in');
      }
    }
  }, [state.currentConversation, getToken, isLoaded, isSignedIn, router]);

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