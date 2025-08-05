'use client';
import React from 'react';
import Image from 'next/image';
import styles from './AvatarCard.module.css';

interface AvatarCardProps {
  avatarName?: string;
  avatarDescription?: string;
  avatarImageUrl?: string;
  isLoading?: boolean;
  className?: string;
}

const AvatarCard: React.FC<AvatarCardProps> = ({
  avatarName,
  avatarDescription,
  avatarImageUrl,
  isLoading = false,
  className = ''
}) => {
  return (
    <div className={`${styles.avatarCard} ${className} ${isLoading ? styles.loading : ''}`}>
      <div className={styles.avatarContainer}>
        {avatarImageUrl ? (
          <div className={styles.avatarImageWrapper}>
            <Image
              src={avatarImageUrl}
              alt={avatarName || 'Avatar'}
              width={400}
              height={400}
              className={styles.avatarImage}
              priority
            />
            <div className={styles.avatarOverlay}>
              <div className={styles.avatarGlow}></div>
            </div>
          </div>
        ) : (
          <div className={styles.avatarPlaceholder}>
            <div className={styles.placeholderIcon}>
              <svg 
                width="120" 
                height="120" 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
                <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <p className={styles.placeholderText}>Aucun avatar généré</p>
          </div>
        )}
      </div>
      
      {avatarName && (
        <div className={styles.avatarInfo}>
          <h3 className={styles.avatarName}>{avatarName}</h3>
          {avatarDescription && (
            <p className={styles.avatarDescription}>{avatarDescription}</p>
          )}
        </div>
      )}
      
      {isLoading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.spinner}></div>
          <p className={styles.loadingText}>Génération en cours...</p>
        </div>
      )}
    </div>
  );
};

export default AvatarCard;