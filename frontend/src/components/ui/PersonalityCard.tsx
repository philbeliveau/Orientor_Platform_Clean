'use client';
import React from 'react';
import Link from 'next/link';
import styles from './personality-card.module.css';

interface PersonalityCardProps {
  items: {
    name: string;
    path: string;
  }[];
}

const PersonalityCard: React.FC<PersonalityCardProps> = ({ items }) => {
  return (
    <div className={styles.card}>
      {items.map((item, index) => (
        <Link key={index} href={item.path} className={styles.cardItem}>
          <span>{item.name}</span>
        </Link>
      ))}
    </div>
  );
};

export default PersonalityCard; 