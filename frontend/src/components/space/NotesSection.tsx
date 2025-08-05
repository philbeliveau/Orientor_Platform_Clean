import React, { useState } from 'react';
import { Note, Recommendation } from '@/services/spaceService';
import { createNote, updateNote, deleteNote } from '@/services/spaceService';

interface NotesSectionProps {
  recommendation: Recommendation;
}

const NotesSection: React.FC<NotesSectionProps> = ({ recommendation }) => {
  const [notes, setNotes] = useState<Note[]>(recommendation.notes || []);
  const [newNote, setNewNote] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    
    try {
      const createdNote = await createNote({
        content: newNote,
        saved_recommendation_id: recommendation.id
      });
      
      setNotes([...notes, createdNote]);
      setNewNote('');
    } catch (error) {
      console.error('Error creating note:', error);
    }
  };

  const handleEditNote = async (noteId: number) => {
    if (!editingContent.trim()) return;
    
    try {
      const updatedNote = await updateNote(noteId, {
        content: editingContent
      });
      
      setNotes(notes.map(note => 
        note.id === noteId ? updatedNote : note
      ));
      
      setEditingNoteId(null);
      setEditingContent('');
    } catch (error) {
      console.error('Error updating note:', error);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold mb-4 text-white">Notes</h3>
      
      {/* Add new note */}
      <div className="mb-6">
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          placeholder="Add a new note..."
          className="w-full p-3 border border-[#3b4d61] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-[#1e2a38] text-gray-200 placeholder-gray-500"
          rows={3}
        />
        <button
          onClick={handleAddNote}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Add Note
        </button>
      </div>
      
      {/* Notes list */}
      <div className="space-y-4">
        {notes.map((note) => (
          <div key={note.id} className="bg-[#1e2a38] p-4 rounded-lg border border-[#3b4d61]">
            {editingNoteId === note.id ? (
              <div>
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  className="w-full p-2 border border-[#3b4d61] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-[#172331] text-gray-200"
                  rows={3}
                />
                <div className="mt-2 flex space-x-2">
                  <button
                    onClick={() => handleEditNote(note.id)}
                    className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setEditingNoteId(null);
                      setEditingContent('');
                    }}
                    className="px-3 py-1 bg-[#223649] text-gray-300 rounded-md hover:bg-[#2c4258] transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-gray-200">{note.content}</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-sm text-gray-400">
                    {new Date(note.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setEditingNoteId(note.id);
                        setEditingContent(note.content);
                      }}
                      className="text-blue-400 hover:text-blue-300"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteNote(note.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotesSection;