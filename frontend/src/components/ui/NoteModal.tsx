import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { saveNodeNote, fetchNodeNotes } from '../../utils/treeStorage';

interface NoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  nodeId: string;
  actionIndex: number;
  actionText: string;
}

export default function NoteModal({ isOpen, onClose, nodeId, actionIndex, actionText }: NoteModalProps) {
  // Auth hook for token
  const { getToken } = useAuth();
  
  const [noteText, setNoteText] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch existing note when modal opens
  useEffect(() => {
    if (isOpen && nodeId) {
      const fetchNote = async () => {
        const token = await getToken();
        if (!token) {
          setError('Authentication required');
          return;
        }
        
        try {
          const notes = await fetchNodeNotes(nodeId, token);
          const existingNote = notes.find(note => note.action_index === actionIndex);
          if (existingNote) {
            setNoteText(existingNote.note_text);
          } else {
            setNoteText('');
          }
        } catch (err: any) {
          console.error('Error fetching note:', err);
          setError(err.message || 'Failed to load note');
        }
      };
      fetchNote();
    }
  }, [isOpen, nodeId, actionIndex, getToken]);

  // Handle save note
  const handleSaveNote = async () => {
    if (!noteText.trim()) {
      return;
    }
    
    const token = await getToken();
    if (!token) {
      setError('Authentication required');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await saveNodeNote(nodeId, actionIndex, noteText, token);
      onClose();
    } catch (err: any) {
      console.error('Error saving note:', err);
      setError(err.message || 'Failed to save note');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        {/* Overlay */}
        <div 
          className="fixed inset-0 bg-black opacity-30"
          onClick={onClose}
          aria-hidden="true"
        ></div>
        
        {/* Modal */}
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-md z-10 relative">
          <div className="p-5">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Notes</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="mb-4">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Action:</div>
              <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md text-gray-700 dark:text-gray-300 text-sm">{actionText}</div>
            </div>
            
            <div className="mb-4">
              <label htmlFor="noteText" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Your Notes:
              </label>
              <textarea
                id="noteText"
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
                placeholder="Write your personal notes here..."
              />
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md text-sm">
                {error}
              </div>
            )}
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveNote}
                disabled={isSaving}
                className="px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Note'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 