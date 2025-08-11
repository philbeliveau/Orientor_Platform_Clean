'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import MainLayout from '@/components/layout/MainLayout';
import { getInsight, generateInsight, regenerateInsight, saveInsight, rewriteInsight, InsightData, mockInsightData } from '@/services/insightService';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import AvatarPanel from '@/components/avatar/AvatarPanel';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { useClerkApi } from '@/services/api';
import Link from 'next/link';
import LoadingScreen from '@/components/ui/LoadingScreen';

// Import our new components
import CircularProgress from '@/components/ui/CircularProgress';
import InsightCard from '@/components/ui/InsightCard';
import CourseCard from '@/components/ui/CourseCard';

const InsightPage: React.FC = () => {
  const router = useRouter();
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const api = useClerkApi();
  const [loading, setLoading] = useState<boolean>(true);
  const [insight, setInsight] = useState<InsightData | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  const [showFullText, setShowFullText] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [rewriting, setRewriting] = useState<boolean>(false);
  const [regenerating, setRegenerating] = useState<boolean>(false);
  
  // User profile state
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(undefined);
  const [userProfile, setUserProfile] = useState<any>(null);
  
  // Personality-related state
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [personalityLoading, setPersonalityLoading] = useState(true);
  const [personalityError, setPersonalityError] = useState<string | null>(null);
  
  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  // Check authentication on mount
  useEffect(() => {
    if (!isLoaded) return; // Wait for auth to load
    
    if (!isSignedIn) {
      router.push('/sign-in');
      return;
    }
  }, [isLoaded, isSignedIn, router]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    
    const loadInsight = async () => {
      try {
        setLoading(true);
        
        // Use Clerk authentication only
        console.log("Loading insight for authenticated user...");
        const token = await getToken();
        if (!token) {
          router.push('/sign-in');
          return;
        }
        
        // Try to get existing insight
        try {
          const existingData = await getInsight(token);
          if (existingData) {
            console.log("Existing insight found:", existingData);
            setInsight(existingData);
          } else {
            console.log("No existing insight found - ready for generation");
            setInsight(null);
          }
        } catch (getError) {
          console.error("Error retrieving insight:", getError);
          setInsight(null);
        }
      } catch (error) {
        console.error('Error loading insight:', error);
        setInsight(null);
      } finally {
        setLoading(false);
      }
    };

    loadInsight();
  }, [isLoaded, isSignedIn, getToken, router]);
  
  // Fetch Holland test results
  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    const fetchHollandResults = async () => {
      try {
        const token = await getToken();
        if (!token) {
          router.push('/sign-in');
          return;
        }
        
        const results = await hollandTestService.getUserLatestResults(token);
        setHollandResults(results);
      } catch (err) {
        console.error('Error fetching Holland results:', err);
        setPersonalityError('Unable to fetch Holland results');
      } finally {
        setPersonalityLoading(false);
      }
    };

    fetchHollandResults();
  }, [isLoaded, isSignedIn, getToken, router]);
  
  // Fetch user profile to get database user ID
  useEffect(() => {
    let isCancelled = false;
    
    const fetchUserProfile = async () => {
      try {
        if (!isLoaded || !isSignedIn || !user?.id) {
          return;
        }

        // Prevent duplicate requests
        if (userProfile || currentUserId) {
          return;
        }

        const profile = await api.getUserProfile();
        if (!isCancelled) {
          setUserProfile(profile);
          
          if (profile && (profile as any).id) {
            setCurrentUserId((profile as any).id);
          }
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Error fetching user profile:', err);
        }
      }
    };

    fetchUserProfile();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, userProfile, currentUserId]);

  const handleSaveInsight = async () => {
    if (!insight) return;
    
    try {
      setSaving(true);
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      await saveInsight(token, insight.full_text);
      alert('Insight sauvegardé avec succès!');
      router.push('/profile'); // Rediriger vers le profil ou une autre page appropriée
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de l\'insight:', error);
      alert('Erreur lors de la sauvegarde. Veuillez réessayer.');
    } finally {
      setSaving(false);
    }
  };

  const handleRewriteInsight = async () => {
    if (!feedback) return;
    
    try {
      setRewriting(true);
      
      // Appeler l'API même en mode développement pour tester les modifications
      console.log("Appel de l'API pour réécrire l'insight avec le feedback:", feedback);
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      const newInsight = await rewriteInsight(token, feedback);
      console.log("Réponse de l'API pour la réécriture:", newInsight);
      setInsight(newInsight);
      setFeedback('');
    } catch (error) {
      console.error('Erreur lors de la réécriture de l\'insight:', error);
      alert('Erreur lors de la réécriture. Veuillez réessayer.');
    } finally {
      setRewriting(false);
    }
  };

  const handleGenerateFirstInsight = async () => {
    try {
      setLoading(true);
      console.log("Génération du premier insight...");
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      const newInsight = await generateInsight(token);
      console.log("Premier insight généré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la génération du premier insight:', error);
      alert('Erreur lors de la génération. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateInsight = async () => {
    try {
      setRegenerating(true);
      console.log("Régénération de l'insight...");
      const token = await getToken();
      if (!token) {
        router.push('/sign-in');
        return;
      }
      const newInsight = await regenerateInsight(token);
      console.log("Insight régénéré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la régénération de l\'insight:', error);
      alert('Erreur lors de la régénération. Veuillez réessayer.');
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <MainLayout showNav={true}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-green-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-300 text-lg">Generating your insights...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Mock data for demonstration
  const progressData = [
    { label: 'Reading', value: hollandResults?.r_score || 56, color: '#64748B', icon: '📚' },
    { label: 'Analysis', value: hollandResults?.i_score || 94, color: '#10B981', icon: '🧠' },
    { label: 'Creativity', value: hollandResults?.a_score || 32, color: '#F59E0B', icon: '🎨' }
  ];

  // Remove the popularCourses variable since we're now using inline CourseCard components

  return (
    <MainLayout showNav={true}>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        {/* Header */}
        <div className="relative z-10 pt-6 pb-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link
                  href="/dashboard"
                  className="p-2 rounded-full bg-gray-800/50 text-gray-300 hover:text-white hover:bg-gray-700/50 transition-all duration-200"
                  title="Back to Dashboard"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Link>
                <h1 className="text-2xl sm:text-3xl font-light text-white">
                  Hi, {user?.firstName || 'User'} 👋
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <button className="p-2 rounded-full bg-gray-800/50 text-gray-300 hover:text-white transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
                <div className="relative">
                  <button className="p-2 rounded-full bg-gray-800/50 text-gray-300 hover:text-white transition-colors duration-200">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 19h11a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
          {/* Progress Cards Section */}
          <div className="mb-8">
            <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-12">
                {progressData.map((item, index) => (
                  <div key={index} className="flex flex-col items-center text-center">
                    <CircularProgress
                      value={item.value}
                      color={item.color}
                      size={120}
                      strokeWidth={8}
                      className="mb-4"
                    />
                    <h3 className="text-lg font-medium text-gray-300 mt-2">
                      {item.icon} {item.label}
                    </h3>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Access Cards Section */}
          <div className="mb-8">
            <h2 className="text-2xl sm:text-3xl font-light text-white mb-6">
              Personal Insights
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CourseCard
                title="Philosophical Analysis"
                description={insight ? 'View your generated philosophical insights' : 'Generate deep philosophical insights about your personality'}
                progress={insight ? 100 : 0}
                color="#F59E0B"
                icon="💡"
                onClick={() => {
                  if (!insight) {
                    handleGenerateFirstInsight();
                  } else {
                    document.getElementById('philosophical-insight')?.scrollIntoView({ behavior: 'smooth' });
                  }
                }}
              />
              <CourseCard
                title="Personality Development"
                description="Explore your RIASEC and HEXACO personality traits"
                progress={hollandResults ? 75 : 25}
                color="#10B981"
                icon="🌱"
                onClick={() => {
                  document.getElementById('personality-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
              />
            </div>
          </div>

          {/* Profile Avatar Section */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl font-light text-white mb-6">Profile Avatar</h2>
            <div className="flex flex-col lg:flex-row items-center gap-6">
              <div className="w-24 h-24 rounded-full bg-gray-700/50 flex items-center justify-center border border-gray-600/50">
                <span className="text-gray-400 text-sm">Avatar</span>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-white mb-2">Your Profile</h3>
                <p className="text-gray-300 mb-4">
                  This avatar represents your unique personality traits and skills
                </p>
                <button className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-2 rounded-xl transition-all duration-200 text-sm font-medium">
                  Customize Avatar
                </button>
              </div>
            </div>
          </div>

          {/* Skills Section */}
          {currentUserId && (
            <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
              <h2 className="text-2xl font-light text-white mb-6">Your Skills</h2>
              <SkillShowcase userId={currentUserId} />
            </div>
          )}

          {/* Avatar Profile Generation Section */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl font-light text-white mb-6">Your Avatar Profile</h2>
            <p className="text-gray-300 mb-6 leading-relaxed">
              Generate your personalized avatar based on your psychological profile and personality traits.
            </p>
            <AvatarPanel className="w-full" />
          </div>

          {/* Personality Tests Section */}
          <div id="personality-section" className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl font-light text-white mb-6">Personality Tests</h2>
            <PersonalityCard items={personalityItems} />
            
            {/* RIASEC Results */}
            {hollandResults && (
              <div className="mt-8">
                <h3 className="text-xl font-medium text-white mb-6 text-center">
                  RIASEC Personality Profile
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                  {[
                    { label: 'R', name: 'Realistic', score: hollandResults.r_score, color: 'text-red-400' },
                    { label: 'I', name: 'Investigative', score: hollandResults.i_score, color: 'text-blue-400' },
                    { label: 'A', name: 'Artistic', score: hollandResults.a_score, color: 'text-yellow-400' },
                    { label: 'S', name: 'Social', score: hollandResults.s_score, color: 'text-green-400' },
                    { label: 'E', name: 'Enterprising', score: hollandResults.e_score, color: 'text-purple-400' },
                    { label: 'C', name: 'Conventional', score: hollandResults.c_score, color: 'text-orange-400' }
                  ].map((item, index) => (
                    <div key={index} className="text-center p-4 bg-gray-800/50 rounded-2xl border border-gray-700/50 hover:bg-gray-800/70 transition-all duration-200">
                      <div className={`font-bold text-2xl ${item.color} mb-2`}>{item.label}</div>
                      <div className="text-sm text-gray-400 mb-2">{item.name}</div>
                      <div className="text-lg font-bold text-white">{item.score?.toFixed(1)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* HEXACO Placeholder */}
            <div className="mt-8 p-6 bg-blue-900/20 rounded-2xl border border-blue-700/30">
              <h3 className="text-lg font-semibold mb-3 text-blue-300">HEXACO Results</h3>
              <div className="text-sm text-blue-400">
                Take the HEXACO test to see your comprehensive personality analysis here.
              </div>
            </div>
          </div>

          {/* Philosophical Insight Section - Full Original Functionality */}
          <div id="philosophical-insight" className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl font-light text-white mb-6">Philosophical Insight</h2>
            
            {!insight && !loading && (
              <div className="text-center py-12">
                <div className="max-w-2xl mx-auto">
                  <h3 className="text-xl font-medium text-white mb-4">No Philosophical Analysis Available</h3>
                  <p className="text-gray-300 text-lg mb-8 leading-relaxed">
                    Generate your first personalized analysis based on your profile, personality tests, and reflections.
                  </p>
                  <button
                    className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium px-8 py-3 text-lg rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl"
                    onClick={handleGenerateFirstInsight}
                  >
                    Generate My Philosophical Analysis
                  </button>
                </div>
              </div>
            )}
            
            {insight && (
              <div className="space-y-8">
                {/* Accept Section */}
                <div className="bg-gradient-to-r from-green-900/30 to-green-800/20 border border-green-700/50 rounded-2xl p-6">
                  <h3 className="text-green-300 text-xl font-medium mb-4">If you accept this truth</h3>
                  <p className="text-gray-200 text-lg leading-relaxed whitespace-pre-wrap">
                    {insight.if_you_accept}
                  </p>
                </div>
                
                {/* Full Text Section */}
                <div className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700/30">
                  <h3 className="text-green-300 text-xl font-medium mb-4">Complete Analysis</h3>
                  <div className="text-gray-200 text-lg leading-relaxed whitespace-pre-wrap">
                    {insight.full_text}
                  </div>
                </div>
                
                {/* Actions Section */}
                <div className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700/30">
                  <div className="flex flex-col sm:flex-row gap-4 mb-6">
                    <button
                      className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                      onClick={handleSaveInsight}
                      disabled={saving}
                    >
                      {saving ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Saving...</span>
                        </>
                      ) : (
                        <span>Save This Analysis</span>
                      )}
                    </button>
                    
                    <button
                      className="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                      onClick={handleRegenerateInsight}
                      disabled={regenerating}
                    >
                      {regenerating ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Regenerating...</span>
                        </>
                      ) : (
                        <span>Regenerate Analysis</span>
                      )}
                    </button>
                  </div>
                  
                  <div className="border-t border-gray-700/50 pt-6">
                    <h4 className="text-green-300 text-lg font-medium mb-4">
                      Want a different perspective?
                    </h4>
                    <textarea
                      className="w-full bg-gray-700/50 border border-gray-600/50 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-transparent resize-none mb-4"
                      value={feedback}
                      onChange={(e) => setFeedback(e.target.value)}
                      placeholder="Describe what you'd like to explore differently..."
                      rows={4}
                    />
                    <button
                      className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 flex items-center space-x-2"
                      onClick={handleRewriteInsight}
                      disabled={rewriting || !feedback}
                    >
                      {rewriting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Rewriting...</span>
                        </>
                      ) : (
                        <span>Request Rewrite</span>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default InsightPage;
