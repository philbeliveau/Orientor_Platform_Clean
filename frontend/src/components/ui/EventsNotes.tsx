'use client';

import React from 'react';
import styles from './EventsNotes.module.css';

interface Event {
  id: string;
  title: string;
  date: Date;
  type: 'test' | 'challenge' | 'event';
  description?: string;
}

interface Note {
  id: number;
  title: string;
  content: string;
  createdAt: Date;
  tags?: string[];
  recommendationId?: number;
}

interface EventsNotesProps {
  events: Event[];
  notes: Note[];
  className?: string;
  onEventClick?: (event: Event) => void;
  onNoteClick?: (note: Note) => void;
}

const EventsNotes: React.FC<EventsNotesProps> = ({ 
  events, 
  notes, 
  className = '', 
  onEventClick, 
  onNoteClick 
}) => {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const formatNoteDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };

  return (
    <div className={`${styles.container} ${className}`}>
      {/* Upcoming Events Section */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Upcoming Events</h3>
        <div className={styles.itemsList}>
          {events.length === 0 ? (
            <p className={styles.emptyMessage}>No upcoming events</p>
          ) : (
            events.map((event) => (
              <div
                key={event.id}
                className={styles.eventCard}
                onClick={() => onEventClick?.(event)}
              >
                <div className={styles.eventIcon}>
                  <span className={`${styles.eventDot} ${styles[event.type]}`}></span>
                </div>
                <div className={styles.eventInfo}>
                  <h4 className={styles.eventTitle}>{event.title}</h4>
                  <p className={styles.eventDate}>{formatDate(event.date)}</p>
                  {event.description && (
                    <p className={styles.eventDescription}>{event.description}</p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* User Notes Section */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>User Notes</h3>
        <div className={styles.itemsList}>
          {notes.length === 0 ? (
            <p className={styles.emptyMessage}>No notes yet</p>
          ) : (
            notes.map((note) => (
              <div
                key={note.id}
                className={styles.noteCard}
                onClick={() => onNoteClick?.(note)}
              >
                <div className={styles.noteHeader}>
                  <h4 className={styles.noteTitle}>{note.title}</h4>
                  <span className={styles.noteDate}>{formatNoteDate(note.createdAt)}</span>
                </div>
                <p className={styles.noteContent}>{note.content}</p>
                {note.tags && note.tags.length > 0 && (
                  <div className={styles.noteTags}>
                    {note.tags.map((tag, index) => (
                      <span key={index} className={styles.tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default EventsNotes;