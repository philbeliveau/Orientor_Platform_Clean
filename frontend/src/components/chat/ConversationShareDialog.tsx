import React, { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { 
  XMarkIcon, 
  ClipboardDocumentIcon,
  LockClosedIcon,
  GlobeAltIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { getAuthHeader, endpoint } from '@/services/api';

interface ConversationShareDialogProps {
  conversationId: number;
  onClose: () => void;
}

export default function ConversationShareDialog({ 
  conversationId, 
  onClose 
}: ConversationShareDialogProps) {
  const [isPublic, setIsPublic] = useState(false);
  const [password, setPassword] = useState('');
  const [expiresInHours, setExpiresInHours] = useState<number | null>(24);
  const [shareLink, setShareLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCreateShare = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/share/conversations/${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          is_public: isPublic,
          password: password || null,
          expires_in_hours: expiresInHours,
          base_url: window.location.origin
        })
      });

      if (response.ok) {
        const data = await response.json();
        setShareLink(data.full_url);
      }
    } catch (error) {
      console.error('Error creating share link:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Share Conversation</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {!shareLink ? (
          <div className="space-y-4">
            {/* Public/Private Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isPublic ? (
                  <GlobeAltIcon className="w-5 h-5 text-primary" />
                ) : (
                  <LockClosedIcon className="w-5 h-5 text-gray-400" />
                )}
                <span className="font-medium">
                  {isPublic ? 'Public Link' : 'Password Protected'}
                </span>
              </div>
              <button
                onClick={() => setIsPublic(!isPublic)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isPublic ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isPublic ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Password Field */}
            {!isPublic && (
              <div>
                <label className="block text-sm font-medium mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password for protection"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            )}

            {/* Expiration */}
            <div>
              <label className="block text-sm font-medium mb-1">
                <ClockIcon className="w-4 h-4 inline mr-1" />
                Link Expires In
              </label>
              <select
                value={expiresInHours || ''}
                onChange={(e) => setExpiresInHours(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Never</option>
                <option value="1">1 hour</option>
                <option value="24">24 hours</option>
                <option value="72">3 days</option>
                <option value="168">1 week</option>
                <option value="720">30 days</option>
              </select>
            </div>

            {/* Create Button */}
            <button
              onClick={handleCreateShare}
              disabled={loading || (!isPublic && !password)}
              className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Share Link'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Share this link to give others access to your conversation:
              </p>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={shareLink}
                  readOnly
                  className="flex-1 px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-sm"
                />
                <button
                  onClick={handleCopyLink}
                  className="px-3 py-2 bg-primary text-white rounded hover:bg-primary-dark"
                >
                  {copied ? (
                    <span className="text-sm">Copied!</span>
                  ) : (
                    <ClipboardDocumentIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {!isPublic && password && (
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  <LockClosedIcon className="w-4 h-4 inline mr-1" />
                  Password: <code className="font-mono">{password}</code>
                </p>
              </div>
            )}

            <button
              onClick={() => {
                setShareLink('');
                setPassword('');
              }}
              className="w-full py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Create Another Link
            </button>
          </div>
        )}
      </div>
    </div>
  );
}