import React, { useState } from 'react';
import { 
  EllipsisVerticalIcon, 
  PencilIcon, 
  ArchiveBoxIcon,
  TrashIcon,
  ShareIcon,
  ArrowDownTrayIcon,
  ChartBarIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import ConversationShareDialog from './ConversationShareDialog';
import ConversationExportDialog from './ConversationExportDialog';

interface ConversationManagerProps {
  conversationId: number;
  conversationTitle: string;
  isArchived: boolean;
  onTitleUpdate: (newTitle: string) => void;
  onArchive: () => void;
  onDelete: () => void;
  onRefresh: () => void;
}

export default function ConversationManager({
  conversationId,
  conversationTitle,
  isArchived,
  onTitleUpdate,
  onArchive,
  onDelete,
  onRefresh
}: ConversationManagerProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(conversationTitle);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);

  const handleTitleSubmit = async () => {
    if (editedTitle.trim() && editedTitle !== conversationTitle) {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ title: editedTitle })
        });

        if (response.ok) {
          onTitleUpdate(editedTitle);
        }
      } catch (error) {
        console.error('Error updating title:', error);
      }
    }
    setIsEditing(false);
  };

  const handleGenerateTitle = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}/generate-title`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        onTitleUpdate(data.title);
        setEditedTitle(data.title);
      }
    } catch (error) {
      console.error('Error generating title:', error);
    }
  };

  const handleViewAnalytics = () => {
    window.open(`${process.env.NEXT_PUBLIC_API_URL}/chat/analytics?conversation=${conversationId}`, '_blank');
  };

  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
      <div className="flex-1">
        {isEditing ? (
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              onBlur={handleTitleSubmit}
              onKeyPress={(e) => e.key === 'Enter' && handleTitleSubmit()}
              className="flex-1 px-2 py-1 bg-transparent border-b-2 border-primary focus:outline-none"
              autoFocus
            />
            <button
              onClick={handleGenerateTitle}
              className="text-xs text-primary hover:text-primary-dark"
            >
              Auto-generate
            </button>
          </div>
        ) : (
          <h1 className="text-xl font-semibold flex items-center">
            {conversationTitle}
            <button
              onClick={() => setIsEditing(true)}
              className="ml-2 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
            >
              <PencilIcon className="w-4 h-4 text-gray-400" />
            </button>
          </h1>
        )}
      </div>

      <div className="relative">
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
        >
          <EllipsisVerticalIcon className="w-5 h-5" />
        </button>

        {showMenu && (
          <>
            <div 
              className="fixed inset-0 z-10"
              onClick={() => setShowMenu(false)}
            />
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20">
              <button
                onClick={() => {
                  setShowShareDialog(true);
                  setShowMenu(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center space-x-2"
              >
                <ShareIcon className="w-4 h-4" />
                <span>Share</span>
              </button>
              
              <button
                onClick={() => {
                  setShowExportDialog(true);
                  setShowMenu(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center space-x-2"
              >
                <ArrowDownTrayIcon className="w-4 h-4" />
                <span>Export</span>
              </button>
              
              <button
                onClick={() => {
                  handleViewAnalytics();
                  setShowMenu(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center space-x-2"
              >
                <ChartBarIcon className="w-4 h-4" />
                <span>Analytics</span>
              </button>
              
              <hr className="my-1 border-gray-200 dark:border-gray-700" />
              
              <button
                onClick={() => {
                  onArchive();
                  setShowMenu(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center space-x-2"
              >
                <ArchiveBoxIcon className="w-4 h-4" />
                <span>{isArchived ? 'Unarchive' : 'Archive'}</span>
              </button>
              
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to delete this conversation?')) {
                    onDelete();
                  }
                  setShowMenu(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 flex items-center space-x-2"
              >
                <TrashIcon className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </>
        )}
      </div>

      {showShareDialog && (
        <ConversationShareDialog
          conversationId={conversationId}
          onClose={() => setShowShareDialog(false)}
        />
      )}

      {showExportDialog && (
        <ConversationExportDialog
          conversationId={conversationId}
          conversationTitle={conversationTitle}
          onClose={() => setShowExportDialog(false)}
        />
      )}
    </div>
  );
}