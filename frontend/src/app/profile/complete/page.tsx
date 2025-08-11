'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import MainLayout from '@/components/layout/MainLayout';
import CircularProgress from '@/components/ui/CircularProgress';
import Link from 'next/link';

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
  const { user } = useUser();
  const [completionData, setCompletionData] = useState<ProfileCompletionData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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
    if (percentage < 0.3) return '#EF4444';
    if (percentage < 0.6) return '#F59E0B';
    if (percentage < 0.8) return '#3B82F6';
    return '#10B981';
  };

  const getCategoryDisplayName = (category: string): string => {
    const names: Record<string, string> = {
      'basic_info': 'Basic Information',
      'career_info': 'Career Information',
      'personality_assessments': 'Personality Tests',
      'personal_details': 'Personal Details',
      'preferences': 'Preferences',
      'skills_goals': 'Skills & Goals'
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
      <MainLayout showNav={true}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-green-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-300 text-lg">Loading your profile completion...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error || !completionData) {
    return (
      <MainLayout showNav={true}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
          <div className="max-w-md mx-auto bg-gray-900/60 backdrop-blur-sm rounded-3xl border border-gray-700/50 shadow-2xl p-8 text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-white mb-4">Loading Error</h2>
            <p className="text-gray-300 mb-6">
              Unable to load your profile completion data.
            </p>
            <button
              onClick={() => fetchCompletionData()}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Try Again
            </button>
          </div>
        </div>
      </MainLayout>
    );
  }

  const { overall_percentage, category_scores, next_actions, recommendation_eligible } = completionData;
  const progressColor = getProgressColor(overall_percentage);

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
                  Profile Completion
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <button className="p-2 rounded-full bg-gray-800/50 text-gray-300 hover:text-white transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </div>
            <p className="mt-4 text-gray-300 text-lg max-w-2xl">
              Complete your profile to unlock personalized recommendations and career insights.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
          {/* Overall Progress */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
              <div className="flex-1 text-center lg:text-left">
                <h2 className="text-2xl sm:text-3xl font-light text-white mb-4">
                  Overall Progress
                </h2>
                <p className="text-gray-300 text-lg leading-relaxed mb-6">
                  {recommendation_eligible ? 
                    "✅ Profile sufficient for personalized recommendations" :
                    "⏳ Complete your profile to unlock recommendations"
                  }
                </p>
                {recommendation_eligible && (
                  <div className="inline-block bg-gradient-to-r from-green-500/20 to-green-600/20 border border-green-500/30 text-green-300 px-4 py-2 rounded-xl text-sm font-medium">
                    🎯 Recommendations Active
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-center">
                <CircularProgress
                  value={overall_percentage * 100}
                  color={progressColor}
                  size={160}
                  strokeWidth={12}
                  className="drop-shadow-2xl"
                />
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl sm:text-3xl font-light text-white mb-8 text-center">
              Category Breakdown
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(category_scores).map(([category, score]) => {
                const categoryColor = getProgressColor(score);
                return (
                  <div key={category} className="bg-gray-800/40 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/30 hover:bg-gray-800/60 transition-all duration-200">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gray-700/50 rounded-xl flex items-center justify-center backdrop-blur-sm border border-gray-600/30">
                          <span className="text-2xl">{getCategoryIcon(category)}</span>
                        </div>
                        <h3 className="font-medium text-white text-lg">
                          {getCategoryDisplayName(category)}
                        </h3>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-center mb-4">
                      <CircularProgress
                        value={score * 100}
                        color={categoryColor}
                        size={80}
                        strokeWidth={6}
                      />
                    </div>
                    
                    <div className="text-center">
                      <div className="w-full bg-gray-700/40 rounded-full h-2">
                        <div 
                          className="h-2 rounded-full transition-all duration-700 ease-out"
                          style={{ 
                            width: `${score * 100}%`,
                            backgroundColor: categoryColor 
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Next Actions */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl mb-8">
            <h2 className="text-2xl sm:text-3xl font-light text-white mb-8 text-center">
              Recommended Next Steps
            </h2>
            
            {next_actions.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-8xl mb-6">🎉</div>
                <h3 className="text-2xl font-semibold text-white mb-4">
                  Congratulations! Profile Complete
                </h3>
                <p className="text-gray-300 text-lg leading-relaxed max-w-2xl mx-auto">
                  Your profile is now optimized for personalized recommendations and career insights.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {next_actions.map((action, index) => {
                  const priorityColor = getProgressColor(action.weight);
                  return (
                    <div 
                      key={action.id}
                      className="bg-gray-800/40 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/30 hover:bg-gray-800/60 transition-all duration-200 cursor-pointer group"
                      onClick={() => handleActionClick(action)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-4 mb-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500/20 to-blue-600/20 border border-blue-500/30 text-blue-300 rounded-xl flex items-center justify-center text-lg font-bold">
                              #{index + 1}
                            </div>
                            <h3 className="text-xl font-medium text-white group-hover:text-blue-300 transition-colors">
                              {action.title}
                            </h3>
                            <div className="bg-gray-700/50 text-gray-300 px-3 py-1 rounded-xl text-sm backdrop-blur-sm">
                              {action.category}
                            </div>
                          </div>
                          
                          <p className="text-gray-300 text-lg mb-6 leading-relaxed">
                            {action.description}
                          </p>
                          
                          <div className="flex items-center gap-6 text-gray-400">
                            <div className="flex items-center gap-2">
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <span>{action.estimated_time}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                              </svg>
                              <span style={{ color: priorityColor }}>Priority: {Math.round(action.weight * 100)}%</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="ml-6">
                          <button 
                            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl group-hover:scale-105"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleActionClick(action);
                            }}
                          >
                            Start Now
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-gray-900/60 backdrop-blur-sm rounded-3xl p-6 sm:p-8 border border-gray-700/50 shadow-2xl">
            <h2 className="text-2xl sm:text-3xl font-light text-white mb-8 text-center">
              Quick Actions
            </h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <button
                onClick={() => router.push('/profile')}
                className="bg-gradient-to-br from-blue-500/90 to-blue-600/90 hover:from-blue-400/95 hover:to-blue-500/95 text-white p-6 rounded-2xl transition-all duration-300 text-center transform hover:scale-105 hover:shadow-2xl border border-white/10 backdrop-blur-sm group"
              >
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/10 group-hover:bg-white/30 transition-all">
                  <span className="text-3xl">👤</span>
                </div>
                <div className="font-medium text-lg">Edit Profile</div>
                <p className="text-white/80 text-sm mt-2">Update personal information</p>
              </button>
              
              <button
                onClick={() => router.push('/hexaco-test')}
                className="bg-gradient-to-br from-purple-500/90 to-purple-600/90 hover:from-purple-400/95 hover:to-purple-500/95 text-white p-6 rounded-2xl transition-all duration-300 text-center transform hover:scale-105 hover:shadow-2xl border border-white/10 backdrop-blur-sm group"
              >
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/10 group-hover:bg-white/30 transition-all">
                  <span className="text-3xl">🧠</span>
                </div>
                <div className="font-medium text-lg">HEXACO Test</div>
                <p className="text-white/80 text-sm mt-2">Personality assessment</p>
              </button>
              
              <button
                onClick={() => router.push('/holland-test')}
                className="bg-gradient-to-br from-green-500/90 to-green-600/90 hover:from-green-400/95 hover:to-green-500/95 text-white p-6 rounded-2xl transition-all duration-300 text-center transform hover:scale-105 hover:shadow-2xl border border-white/10 backdrop-blur-sm group"
              >
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/10 group-hover:bg-white/30 transition-all">
                  <span className="text-3xl">🎯</span>
                </div>
                <div className="font-medium text-lg">Holland Test</div>
                <p className="text-white/80 text-sm mt-2">Career interests</p>
              </button>
              
              <button
                onClick={() => router.push('/self-reflection')}
                className="bg-gradient-to-br from-yellow-500/90 to-yellow-600/90 hover:from-yellow-400/95 hover:to-yellow-500/95 text-white p-6 rounded-2xl transition-all duration-300 text-center transform hover:scale-105 hover:shadow-2xl border border-white/10 backdrop-blur-sm group"
              >
                <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/10 group-hover:bg-white/30 transition-all">
                  <span className="text-3xl">✨</span>
                </div>
                <div className="font-medium text-lg">Self Reflection</div>
                <p className="text-white/80 text-sm mt-2">Personal insights</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ProfileCompletionHub;