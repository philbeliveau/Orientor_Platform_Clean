'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';

export default function LoginPage() {
    const router = useRouter();
    const { isLoaded, isSignedIn } = useUser();

    useEffect(() => {
        if (isLoaded) {
            if (isSignedIn) {
                // Already signed in, redirect to dashboard
                router.push('/dashboard');
            } else {
                // Not signed in, redirect to Clerk sign-in page
                router.push('/sign-in');
            }
        }
    }, [isLoaded, isSignedIn, router]);

    // Show loading while redirecting
    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="ml-3 text-gray-600">Redirecting to sign in...</p>
        </div>
    );
}