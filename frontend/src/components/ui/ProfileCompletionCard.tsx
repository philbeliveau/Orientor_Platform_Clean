'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import LoadingSpinner from './LoadingSpinner';
import styles from './profile-completion-card.module.css';

interface ProfileCompletionData {
  overall_percentage: number;
  category_scores: Record<string, number>;
  next_actions: CompletionAction[];
  recommendation_eligible: boolean;
  missing_critical_data: string[];
}

interface CompletionAction {
  id: string;
  title: string;
  description: string;
  url: string;
  category: string;
  weight: number;
  estimated_time: string;
}

interface ProfileCompletionCardProps {
  className?: string;
}

const ProfileCompletionCard: React.FC<ProfileCompletionCardProps> = ({ className = "" }) => {
  const router = useRouter();
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [completionData, setCompletionData] = useState<ProfileCompletionData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Wait for authentication to be loaded and verified
    if (!isLoaded) return;
    
    if (!isSignedIn) {
      setError('Authentication required');
      setLoading(false);
      return;
    }

    fetchCompletionData();
  }, [isLoaded, isSignedIn]);
  
  const fetchCompletionData = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      
      if (!token) {
        setError('Authentication required');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/profiles/completion`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ProfileCompletionData = await response.json();
      setCompletionData(data);
      
    } catch (err) {
      console.error('Error fetching completion data:', err);
      setError('Failed to load profile completion data');
    } finally {
      setLoading(false);
    }
  };
  
  const handleClick = () => {
    // Navigate to profile completion hub
    router.push('/profile/complete');
  };

  const getProgressColor = (percentage: number): string => {
    if (percentage < 0.3) return '#ef4444'; // Red
    if (percentage < 0.6) return '#f59e0b'; // Amber
    if (percentage < 0.8) return '#3b82f6'; // Blue
    return '#10b981'; // Green
  };

  const getMotivationalMessage = (percentage: number, nextAction?: CompletionAction): string => {
    if (percentage >= 0.9) {
      return "🎉 Profil excellent ! Vos recommandations sont optimisées.";
    } else if (percentage >= 0.7) {
      return "✨ Presque terminé ! Quelques détails pour parfaire votre profil.";
    } else if (percentage >= 0.5) {
      return "🚀 Bon début ! Continuez pour débloquer plus de recommandations.";
    } else if (percentage >= 0.3) {
      return "💡 Votre profil prend forme ! Ajoutez plus d'informations.";
    } else if (nextAction) {
      return `📝 Commencez par: ${nextAction.title}`;
    } else {
      return "🌟 Créez votre profil pour des recommandations personnalisées !";
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={`${styles.card} ${styles.loading}`}>
          <h3 className={styles.title}>📊 Completion du Profil</h3>
          <p className={styles.preview}>Chargement de vos données...</p>
          <div className={styles.loadingIndicator}>
            <LoadingSpinner size="sm" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !completionData) {
    return (
      <div className={styles.container}>
        <div className={`${styles.card} ${styles.error}`} onClick={handleClick}>
          <h3 className={styles.title}>⚠️ Profile Incomplet</h3>
          <p className={styles.preview}>
            Completez votre profil pour des recommandations personnalisées
          </p>
          <div className={styles.ctaText}>
            Cliquez pour commencer
          </div>
        </div>
      </div>
    );
  }

  const { overall_percentage, next_actions, recommendation_eligible } = completionData;
  const nextAction = next_actions[0];
  const progressColor = getProgressColor(overall_percentage);
  const message = getMotivationalMessage(overall_percentage, nextAction);

  return (
    <div className={styles.container}>
      <div
        className={`${styles.card} ${className}`}
        onClick={handleClick}
        style={{ cursor: 'pointer' }}
      >
        <h3 className={styles.title}>
          📊 Completion du Profil
          {recommendation_eligible && <span className={styles.badge}>✓</span>}
        </h3>
        
        {/* Progress Bar */}
        <div className={styles.progressContainer}>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill}
              style={{ 
                width: `${overall_percentage * 100}%`,
                backgroundColor: progressColor 
              }}
            />
          </div>
          <span className={styles.progressText} style={{ color: progressColor }}>
            {Math.round(overall_percentage * 100)}%
          </span>
        </div>
        
        {/* Motivational Message */}
        <p className={styles.preview}>{message}</p>
        
        {/* Next Action */}
        {nextAction && (
          <div className={styles.nextAction}>
            <span className={styles.nextActionLabel}>Prochaine étape:</span>
            <span className={styles.nextActionTitle}>{nextAction.title}</span>
            <span className={styles.estimatedTime}>~{nextAction.estimated_time}</span>
          </div>
        )}
        
        {/* Call to Action */}
        <div className={styles.ctaText}>
          {overall_percentage < 0.9 ? 'Cliquez pour compléter' : 'Voir votre profil complet'}
        </div>
      </div>
    </div>
  );
};

export default ProfileCompletionCard;