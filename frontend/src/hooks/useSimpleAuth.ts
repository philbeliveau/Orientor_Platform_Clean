// Simple auth hook - Module B equivalent  
import { useAuth } from '@clerk/nextjs';
import { getCachedToken } from '@/utils/tokenCache';

export const useSimpleAuth = () => {
  const { getToken: clerkGetToken, ...authRest } = useAuth();
  
  const getToken = () => getCachedToken(clerkGetToken);
  
  return {
    getToken,
    ...authRest
  };
};