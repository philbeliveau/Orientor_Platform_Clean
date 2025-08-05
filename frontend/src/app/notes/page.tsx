'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { fetchAllUserNotes, createStandaloneNote, updateNote, deleteNote, Note } from '@/services/spaceService';

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const userNotes = await fetchAllUserNotes();
      setNotes(userNotes.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
    } catch (err) {
      setError('Erreur lors du chargement des notes');
      console.error('Error loading notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNote = async () => {
    if (!newNoteContent.trim()) return;
    
    try {
      const newNote = await createStandaloneNote(newNoteContent.trim());
      setNotes(prev => [newNote, ...prev]);
      setNewNoteContent('');
      setIsCreating(false);
    } catch (err) {
      setError('Erreur lors de la création de la note');
      console.error('Error creating note:', err);
    }
  };

  const handleEditNote = async (noteId: number) => {
    if (!editContent.trim()) return;
    
    try {
      const updatedNote = await updateNote(noteId, { content: editContent.trim() });
      setNotes(prev => prev.map(note => note.id === noteId ? updatedNote : note));
      setEditingId(null);
      setEditContent('');
    } catch (err) {
      setError('Erreur lors de la modification de la note');
      console.error('Error updating note:', err);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) return;
    
    try {
      await deleteNote(noteId);
      setNotes(prev => prev.filter(note => note.id !== noteId));
    } catch (err) {
      setError('Erreur lors de la suppression de la note');
      console.error('Error deleting note:', err);
    }
  };

  const startEdit = (note: Note) => {
    setEditingId(note.id);
    setEditContent(note.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditContent('');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl md:text-4xl font-bold text-stitch-accent mb-6 font-departure">Notes</h1>
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-stitch-accent"></div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl md:text-4xl font-bold text-stitch-accent font-departure">Notes</h1>
          <button 
            onClick={() => setIsCreating(true)}
            className="btn btn-primary"
          >
            + Nouvelle note
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Create new note form */}
        {isCreating && (
          <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 mb-6 shadow-soft">
            <h3 className="text-lg font-bold text-stitch-accent mb-4 font-departure">Nouvelle note</h3>
            <textarea
              value={newNoteContent}
              onChange={(e) => setNewNoteContent(e.target.value)}
              placeholder="Écrivez votre note ici..."
              className="w-full p-3 border border-stitch-border rounded-lg bg-stitch-secondary text-stitch-sage placeholder-stitch-sage/70 resize-none focus:outline-none focus:ring-2 focus:ring-stitch-accent focus:border-transparent"
              rows={4}
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-4">
              <button 
                onClick={() => {
                  setIsCreating(false);
                  setNewNoteContent('');
                }}
                className="px-4 py-2 text-stitch-sage hover:text-stitch-accent transition-colors"
              >
                Annuler
              </button>
              <button 
                onClick={handleCreateNote}
                disabled={!newNoteContent.trim()}
                className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sauvegarder
              </button>
            </div>
          </div>
        )}

        {/* Notes list */}
        {notes.length === 0 && !isCreating ? (
          <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 md:p-8 shadow-soft">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="64px" height="64px" fill="currentColor" viewBox="0 0 256 256" className="text-stitch-sage mb-4">
                <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
              </svg>
              <h2 className="text-xl md:text-2xl font-bold text-stitch-accent mb-2 font-departure">Aucune note pour le moment</h2>
              <p className="text-stitch-sage mb-6">Prenez des notes pendant votre parcours d'apprentissage pour les consulter plus tard.</p>
              <button 
                onClick={() => setIsCreating(true)}
                className="btn btn-primary"
              >
                Créer une nouvelle note
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {notes.map((note) => (
              <div key={note.id} className="bg-stitch-primary border border-stitch-border rounded-lg p-6 shadow-soft">
                {editingId === note.id ? (
                  <div>
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full p-3 border border-stitch-border rounded-lg bg-stitch-secondary text-stitch-sage resize-none focus:outline-none focus:ring-2 focus:ring-stitch-accent focus:border-transparent"
                      rows={4}
                      autoFocus
                    />
                    <div className="flex justify-end gap-2 mt-4">
                      <button 
                        onClick={cancelEdit}
                        className="px-4 py-2 text-stitch-sage hover:text-stitch-accent transition-colors"
                      >
                        Annuler
                      </button>
                      <button 
                        onClick={() => handleEditNote(note.id)}
                        disabled={!editContent.trim()}
                        className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Sauvegarder
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-sm text-stitch-sage/70">
                        {formatDate(note.created_at)}
                        {note.updated_at !== note.created_at && (
                          <span className="ml-2">(modifiée le {formatDate(note.updated_at)})</span>
                        )}
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => startEdit(note)}
                          className="p-1 text-stitch-sage hover:text-stitch-accent transition-colors"
                          title="Modifier"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M227.31,73.37,182.63,28.69a16,16,0,0,0-22.63,0L36.69,152A15.86,15.86,0,0,0,32,163.31V208a16,16,0,0,0,16,16H92.69A15.86,15.86,0,0,0,104,219.31L227.31,96A16,16,0,0,0,227.31,73.37ZM92.69,208H48V163.31l88-88L180.69,120Z"></path>
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteNote(note.id)}
                          className="p-1 text-stitch-sage hover:text-red-500 transition-colors"
                          title="Supprimer"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM96,40a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v8H96Zm96,168H64V64H192Z"></path>
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="text-stitch-sage whitespace-pre-wrap">{note.content}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}