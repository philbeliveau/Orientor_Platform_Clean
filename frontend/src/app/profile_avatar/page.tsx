'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import AvatarPanel from '@/components/avatar/AvatarPanel';
import styles from './page.module.css';

// Interface pour simuler l'utilisateur actuel
// Dans un vrai projet, ceci viendrait d'un contexte d'authentification
interface CurrentUser {
  id: number;
  name: string;
  email: string;
}

export default function ProfileAvatarPage() {
  const router = useRouter();
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const [isLoading, setIsLoading] = useState(true);

  // Simuler la récupération de l'utilisateur actuel
  // Dans un vrai projet, ceci viendrait d'un service d'authentification
  useEffect(() => {
    if (!isLoaded) return; // Wait for auth to load
    
    if (!isSignedIn) {
      router.push('/sign-in');
      return;
    }
    
    setIsLoading(false);
  }, [isLoaded, isSignedIn, router]);

  const handleBackToHome = () => {
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p className={styles.loadingText}>Chargement...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.errorContainer}>
          <h1>Erreur d'authentification</h1>
          <p>Impossible de charger les informations utilisateur.</p>
          <button onClick={() => router.push('/')} className={styles.button}>
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.pageContainer}>
      {/* Header avec navigation */}
      <header className={styles.header}>
        <button onClick={handleBackToHome} className={styles.backButton}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Retour à l'accueil
        </button>
        
        <div className={styles.userInfo}>
          <h1 className={styles.pageTitle}>Profil Avatar</h1>
          <p className={styles.userName}>Bienvenue, {user?.fullName || user?.firstName || 'User'}</p>
        </div>
      </header>

      {/* Contenu principal */}
      <main className={styles.main}>
        <div className={styles.content}>
          <AvatarPanel className={styles.avatarPanel} />
          
          {/* Section d'informations supplémentaires */}
          <div className={styles.infoSection}>
            <h3 className={styles.infoTitle}>À propos de votre avatar</h3>
            <div className={styles.infoGrid}>
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <h4 className={styles.infoCardTitle}>Personnalisé</h4>
                <p className={styles.infoCardText}>
                  Votre avatar est généré en fonction de votre profil psychologique unique
                </p>
              </div>
              
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h4 className={styles.infoCardTitle}>IA Avancée</h4>
                <p className={styles.infoCardText}>
                  Utilise l'intelligence artificielle pour créer une représentation visuelle authentique
                </p>
              </div>
              
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 4v6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h4 className={styles.infoCardTitle}>Évolutif</h4>
                <p className={styles.infoCardText}>
                  Régénérez votre avatar à tout moment pour refléter votre évolution
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}