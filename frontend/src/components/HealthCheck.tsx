'use client';
import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface ApiStatus {
  status: 'checking...' | 'online' | 'error' | 'offline';
  error: string | null;
}

export default function HealthCheck() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>({ status: 'checking...', error: null });
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    async function checkApiHealth() {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`);
        if (response.ok) {
          setApiStatus({ status: 'online', error: null });
        } else {
          setApiStatus({ status: 'error', error: `API returned ${response.status}` });
        }
      } catch (err) {
        console.error('Health check failed:', err);
        setApiStatus({ status: 'offline', error: err instanceof Error ? err.message : String(err) });
      }
    }
    
    checkApiHealth();
  }, []);

  const navigateToSpace = () => {
    console.log('Debug: Navigating to /space');
    window.location.href = '/space';
  };

  const navigateToTreePath = () => {
    console.log('Debug: Navigating to /tree-path');
    window.location.href = '/tree-path';
  };

  return (
    <div className="fixed bottom-0 right-0 m-4 p-2 bg-white/80 backdrop-blur-sm text-xs text-gray-500 rounded shadow-sm border border-gray-200 z-50">
      <div>
        API: <span className={apiStatus.status === 'online' ? 'text-green-500' : 'text-red-500'}>
          {apiStatus.status}
        </span>
      </div>
      
      <div className="mt-2">
        <strong>Current Path:</strong> {pathname}
      </div>
      
      <div className="mt-2 space-x-2">
        <button 
          onClick={navigateToSpace}
          className="px-2 py-1 bg-blue-500 text-white rounded text-xs"
        >
          Force Space
        </button>
        <button 
          onClick={navigateToTreePath}
          className="px-2 py-1 bg-green-500 text-white rounded text-xs"
        >
          Force Tree
        </button>
      </div>
    </div>
  );
} 