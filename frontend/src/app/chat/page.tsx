'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import MainLayout from '@/components/layout/MainLayout';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
    const router = useRouter();
    const { isLoaded, isSignedIn } = useAuth();
    const { user } = useUser();
    const [currentUserId, setCurrentUserId] = useState<number | null>(null);
    const [authError, setAuthError] = useState<string | null>(null);

    // Check authentication on mount
    useEffect(() => {
        if (!isLoaded) return; // Wait for auth to load

        if (!isSignedIn) {
            router.push('/sign-in');
            return;
        }

        // Use Clerk user ID - convert to number if needed
        if (user?.id) {
            // For now, use a simple hash of the user ID to generate a numeric ID
            const numericId = Math.abs(user.id.split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0)) % 1000000;
            setCurrentUserId(numericId);
        }
    }, [isLoaded, isSignedIn, user, router]);

    if (!currentUserId) {
        return (
            <MainLayout>
                <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
                    <div className="relative z-10 w-full">
                        <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
                            <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
                                <div 
                                    className="p-8 text-center"
                                    style={{
                                        borderRadius: '24px',
                                        background: '#e0e0e0',
                                        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                                    }}
                                >
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                                    <p className="text-gray-600">Loading chat...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
                {authError && (
                    <div className="absolute top-6 left-6 right-6 z-20">
                        <div 
                            className="px-4 py-3 text-red-700"
                            style={{
                                borderRadius: '12px',
                                background: '#fee2e2',
                                border: '1px solid #fca5a5'
                            }}
                        >
                            {authError}
                        </div>
                    </div>
                )}
                <div className="relative z-10 w-full">
                    <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
                        <ChatInterface currentUserId={currentUserId} enableOrientator={true} />
                    </div>
                </div>
            </div>
        </MainLayout>
    );
} 
