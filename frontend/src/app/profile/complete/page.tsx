'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import NewSidebar from '@/components/layout/NewSidebar';

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

const ProfileCompletionHub: React.FC = () => {
  const router = useRouter();
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [completionData, setCompletionData] = useState<ProfileCompletionData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Navigation items for the sidebar
  const navItems = [
    { name: 'Dashboard', icon: 'Dashboard', path: '/dashboard' },
    { name: 'Education', icon: 'Education', path: '/education' },
    { name: 'Chat', icon: 'Chat', path: '/chat' },
    { name: 'Swipe', icon: 'Swipe', path: '/find-your-way' },
    { name: 'Saved', icon: 'Bookmark', path: '/space' },
    { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
    { name: 'Notes', icon: 'Note', path: '/notes' },
    { name: 'Case Study', icon: 'Case Study', path: '/case-study-journey' },
    { name: 'Competence Tree', icon: 'Tree', path: '/competence-tree' },
  ];

  useEffect(() => {
    if (!isLoaded) return;
    
    if (!isSignedIn) {
      router.push('/sign-in');
      return;
    }

    fetchCompletionData();
  }, [isLoaded, isSignedIn, router]);

  const fetchCompletionData = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      
      if (!token) {
        router.push('/sign-in');
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

  const getProgressColor = (percentage: number): string => {
    if (percentage < 0.3) return '#ef4444';
    if (percentage < 0.6) return '#f59e0b';
    if (percentage < 0.8) return '#3b82f6';
    return '#10b981';
  };

  const getCategoryDisplayName = (category: string): string => {
    const names: Record<string, string> = {
      'basic_info': 'Informations de Base',
      'career_info': 'Informations Professionnelles',
      'personality_assessments': 'Tests de Personnalité',
      'personal_details': 'Détails Personnels',
      'preferences': 'Préférences',
      'skills_goals': 'Compétences & Objectifs'
    };
    return names[category] || category;
  };

  const getCategoryIcon = (category: string): string => {
    const icons: Record<string, string> = {
      'basic_info': '👤',
      'career_info': '💼',
      'personality_assessments': '🧠',
      'personal_details': '✨',
      'preferences': '❤️',
      'skills_goals': '🎯'
    };
    return icons[category] || '📋';
  };

  const handleActionClick = (action: CompletionAction) => {
    router.push(action.url);
  };

  if (!isLoaded || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex">
        {/* Sidebar Navigation */}
        <div className="hidden md:block fixed left-0 top-0 h-full z-40">
          <div className="h-full w-20 bg-white border-r border-gray-200 shadow-lg">
            <NewSidebar navItems={navItems} />
          </div>
        </div>
        
        {/* Loading Content */}
        <div className="flex-1 md:ml-20 flex items-center justify-center">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Chargement de votre profil...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !completionData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex">
        {/* Sidebar Navigation */}
        <div className="hidden md:block fixed left-0 top-0 h-full z-40">
          <div className="h-full w-20 bg-white border-r border-gray-200 shadow-lg">
            <NewSidebar navItems={navItems} />
          </div>
        </div>
        
        {/* Error Content */}
        <div className="flex-1 md:ml-20 flex items-center justify-center">
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Erreur de Chargement</h2>
            <p className="text-gray-600 mb-6">
              Impossible de charger les données de votre profil.
            </p>
            <button
              onClick={() => fetchCompletionData()}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { overall_percentage, category_scores, next_actions, recommendation_eligible } = completionData;
  const progressColor = getProgressColor(overall_percentage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex">
      {/* Sidebar Navigation */}
      <div className="hidden md:block fixed left-0 top-0 h-full z-40">
        <div className="h-full w-20 bg-white border-r border-gray-200 shadow-lg">
          <NewSidebar navItems={navItems} />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 md:ml-20">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Completion du Profil
                </h1>
                <p className="mt-2 text-gray-600">
                  Complétez votre profil pour débloquer des recommandations personnalisées
                </p>
              </div>
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                ← Retour au Dashboard
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Progress */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Progression Globale
              </h2>
              <p className="text-gray-600">
                {recommendation_eligible ? 
                  "✅ Profil suffisant pour des recommandations personnalisées" :
                  "⏳ Complétez votre profil pour débloquer les recommandations"
                }
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold" style={{ color: progressColor }}>
                {Math.round(overall_percentage * 100)}%
              </div>
              {recommendation_eligible && (
                <div className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium mt-2">
                  Recommandations Actives
                </div>
              )}
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div 
              className="h-4 rounded-full transition-all duration-700 ease-out"
              style={{ 
                width: `${overall_percentage * 100}%`,
                backgroundColor: progressColor 
              }}
            />
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Détail par Catégorie
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(category_scores).map(([category, score]) => {
              const categoryColor = getProgressColor(score);
              return (
                <div key={category} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getCategoryIcon(category)}</span>
                      <h3 className="font-semibold text-gray-900">
                        {getCategoryDisplayName(category)}
                      </h3>
                    </div>
                    <span className="font-bold" style={{ color: categoryColor }}>
                      {Math.round(score * 100)}%
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${score * 100}%`,
                        backgroundColor: categoryColor 
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Next Actions */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Prochaines Étapes Recommandées
          </h2>
          
          {next_actions.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Félicitations ! Profil Complété
              </h3>
              <p className="text-gray-600">
                Votre profil est maintenant optimisé pour des recommandations personnalisées.
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {next_actions.map((action, index) => (
                <div 
                  key={action.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => handleActionClick(action)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                          #{index + 1}
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {action.title}
                        </h3>
                        <div className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm">
                          {action.category}
                        </div>
                      </div>
                      
                      <p className="text-gray-600 mb-3">
                        {action.description}
                      </p>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <span>⏱️</span>
                          <span>{action.estimated_time}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span>⚖️</span>
                          <span>Priorité: {Math.round(action.weight * 100)}%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-4">
                      <button 
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActionClick(action);
                        }}
                      >
                        Commencer
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-lg p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Actions Rapides
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => router.push('/profile')}
              className="bg-blue-50 hover:bg-blue-100 text-blue-700 p-4 rounded-lg transition-colors text-center"
            >
              <div className="text-2xl mb-2">👤</div>
              <div className="font-medium">Modifier Profil</div>
            </button>
            
            <button
              onClick={() => router.push('/hexaco-test')}
              className="bg-purple-50 hover:bg-purple-100 text-purple-700 p-4 rounded-lg transition-colors text-center"
            >
              <div className="text-2xl mb-2">🧠</div>
              <div className="font-medium">Test HEXACO</div>
            </button>
            
            <button
              onClick={() => router.push('/holland-test')}
              className="bg-green-50 hover:bg-green-100 text-green-700 p-4 rounded-lg transition-colors text-center"
            >
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium">Test Holland</div>
            </button>
            
            <button
              onClick={() => router.push('/self-reflection')}
              className="bg-amber-50 hover:bg-amber-100 text-amber-700 p-4 rounded-lg transition-colors text-center"
            >
              <div className="text-2xl mb-2">✨</div>
              <div className="font-medium">Réflexion</div>
            </button>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileCompletionHub;