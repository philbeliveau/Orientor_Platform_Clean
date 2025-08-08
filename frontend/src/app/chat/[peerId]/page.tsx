'use client';
import { useState, useEffect, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import MainLayout from '@/components/layout/MainLayout';
import MessageList from '@/components/chat/MessageList';
import MessageInput from '@/components/chat/MessageInput';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface Message {
    message_id: number;
    sender_id: number;
    recipient_id: number;
    body: string;
    timestamp: string;
}

interface PeerProfile {
    user_id: number;
    name: string | null;
    major: string | null;
    year: number | null;
}

export default function PeerChatPage() {
    const router = useRouter();
    const params = useParams();
    const peerId = params?.peerId as string;
    const { getToken, isLoaded, isSignedIn } = useAuth();
    
    const [messages, setMessages] = useState<Message[]>([]);
    const [peer, setPeer] = useState<PeerProfile | null>(null);
    const [currentUserId, setCurrentUserId] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Function to fetch conversation history
    const fetchMessages = useCallback(async () => {
        if (!isLoaded || !isSignedIn) return;
        
        try {
            const token = await getToken();
            if (!token) {
                router.push('/sign-in');
                return;
            }

            console.log('Fetching messages for peer:', peerId);
            const response = await axios.get<Message[]>(
                `${cleanApiUrl}/messages/conversation/${peerId}`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            console.log('Messages response:', response.data);
            setMessages(response.data);
        } catch (err: any) {
            console.error('Error fetching messages:', err);
            console.error('Error details:', err.response);
            if (err.response?.status === 401) {
                router.push('/sign-in');
                return;
            }
            setError(err.response?.data?.detail || 'Failed to load messages');
        }
    }, [peerId, router, getToken, isLoaded, isSignedIn]);

    // Function to fetch peer profile
    const fetchPeerProfile = useCallback(async () => {
        if (!isLoaded || !isSignedIn) return;
        
        try {
            const token = await getToken();
            if (!token) {
                router.push('/sign-in');
                return;
            }

            const response = await axios.get<PeerProfile>(
                `${cleanApiUrl}/api/v1/profiles/${peerId}`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            setPeer(response.data);
        } catch (err: any) {
            console.error('Error fetching peer profile:', err);
            if (err.response?.status === 401) {
                router.push('/sign-in');
                return;
            }
            setError(err.response?.data?.detail || 'Failed to load peer profile');
        }
    }, [peerId, router, getToken, isLoaded, isSignedIn]);

    // Function to get current user ID
    const fetchCurrentUserId = useCallback(async () => {
        if (!isLoaded || !isSignedIn) return;
        
        try {
            const token = await getToken();
            if (!token) {
                router.push('/sign-in');
                return;
            }

            console.log('Fetching current user info...');
            const response = await axios.get<{id: number}>(
                `${cleanApiUrl}/users/me`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            console.log('Current user response:', response.data);
            setCurrentUserId(response.data.id);
        } catch (err: any) {
            console.error('Error fetching current user:', err);
            console.error('Error details:', err.response);
            if (err.response?.status === 401) {
                router.push('/sign-in');
                return;
            }
            setError(err.response?.data?.detail || 'Failed to load user information');
        }
    }, [router, getToken, isLoaded, isSignedIn]);

    // Function to send a message
    const handleSendMessage = async (messageText: string) => {
        if (!isLoaded || !isSignedIn) return;
        
        try {
            const token = await getToken();
            if (!token) {
                router.push('/sign-in');
                return;
            }

            await axios.post(
                `${cleanApiUrl}/messages`,
                {
                    recipient_id: parseInt(peerId),
                    body: messageText
                },
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            // Refresh messages after sending
            fetchMessages();
        } catch (err: any) {
            console.error('Error sending message:', err);
            if (err.response?.status === 401) {
                router.push('/sign-in');
                return;
            }
            setError(err.response?.data?.detail || 'Failed to send message');
        }
    };

    // If someone navigates to /chat/conversations, redirect to /chat
    useEffect(() => {
        if (peerId === 'conversations') {
            router.replace('/chat');
            return;
        }
    }, [peerId, router]);

    // Initial data fetch
    useEffect(() => {
        if (!isLoaded) return; // Wait for auth to load
        
        if (!isSignedIn) {
            router.push('/sign-in');
            return;
        }
        
        const initializeChat = async () => {
            setLoading(true);
            setError(null);
            
            try {
                await Promise.all([
                    fetchCurrentUserId(),
                    fetchPeerProfile(),
                    fetchMessages()
                ]);
            } catch (err) {
                console.error('Error initializing chat:', err);
            } finally {
                setLoading(false);
            }
        };

        if (peerId && peerId !== 'conversations') {
            initializeChat();
        }
    }, [peerId, isLoaded, isSignedIn, router, fetchCurrentUserId, fetchPeerProfile, fetchMessages]);

    // Set up polling for new messages  
    useEffect(() => {
        if (!peerId || peerId === 'conversations') return;

        const interval = setInterval(() => {
            fetchMessages();
        }, 5000);

        return () => {
            clearInterval(interval);
        };
    }, [peerId, fetchMessages]);

    // Don't render anything if we're redirecting
    if (peerId === 'conversations') {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            </MainLayout>
        );
    }

    // Debug logging
    console.log('Component state:', {
        peerId,
        loading,
        error,
        messagesCount: messages.length,
        currentUserId,
        peerName: peer?.name
    });

    if (!peerId) {
        return (
            <MainLayout>
                <div className="flex h-full items-center justify-center">
                    <p className="text-neutral-gray">No peer selected</p>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="flex h-full flex-col">
                {/* Chat header */}
                <div className="border-b border-neutral-lightest p-4">
                    <h2 className="text-xl font-semibold text-neutral-darkest">
                        {peer?.name || `User ${peerId}`}
                    </h2>
                    {peer?.major && (
                        <p className="text-sm text-neutral-gray">
                            {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                        </p>
                    )}
                </div>

                {/* Chat content */}
                <div className="flex-1 overflow-y-auto">
                    {loading ? (
                        <div className="flex h-full items-center justify-center">
                            <div className="h-8 w-8 animate-spin rounded-full border-2 border-secondary-purple border-t-transparent"></div>
                        </div>
                    ) : error ? (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-red-500">{error}</p>
                        </div>
                    ) : messages.length === 0 ? (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-neutral-gray">No messages yet. Start the conversation!</p>
                        </div>
                    ) : !currentUserId ? (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-red-500">Loading user info...</p>
                        </div>
                    ) : (
                        <MessageList
                            messages={messages}
                            currentUserId={currentUserId}
                            className="min-h-0"
                        />
                    )}
                </div>
                {/* Message input */}
                <div className="border-t border-neutral-lightest">
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        placeholder="Type your message..."
                        className="text-gray-900" // Added class for better visibility
                    />
                </div>
            </div>
        </MainLayout>
    );
} 