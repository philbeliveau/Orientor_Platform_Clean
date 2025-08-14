'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { useClerkApi } from '@/services/api';
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
  const api = useClerkApi();
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

      const data: ProfileCompletionData = await api.request('/api/v1/profiles/completion', {
        method: 'GET'
      });
      
      // Validate data consistency and log any issues
      console.log('🔍 Profile completion data received:', {
        percentage: data.overall_percentage,
        eligible: data.recommendation_eligible,
        nextActions: data.next_actions?.length || 0,
        categories: Object.keys(data.category_scores || {}).length
      });
      
      // Check for contradictory states
      if (data.overall_percentage === 0 && data.recommendation_eligible) {
        console.warn('⚠️ Inconsistent state: 0% completion but marked as eligible for recommendations');
        // Override recommendation_eligible to false for 0% completion
        data.recommendation_eligible = false;
      }
      
      if (data.overall_percentage >= 0.9 && !data.recommendation_eligible) {
        console.warn('⚠️ Inconsistent state: High completion but not eligible for recommendations');
      }
      
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

  const getMotivationalMessage = (percentage: number, isEligible: boolean, nextAction?: CompletionAction): string => {
    // Handle edge case where percentage is 0 but system says complete
    if (percentage === 0) {
      return "🌟 Commencez votre profil pour des recommandations personnalisées !";
    }
    
    // If system says complete but percentage is low, trust the percentage
    if (percentage >= 0.9 && isEligible) {
      return "🎉 Profil excellent ! Vos recommandations sont optimisées.";
    } else if (percentage >= 0.7) {
      return "✨ Presque terminé ! Quelques détails pour parfaire votre profil.";
    } else if (percentage >= 0.5) {
      return "🚀 Bon début ! Continuez pour débloquer plus de recommandations.";
    } else if (percentage >= 0.3) {
      return "💡 Votre profil prend forme ! Ajoutez plus d'informations.";
    } else if (percentage > 0 && nextAction) {
      return `📝 Prochaine étape: ${nextAction.title}`;
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
            {error ? 'Erreur de chargement - ' : ''}Completez votre profil pour des recommandations personnalisées
          </p>
          <div className={styles.ctaText}>
            {error ? 'Cliquez pour réessayer' : 'Cliquez pour commencer'}
          </div>
          {error && (
            <div className="mt-2 text-xs text-gray-500">
              Problème de connexion au serveur
            </div>
          )}
        </div>
      </div>
    );
  }

  const { overall_percentage, next_actions, recommendation_eligible } = completionData;
  const nextAction = next_actions && next_actions.length > 0 ? next_actions[0] : undefined;
  const progressColor = getProgressColor(overall_percentage);
  const message = getMotivationalMessage(overall_percentage, recommendation_eligible, nextAction);

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
        {nextAction && overall_percentage < 0.9 && (
          <div className={styles.nextAction}>
            <span className={styles.nextActionLabel}>Prochaine étape:</span>
            <span className={styles.nextActionTitle}>{nextAction.title || 'Action'}</span>
            <span className={styles.estimatedTime}>~{nextAction.estimated_time || '5 min'}</span>
          </div>
        )}
        
        {/* No next actions but incomplete profile */}
        {!nextAction && overall_percentage > 0 && overall_percentage < 0.9 && (
          <div className={styles.nextAction}>
            <span className={styles.nextActionLabel}>Continuez à compléter votre profil</span>
          </div>
        )}
        
        {/* Call to Action */}
        <div className={styles.ctaText}>
          {overall_percentage === 0 ? 'Cliquez pour commencer' : 
           overall_percentage < 0.9 ? 'Cliquez pour compléter' : 
           'Voir votre profil complet'}
        </div>
      </div>
    </div>
  );
};

export default ProfileCompletionCard;