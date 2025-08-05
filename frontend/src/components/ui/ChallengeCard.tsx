import React from 'react';
import styles from './ChallengeCard.module.css';

interface ChallengeCardProps {
  challenge: string;
  xpReward: number;
  completed: boolean;
  onComplete: () => void;
}

const ChallengeCard: React.FC<ChallengeCardProps> = ({ challenge, xpReward, completed, onComplete }) => {
  return (
    <div className={`${styles.challengeCard} ${completed ? styles.completed : ''}`}>
      <div className={styles.challengeContent}>
        <p>{challenge}</p>
        <div className={styles.rewardInfo}>
          <span>XP: {xpReward}</span>
        </div>
      </div>
      {!completed && (
        <button 
          className={styles.completeButton}
          onClick={onComplete}
        >
          Marquer comme terminé
        </button>
      )}
      {completed && (
        <div className={styles.completedBadge}>
          ✓ Terminé
        </div>
      )}
    </div>
  );
};

export default ChallengeCard;