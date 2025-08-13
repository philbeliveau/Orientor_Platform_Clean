'use client';

import React, { useState, useEffect, useMemo } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useRouter } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import Link from 'next/link';
import UserCard from '@/components/ui/UserCard';
import ProfileCompletionCard from '@/components/ui/ProfileCompletionCard';
import ColorfulCareerGoalCard from '@/components/ui/ColorfulCareerGoalCard';
import EnhancedClassesCard from '@/components/classes/EnhancedClassesCard';
import Calendar from '@/components/ui/Calendar';
import EventsNotes from '@/components/ui/EventsNotes';
import JobRecommendationVerticalList from '@/components/jobs/JobRecommendationVerticalList';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import StarConstellation from '@/components/ui/StarConstellation';
import VectorSearchCard from '@/components/search/VectorSearchCard';
import CareerGoalCard from '@/components/ui/CareerGoalCard';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { useClerkApi } from '@/services/api';
import { Job } from '@/components/jobs/JobCard';
import { fetchAllUserNotes, Note } from '@/services/spaceService';
import axios from 'axios';
import SaveJobButton from '@/components/common/SaveJobButton';
import { useOnboardingService } from '@/services/onboardingService';

interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
}

interface EnhancedPeerProfile {
  user_id: number;
  name: string;
  major: string;
  year?: number;
  job_title?: string;
  industry?: string;
  compatibility_score: number;
  explanation: string;
  score_details: {
    overall_compatibility: number;
    timestamp: string;
  };
}

export default function Dashboard() {
  const router = useRouter();
  
  // Protect this route - redirect unauthenticated users to landing page
  const { isLoaded, isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const api = useClerkApi();
  const onboardingService = useOnboardingService();
  
  // Define API URL with fallback and trim any trailing spaces
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const cleanApiUrl = API_URL ? API_URL.trim() : '';
  
  // State
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [onboardingStatus, setOnboardingStatus] = useState<{isComplete: boolean, hasStarted: boolean} | null>(null);
  const [checkingOnboarding, setCheckingOnboarding] = useState(true);
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(1); // Default to 1 for authenticated users
  const [userProfile, setUserProfile] = useState<any>(null);
  const [peers, setPeers] = useState<EnhancedPeerProfile[]>([]);
  const [peersLoading, setPeersLoading] = useState(true);
  const [peersError, setPeersError] = useState<string | null>(null);
  const [userNotes, setUserNotes] = useState<Note[]>([]);
  const [notesLoading, setNotesLoading] = useState(true);
  const [notesError, setNotesError] = useState<string | null>(null);

  // User data from Clerk
  const userData = {
    name: user?.firstName && user?.lastName ? `${user.firstName} ${user.lastName}` : user?.username || 'User',
    role: 'Étudiant Msc. in Data Science',
    level: 3,
    avatarUrl: user?.imageUrl || '/Avatar.PNG',
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    totalXP: 250,
  };

  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  // Check onboarding status first - this is critical for new users
  useEffect(() => {
    let isCancelled = false;
    let timeoutId: NodeJS.Timeout;
    
    const checkOnboardingStatus = async () => {
      try {
        if (!isLoaded || !isSignedIn || !user?.id || isCancelled) {
          return;
        }

        console.log('🔍 Dashboard: Checking onboarding status for user:', user.id);
        
        // Create a timeout promise to prevent hanging
        const timeoutPromise = new Promise((_, reject) => {
          timeoutId = setTimeout(() => {
            reject(new Error('Onboarding status check timeout'));
          }, 10000); // 10 second timeout
        });
        
        // Race between API call and timeout
        const status = await Promise.race([
          onboardingService.getStatus(),
          timeoutPromise
        ]) as any;
        
        // Clear timeout if request completed
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        
        console.log('📊 Onboarding status:', status);
        console.log('📊 DEBUG: isComplete value:', status.isComplete, 'type:', typeof status.isComplete);
        
        if (!isCancelled) {
          setOnboardingStatus(status);
          
          // Enhanced debug logging for onboarding check
          console.log('🔍 ONBOARDING CHECK:', {
            isComplete: status.isComplete,
            hasStarted: status.hasStarted,
            shouldRedirect: !status.isComplete,
            originalStatus: status
          });
          
          if (!status.isComplete) {
            console.log('⚠️ User has not completed onboarding, redirecting...');
            router.push('/onboarding');
            return;
          } else {
            console.log('✅ User has completed onboarding, staying on dashboard');
          }
        }
      } catch (error: any) {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        
        if (!isCancelled) {
          console.error('❌ Error checking onboarding status:', error);
          
          if (error.message?.includes('timeout')) {
            console.log('⏰ Onboarding check timed out, will show loading screen');
            // Don't redirect on timeout, let user try refreshing
            setCheckingOnboarding(false);
            return;
          } else if (error.message?.includes('Authentication service not available')) {
            console.log('🔄 Authentication service initializing, will retry...');
            // Don't redirect, let them try again
          } else if (error.message?.includes('not authenticated') || error.message?.includes('401')) {
            console.log('🔑 Not authenticated, redirecting to sign-in');
            router.push('/sign-in');
            return;
          } else {
            console.log('⚠️ Cannot verify onboarding status, assuming incomplete for safety');
            router.push('/onboarding');
            return;
          }
        }
      } finally {
        if (!isCancelled) {
          setCheckingOnboarding(false);
        }
      }
    };

    checkOnboardingStatus();
    
    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isLoaded, isSignedIn, user?.id, router]); // Removed onboardingService to prevent infinite loop

  // Fetch user data and Holland results
  useEffect(() => {
    let isCancelled = false;
    
    const fetchHollandResults = async () => {
      try {
        if (!isLoaded || !isSignedIn || !user?.id || isCancelled) {
          return;
        }

        const token = await getToken();
        if (!token || isCancelled) {
          return;
        }

        if (!isCancelled) {
          setLoading(true);
          setError(null);
        }

        const results = await api.getHollandResults();
        if (!isCancelled) {
          setHollandResults(results as ScoreResponse);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Error fetching Holland results:', err);
          setError('Unable to fetch Holland results');
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    fetchHollandResults();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, getToken]); // Added getToken for stability

  // Fetch job recommendations
  useEffect(() => {
    let isCancelled = false;
    
    const fetchJobRecommendations = async () => {
      try {
        if (!isLoaded || !isSignedIn || !user?.id || isCancelled) {
          return;
        }

        const token = await getToken();
        if (!token || isCancelled) {
          return;
        }

        if (!isCancelled) {
          setJobsLoading(true);
          setJobsError(null);
        }
        
        const response = await api.getJobRecommendations(3) as JobRecommendationsResponse;
        
        if (response && response.recommendations && !isCancelled) {
          const limitedRecommendations = response.recommendations.slice(0, 3);
          setJobRecommendations(limitedRecommendations);
          
          if (limitedRecommendations.length > 0) {
            setSelectedJob(limitedRecommendations[0]);
          }
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Error fetching job recommendations:', err);
          setJobsError('Unable to fetch job recommendations');
        }
      } finally {
        if (!isCancelled) {
          setJobsLoading(false);
        }
      }
    };
    
    fetchJobRecommendations();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, getToken]); // Added getToken for stability

  // Fetch top peers
  useEffect(() => {
    let isCancelled = false;
    let retryCount = 0;
    const maxRetries = 3;
    
    const fetchPeers = async () => {
      if (!isLoaded || !isSignedIn || !user?.id) return;
      
      try {
        setPeersLoading(true);
        setPeersError(null);
        
        const peersResponse = await api.request<EnhancedPeerProfile[]>('/api/v1/peers/compatible', {
          method: 'GET'
        });
        
        if (!isCancelled) {
          // Ensure we have an array and get top 3 peers for homepage
          const peersArray = Array.isArray(peersResponse) ? peersResponse : [];
          const topPeers = peersArray.slice(0, 3);
          setPeers(topPeers);
        }
      } catch (err: any) {
        if (!isCancelled) {
          console.error('Error fetching peers:', err);
          
          // Only retry on network errors or 500s, not on auth errors
          if (retryCount < maxRetries && 
              (!err.message?.includes('401') && !err.message?.includes('Unauthorized'))) {
            retryCount++;
            setTimeout(() => {
              if (!isCancelled) {
                fetchPeers();
              }
            }, 1000 * retryCount); // Exponential backoff
          } else {
            setPeersError('Unable to fetch peer recommendations');
          }
        }
      } finally {
        if (!isCancelled) {
          setPeersLoading(false);
        }
      }
    };

    fetchPeers();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, getToken]); // Added getToken back for stability

  // Fetch user notes
  useEffect(() => {
    let isCancelled = false;
    
    const fetchNotes = async () => {
      try {
        // Enhanced authentication guard
        if (!isLoaded || !isSignedIn || !user?.id) {
          return;
        }

        // Check token availability before making request
        const token = await getToken();
        if (!token || isCancelled) {
          return;
        }

        setNotesLoading(true);
        setNotesError(null);
        
        const notes = await fetchAllUserNotes(getToken);
        if (!isCancelled) {
          // Get top 3 most recent notes for home page
          const notesArray = Array.isArray(notes) ? notes : [];
          const recentNotes = notesArray.slice(0, 3);
          setUserNotes(recentNotes);
        }
      } catch (err: any) {
        if (!isCancelled) {
          console.error('Error fetching user notes:', err);
          setNotesError('Unable to fetch notes');
        }
      } finally {
        if (!isCancelled) {
          setNotesLoading(false);
        }
      }
    };

    fetchNotes();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, getToken]); // Added getToken for stability

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  // Fetch user profile to get database user ID
  useEffect(() => {
    let isCancelled = false;
    
    const fetchUserProfile = async () => {
      try {
        if (!isLoaded || !isSignedIn || !user?.id) {
          console.log('🔍 Profile fetch skipped - auth not ready:', { isLoaded, isSignedIn, userId: user?.id });
          return;
        }

        // Prevent duplicate requests - only check if we already have the profile
        if (userProfile) {
          console.log('🔍 Profile fetch skipped - already have profile');
          return;
        }

        console.log('📊 Fetching user profile...');
        const profileResponse = await api.getUserProfile();
        console.log('📊 User profile response:', profileResponse);
        
        // Extract data from the API response
        const profileData = profileResponse.data || profileResponse;
        console.log('📊 Extracted profile data:', profileData);
        
        if (!isCancelled) {
          setUserProfile(profileData);
          
          if (profileData && profileData.id) {
            setCurrentUserId(profileData.id);
            console.log('📊 Set currentUserId to:', profileData.id);
          } else {
            console.warn('⚠️ Profile response missing id field, using fallback:', profileData);
            // Set a default currentUserId since we know user exists
            setCurrentUserId(1);
            console.log('📊 Set fallback currentUserId to: 1');
          }
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('❌ Error fetching user profile:', err);
          // Set a fallback currentUserId so the dashboard can still render
          console.log('📊 Setting fallback currentUserId due to profile error');
          setCurrentUserId(1);
        }
      }
    };

    fetchUserProfile();
    
    return () => {
      isCancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id, api]); // Removed userProfile, currentUserId to prevent loops

  // Show loading while checking authentication or during SSR
  if (typeof window === 'undefined' || !isLoaded || checkingOnboarding) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600 mt-4 text-center">
          {checkingOnboarding ? 'Verifying onboarding status...' : 'Loading dashboard...'}
        </p>
        {checkingOnboarding && (
          <div className="mt-4 text-center max-w-md">
            <p className="text-sm text-gray-500">
              If this takes longer than expected, please try refreshing the page.
            </p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-2 text-blue-600 hover:text-blue-800 text-sm underline"
            >
              Refresh Page
            </button>
          </div>
        )}
      </div>
    );
  }

  // Redirect to sign-in if not authenticated
  if (!isSignedIn) {
    router.push('/sign-in');
    return null;
  }

  // Only require user to be loaded from Clerk - currentUserId is optional
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading user data...</p>
      </div>
    );
  }

  return (
    <MainLayout>
      <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
            {/* Mobile-First Layout Stack - Progress and Focus in one row */}
            <div className="flex flex-col gap-6 mb-8">
              
              {/* Single Row: All cards with same dimensions */}
              <div className="w-full">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  
                  {/* My Progress Section */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2" style={{ color: '#000000' }}>My Progress</h2>
                    <div className="w-full">
                      <UserCard
                        name={userData.name}
                        role={userData.role}
                        skills={userData.skills}
                        hollandResults={hollandResults}
                        loading={loading}
                        error={error}
                        className="w-full"
                        style={{
                          width: '100%',
                          height: '220px',
                          borderRadius: '24px',
                          background: '#e0e0e0',
                          boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                        }}
                      />
                    </div>
                  </div>

                  {/* Profile Completion Card */}
                  <div className="w-full">
                    <ProfileCompletionCard />
                  </div>

                  {/* Career Goal Card */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2 opacity-0" style={{ color: '#000000' }}>Hidden</h2>
                    <ColorfulCareerGoalCard
                      style={{ height: '220px' }}
                    />
                  </div>

                  {/* Classes Card */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2 opacity-0" style={{ color: '#000000' }}>Hidden</h2>
                    <EnhancedClassesCard
                      userId={currentUserId || 1}
                      style={{ height: '220px' }}
                    />
                  </div>
                  
                </div>
              </div>

              {/* Mobile: Calendar moved to bottom, full width on mobile */}
              <div className="w-full lg:hidden">
                <h2 className="text-lg font-semibold mb-4 px-2" style={{ color: '#000000' }}>Schedule</h2>
                <Calendar 
                  events={[
                    { id: '1', date: new Date(2025, 0, 20), title: 'Holland Test Review', type: 'test' },
                    { id: '2', date: new Date(2025, 0, 25), title: 'Career Challenge', type: 'challenge' },
                    { id: '3', date: new Date(2025, 0, 28), title: 'Peer Meetup', type: 'event' }
                  ]}
                  onDateClick={(date) => console.log('Date clicked:', date)}
                />
              </div>
            </div>

            {/* Mobile-First Content Sections */}
            <div className="flex flex-col lg:grid lg:grid-cols-12 gap-6 mb-8">
              {/* Activity Section - Full width on mobile */}
              <div className="w-full lg:col-span-4 xl:col-span-3">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Activity</h2>
                  <Link
                    href="/peers"
                    className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    <span>3</span>
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
                    </svg>
                  </Link>
                </div>
                
                {/* Search bar */}
                <div className="mb-4">
                  <div className="relative">
                    <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                    </svg>
                    <input
                      type="text"
                      placeholder="Find update"
                      className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-200"
                    />
                  </div>
                </div>
                
                {peersLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-sm text-gray-600 mt-2">Loading peers...</p>
                  </div>
                ) : peersError ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-red-600">{peersError}</p>
                  </div>
                ) : peers.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-gray-600">No peer recommendations available</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {peers.map((peer) => (
                      <div
                        key={peer.user_id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                        onClick={() => router.push(`/peers/${peer.user_id}`)}
                      >
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                          {peer.name && peer.name.charAt(0) ? peer.name.charAt(0).toUpperCase() : '?'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start">
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-sm text-gray-900 truncate">
                                {peer.name || `User ${peer.user_id}`}
                              </h3>
                              <p className="text-xs text-gray-500 mt-1">
                                {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                              </p>
                            </div>
                            <div className="flex flex-col items-end ml-2">
                              <span className="text-xs text-gray-400">Jan 2, 12:30</span>
                              <span className="text-xs text-blue-600 font-medium mt-1">
                                {Math.round((peer.compatibility_score || 0) * 100)}% match
                              </span>
                            </div>
                          </div>
                        </div>
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256" className="text-gray-300">
                          <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                        </svg>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Job Recommendations - Full width on mobile, larger on desktop */}
              <div className="w-full lg:col-span-5 xl:col-span-6">
                <div className="mb-6">
                  <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Recommended Jobs</h2>
                </div>
                
                {/* Original Recommendations */}
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-medium text-gray-700">Your Personalized Recommendations</h3>
                    <Link
                      href="/career/recommendations"
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <span>See all</span>
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                        <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                      </svg>
                    </Link>
                  </div>
                  {jobsLoading ? (
                    <div className="text-center py-6">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-xs text-gray-600 mt-2">Loading recommendations...</p>
                    </div>
                  ) : jobsError ? (
                    <div className="text-center py-6">
                      <p className="text-xs text-red-600">{jobsError}</p>
                    </div>
                  ) : jobRecommendations.length === 0 ? (
                    <div className="text-center py-6">
                      <p className="text-xs text-gray-600">No job recommendations available</p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {jobRecommendations.map((job) => (
                        <div
                          key={job.id}
                          className="p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                          onClick={() => handleSelectJob(job)}
                        >
                          <h4 className="font-medium text-sm mb-1">
                            {(() => {
                              // Try different possible title fields
                              const possibleTitles = [
                                job.metadata?.preferred_label,
                                job.metadata?.title,
                                job.metadata?.label,
                                job.metadata?.occupation_label,
                                job.metadata?.job_title,
                                job.metadata?.name,
                                (job as any)?.label, // Direct property (like in JobRecommendationVerticalList)
                                (job as any)?.title,
                                (job as any)?.job_title,
                                (job as any)?.occupation_label
                              ];
                              
                              const title = possibleTitles.find(t => t && t.trim() !== '');
                              return title || `Career Opportunity ${job.id}`;
                            })()}
                          </h4>
                          <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                            {job.metadata.description || 'No description available'}
                          </p>
                          <div className="flex justify-between items-center">
                            <div className="text-xs text-blue-600 font-medium">
                              {Math.round(job.score * 100)}% match
                            </div>
                            <div className="flex items-center gap-2">
                              {job.metadata.skills && job.metadata.skills.length > 0 && (
                                <div className="flex gap-1 flex-wrap">
                                  {job.metadata.skills.slice(0, 2).map((skill, index) => (
                                    <span
                                      key={index}
                                      className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <SaveJobButton job={job} size="sm" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Vector Search Integration - Moved below recommendations */}
                <div className="mb-4">
                  <VectorSearchCard />
                </div>
              </div>

              {/* Events & Notes + Desktop Calendar */}
              <div className="w-full lg:col-span-3">
                {/* Desktop Calendar - Hidden on mobile */}
                <div className="hidden lg:block mb-6">
                  <h2 className="text-lg font-semibold mb-4" style={{ color: '#000000' }}>Schedule</h2>
                  <Calendar 
                    events={[
                      { id: '1', date: new Date(2025, 0, 20), title: 'Holland Test Review', type: 'test' },
                      { id: '2', date: new Date(2025, 0, 25), title: 'Career Challenge', type: 'challenge' },
                      { id: '3', date: new Date(2025, 0, 28), title: 'Peer Meetup', type: 'event' }
                    ]}
                    onDateClick={(date) => console.log('Date clicked:', date)}
                  />
                </div>
                <EventsNotes
                  events={[
                    {
                      id: '1',
                      title: 'Holland Test Review',
                      date: new Date(2025, 0, 20),
                      type: 'test',
                      description: 'Review your personality test results'
                    },
                    {
                      id: '2',
                      title: 'Career Challenge',
                      date: new Date(2025, 0, 25),
                      type: 'challenge',
                      description: 'Complete the data analysis challenge'
                    }
                  ]}
                  notes={notesLoading ? [] : notesError ? [] : userNotes.map(note => ({
                    id: note.id,
                    title: note.content && note.content.length > 50 ? `${note.content.substring(0, 50)}...` : (note.content || 'Untitled'),
                    content: note.content && note.content.length > 100 ? `${note.content.substring(0, 100)}...` : (note.content || ''),
                    createdAt: new Date(note.created_at),
                    recommendationId: note.saved_recommendation_id
                  }))}
                  onEventClick={(event) => console.log('Event clicked:', event)}
                  onNoteClick={(note) => router.push('/notes')}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
