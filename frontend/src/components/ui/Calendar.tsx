'use client';

import React, { useState } from 'react';
import styles from './Calendar.module.css';

interface Event {
  id: string;
  date: Date;
  title: string;
  type: 'test' | 'challenge' | 'event';
  description?: string;
}

interface CalendarProps {
  events?: Event[];
  onDateClick?: (date: Date) => void;
  className?: string;
}

const Calendar: React.FC<CalendarProps> = ({ events = [], onDateClick, className = '' }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const daysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const firstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getEventForDate = (date: Date) => {
    return events.find(event => {
      const eventDate = new Date(event.date);
      return eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear();
    });
  };

  const handleDateClick = (day: number) => {
    const clickedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    setSelectedDate(clickedDate);
    if (onDateClick) {
      onDateClick(clickedDate);
    }
  };

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const renderCalendarDays = () => {
    const days = [];
    const totalDays = daysInMonth(currentDate);
    const startDay = firstDayOfMonth(currentDate);

    // Empty cells for days before month starts
    for (let i = 0; i < startDay; i++) {
      days.push(<div key={`empty-${i}`} className={styles.emptyDay}></div>);
    }

    // Days of the month
    for (let day = 1; day <= totalDays; day++) {
      const dateForDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const event = getEventForDate(dateForDay);
      const isToday = new Date().toDateString() === dateForDay.toDateString();
      const isSelected = selectedDate?.toDateString() === dateForDay.toDateString();

      days.push(
        <div
          key={day}
          className={`${styles.calendarDay} ${isToday ? styles.today : ''} ${isSelected ? styles.selected : ''} ${event ? styles.hasEvent : ''}`}
          onClick={() => handleDateClick(day)}
        >
          <span className={styles.dayNumber}>{day}</span>
          {event && (
            <div className={`${styles.eventIndicator} ${styles[event.type]}`} title={event.title}>
              <span className={styles.eventDot}></span>
            </div>
          )}
        </div>
      );
    }

    return days;
  };

  return (
    <div className={`${styles.calendar} ${className}`}>
      <div className={styles.calendarHeader}>
        <button onClick={goToPreviousMonth} className={styles.monthNavButton}>
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </button>
        <h3 className={styles.monthYear}>
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h3>
        <button onClick={goToNextMonth} className={styles.monthNavButton}>
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      <div className={styles.calendarDaysHeader}>
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className={styles.dayHeader}>{day}</div>
        ))}
      </div>

      <div className={styles.calendarGrid}>
        {renderCalendarDays()}
      </div>

      <div className={styles.eventLegend}>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.test}`}></span>
          <span>Test</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.challenge}`}></span>
          <span>Challenge</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.event}`}></span>
          <span>Event</span>
        </div>
      </div>
    </div>
  );
};

export default Calendar;