'use client';
import React, { useState, useEffect } from 'react';
import AvatarCard from './AvatarCard';
import AvatarService, { AvatarData } from '@/services/avatarService';
import styles from './AvatarPanel.module.css';
import LoadingScreen from '@/components/ui/LoadingScreen';
import { useAuth } from '@clerk/nextjs';

interface AvatarPanelProps {
  className?: string;
}

const AvatarPanel: React.FC<AvatarPanelProps> = ({ className = '' }) => {
  const { getToken } = useAuth();
  const [avatarData, setAvatarData] = useState<AvatarData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Charger l'avatar existant au montage du composant
  useEffect(() => {
    let isCancelled = false;
    
    const loadAvatar = async () => {
      // Prevent duplicate requests
      if (avatarData !== null || isLoading) {
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        const token = await getToken();
        if (!token || isCancelled) {
          return;
        }
        const data = await AvatarService.getUserAvatar(token);
        if (!isCancelled) {
          setAvatarData(data);
        }
      } catch (err: any) {
        if (!isCancelled) {
          console.log('Aucun avatar existant trouvé');
          setAvatarData(null);
          setError(null);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    loadAvatar();
    
    return () => {
      isCancelled = true;
    };
  }, [avatarData, isLoading]); // Added state checks

  const loadUserAvatar = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }
      const data = await AvatarService.getUserAvatar(token);
      setAvatarData(data);
    } catch (err: any) {
      console.log('Aucun avatar existant trouvé');
      setAvatarData(null);
      setError(null); // Ne pas afficher d'erreur si aucun avatar n'existe
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAvatar = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }
      
      const response = await AvatarService.generateAvatar(token);
      
      // Mettre à jour les données d'avatar avec la réponse
      setAvatarData({
        success: true,
        avatar_name: response.avatar_name,
        avatar_description: response.avatar_description,
        avatar_image_url: response.avatar_image_url,
        generated_at: response.generated_at
      });
      
    } catch (err: any) {
      const errorMessage = AvatarService.handleAvatarError(err);
      setError(errorMessage);
      console.error('Erreur lors de la génération de l\'avatar:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const hasAvatar = avatarData?.success && avatarData?.avatar_name;
  const avatarImageUrl = avatarData?.avatar_image_url 
    ? AvatarService.getAvatarImageUrl(avatarData.avatar_image_url)
    : undefined;

  if (isLoading) {
    return <LoadingScreen message="Chargement de votre avatar..." />;
  }

  return (
    <div className={`${styles.avatarPanel} ${className}`}>
      <div className={styles.header}>
        <h2 className={styles.title}>Mon Avatar</h2>
        <p className={styles.subtitle}>
          {hasAvatar 
            ? 'Votre avatar personnalisé basé sur votre profil'
            : 'Générez votre avatar personnalisé basé sur votre profil psychologique'
          }
        </p>
      </div>

      <div className={styles.content}>
        <AvatarCard
          avatarName={avatarData?.avatar_name}
          avatarDescription={avatarData?.avatar_description}
          avatarImageUrl={avatarImageUrl}
          isLoading={isGenerating}
          className={styles.avatarCard}
        />

        <div className={styles.actions}>
          {hasAvatar ? (
            <div className={styles.avatarActions}>
              <button
                onClick={handleGenerateAvatar}
                disabled={isGenerating}
                className={`${styles.button} ${styles.regenerateButton}`}
              >
                {isGenerating ? (
                  <>
                    <div className={styles.buttonSpinner}></div>
                    Régénération...
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 4v6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Régénérer l'Avatar
                  </>
                )}
              </button>
              
              {avatarData?.generated_at && (
                <p className={styles.generatedDate}>
                  Généré le {new Date(avatarData.generated_at).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              )}
            </div>
          ) : (
            <button
              onClick={handleGenerateAvatar}
              disabled={isGenerating}
              className={`${styles.button} ${styles.generateButton}`}
            >
              {isGenerating ? (
                <>
                  <div className={styles.buttonSpinner}></div>
                  Génération en cours...
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Generate My Avatar
                </>
              )}
            </button>
          )}
        </div>

        {error && (
          <div className={styles.errorContainer}>
            <div className={styles.errorIcon}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" strokeWidth="2"/>
                <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <p className={styles.errorText}>{error}</p>
            <button 
              onClick={() => setError(null)}
              className={styles.dismissButton}
            >
              Fermer
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AvatarPanel;