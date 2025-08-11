'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Target, TrendingUp, Calendar, CheckCircle, Circle, Plus } from 'lucide-react';
import { CareerGoal } from '@/services/careerGoalsService';
import { useAuthenticatedServices } from '@/hooks/useAuthenticatedServices';

interface ColorfulCareerGoalCardProps {
  style?: React.CSSProperties;
  className?: string;
}

interface Milestone {
  task: string;
  completed: boolean;
}

export default function ColorfulCareerGoalCard({ style, className = '' }: ColorfulCareerGoalCardProps) {
  const [careerGoal, setCareerGoal] = useState<{
    title: string;
    description: string;
    targetDate: string;
    progress: number;
    milestones: Milestone[];
    hasActiveGoal: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastErrorDetails, setLastErrorDetails] = useState<{
    type: 'auth' | 'network' | 'api' | 'unknown';
    message: string;
    canRetry: boolean;
  } | null>(null);
  const { isSignedIn, isLoaded, getAuthToken } = useAuthenticatedServices();
  const isMounted = useRef(true);
  const maxRetries = 3;

  const analyzeError = (err: any) => {
    console.log('[CareerGoalCard] 🔍 Analyzing error:', err);
    
    if (err.message?.includes('Clerk not loaded') || err.message?.includes('User not signed in')) {
      return {
        type: 'auth' as const,
        message: 'Authentication issue - please sign in',
        canRetry: false
      };
    }
    
    if (err.message?.includes('Authentication required') || err.message?.includes('No authentication token')) {
      return {
        type: 'auth' as const,
        message: 'Token unavailable - refreshing session',
        canRetry: true
      };
    }
    
    if (err.message?.includes('Career goals API error: 401') || err.message?.includes('401')) {
      return {
        type: 'auth' as const,
        message: 'Session expired - please refresh',
        canRetry: true
      };
    }
    
    if (err.message?.includes('Career goals API error: 404')) {
      return {
        type: 'api' as const,
        message: 'Career goals feature not available',
        canRetry: false
      };
    }
    
    if (err.message?.includes('Career goals API error: 500')) {
      return {
        type: 'api' as const,
        message: 'Server error - trying again',
        canRetry: true
      };
    }
    
    if (err.message?.includes('NetworkError') || err.message?.includes('fetch')) {
      return {
        type: 'network' as const,
        message: 'Connection issue - retrying',
        canRetry: true
      };
    }
    
    return {
      type: 'unknown' as const,
      message: err.message || 'Something went wrong',
      canRetry: true
    };
  };

  const fetchActiveCareerGoal = async (isRetry = false) => {
    console.log('[CareerGoalCard] 🚀 Fetching career goal...', { isRetry, retryCount });
    
    if (!isLoaded || !isSignedIn) {
      if (isMounted.current) {
        setLoading(false);
        setError(null);
        setLastErrorDetails(null);
      }
      return;
    }

    try {
      if (isMounted.current) {
        setLoading(true);
        if (!isRetry) {
          setError(null);
          setLastErrorDetails(null);
        }
      }
      
      // Add small delay to prevent rapid successive calls
      await new Promise(resolve => setTimeout(resolve, isRetry ? 1000 : 200));
      if (!isMounted.current) return;
      
      // Import service directly to avoid dependency issues
      const { CareerGoalsService } = await import('@/services/careerGoalsService');
      const response = await CareerGoalsService.getActiveCareerGoal(getAuthToken);
      if (!isMounted.current) return;
      
      console.log('[CareerGoalCard] ✅ Career goal data received:', response);
      
      if (response.goal) {
        // Format the target date
        const targetDate = response.goal.target_date 
          ? new Date(response.goal.target_date).toLocaleDateString('en-US', { 
              month: 'short', 
              year: 'numeric' 
            })
          : 'No deadline';

        // Convert milestones to the expected format
        const milestones: Milestone[] = response.milestones?.slice(0, 4).map(m => ({
          task: m.skill_name,
          completed: m.is_completed
        })) || [];

        // Add placeholder milestones if we have fewer than 4
        while (milestones.length < 4) {
          milestones.push({
            task: "Complete skill assessment",
            completed: false
          });
        }

        setCareerGoal({
          title: response.goal.title,
          description: response.goal.description || "Work towards your dream career",
          targetDate,
          progress: Math.round(response.goal.progress_percentage || 0),
          milestones,
          hasActiveGoal: true
        });
        
        // Clear any previous errors on success
        setError(null);
        setLastErrorDetails(null);
        setRetryCount(0);
      } else {
        // No active goal set - this is a valid state
        console.log('[CareerGoalCard] ℹ️ No active career goal found');
        setCareerGoal({
          title: "Set Your Career Goal",
          description: "Choose a career path to start your journey",
          targetDate: "Not set",
          progress: 0,
          milestones: [
            { task: "Take personality assessments", completed: false },
            { task: "Explore career recommendations", completed: false },
            { task: "Set your first career goal", completed: false },
            { task: "Create learning timeline", completed: false }
          ],
          hasActiveGoal: false
        });
        
        setError(null);
        setLastErrorDetails(null);
      }
    } catch (err: any) {
      console.error('[CareerGoalCard] ❌ Error fetching career goal:', err);
      
      const errorDetails = analyzeError(err);
      setLastErrorDetails(errorDetails);
      
      // Only retry if the error is retryable and we haven't exceeded max retries
      if (errorDetails.canRetry && retryCount < maxRetries && !isRetry) {
        console.log(`[CareerGoalCard] 🔄 Scheduling retry ${retryCount + 1}/${maxRetries}`);
        setRetryCount(prev => prev + 1);
        setTimeout(() => {
          if (isMounted.current) {
            fetchActiveCareerGoal(true);
          }
        }, Math.min(1000 * Math.pow(2, retryCount), 5000)); // Exponential backoff, max 5s
        return;
      }
      
      // Set error state
      setError(errorDetails.message);
      
      // Fallback to default state for non-auth errors
      if (errorDetails.type !== 'auth') {
        setCareerGoal({
          title: "Set Your Career Goal",
          description: "Choose a career path to start your journey",
          targetDate: "Not set",
          progress: 0,
          milestones: [
            { task: "Take personality assessments", completed: false },
            { task: "Explore career recommendations", completed: false },
            { task: "Set your first career goal", completed: false },
            { task: "Create learning timeline", completed: false }
          ],
          hasActiveGoal: false
        });
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  };

  const handleRetry = () => {
    console.log('[CareerGoalCard] 🔄 Manual retry triggered');
    setRetryCount(0);
    setError(null);
    setLastErrorDetails(null);
    fetchActiveCareerGoal(false);
  };

  useEffect(() => {
    fetchActiveCareerGoal();
    
    return () => {
      isMounted.current = false;
    };
  }, [isLoaded, isSignedIn, getAuthToken]);

  // Show loading overlay if we have no data yet
  if (loading && !careerGoal) {
    return (
      <div 
        className={`bg-gradient-to-br from-gray-400 to-gray-500 rounded-3xl p-4 sm:p-6 shadow-lg relative overflow-hidden touch-none select-none ${className}`}
        style={{
          minHeight: '200px',
          WebkitTapHighlightColor: 'transparent',
          touchAction: 'manipulation',
          ...style
        }}
      >
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <p className="ml-3 text-white text-sm">Loading career goal...</p>
        </div>
      </div>
    );
  }

  // Show error state if we have no data
  if ((error || !careerGoal) && !loading) {
    const errorColor = lastErrorDetails?.type === 'auth' ? 'from-orange-400 to-orange-500' : 
                      lastErrorDetails?.type === 'network' ? 'from-yellow-400 to-yellow-500' :
                      'from-red-400 to-red-500';
    
    return (
      <div 
        className={`bg-gradient-to-br ${errorColor} rounded-3xl p-4 sm:p-6 shadow-lg relative overflow-hidden touch-none select-none ${className}`}
        style={{
          minHeight: '200px',
          WebkitTapHighlightColor: 'transparent',
          touchAction: 'manipulation',
          ...style
        }}
      >
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="mb-4">
            {lastErrorDetails?.type === 'auth' && (
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mb-2 mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            )}
            {lastErrorDetails?.type === 'network' && (
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mb-2 mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
              </div>
            )}
            {(lastErrorDetails?.type === 'api' || lastErrorDetails?.type === 'unknown') && (
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mb-2 mx-auto">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            )}
            
            <p className="text-white text-sm mb-2 font-medium">
              {error || 'Unable to load career goal'}
            </p>
            
            {lastErrorDetails?.type === 'auth' && (
              <p className="text-white/80 text-xs mb-3">
                Please refresh the page or sign in again
              </p>
            )}
            
            {retryCount > 0 && (
              <p className="text-white/70 text-xs mb-3">
                Attempted {retryCount}/{maxRetries} retries
              </p>
            )}
          </div>
          
          <div className="flex flex-col gap-2">
            {lastErrorDetails?.canRetry && retryCount < maxRetries && (
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white text-xs rounded-lg transition-colors backdrop-blur-sm border border-white/20"
              >
                Try Again
              </button>
            )}
            
            <Link
              href={lastErrorDetails?.type === 'auth' ? '/sign-in' : '/goals'}
              className="text-white/80 hover:text-white text-xs underline"
            >
              {lastErrorDetails?.type === 'auth' ? 'Sign In →' : 'Go to Career Goals →'}
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!careerGoal) return null; // Should never happen due to earlier checks

  const completedMilestones = careerGoal.milestones.filter(m => m.completed).length;
  const totalMilestones = careerGoal.milestones.length;

  // Dynamic styling based on whether user has an active goal and error state
  const cardColors = careerGoal.hasActiveGoal 
    ? 'from-teal-500 to-teal-600'  // Active goal - teal
    : error 
    ? 'from-gray-400 to-gray-500'  // Error state - gray
    : 'from-blue-500 to-purple-600'; // No goal but ready to start - colorful

  return (
    <div 
      className={`bg-gradient-to-br ${cardColors} rounded-3xl p-4 sm:p-6 shadow-lg hover:shadow-xl active:scale-95 transition-all duration-300 relative overflow-hidden touch-none select-none ${className}`}
      style={{
        minHeight: '200px',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation',
        ...style
      }}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3 sm:mb-4 relative z-10">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 rounded-xl sm:rounded-2xl flex items-center justify-center backdrop-blur-sm">
            {careerGoal.hasActiveGoal ? (
              <Target className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            ) : (
              <Plus className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            )}
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-semibold text-white">
              {careerGoal.hasActiveGoal ? 'Career Goal' : error ? 'Career Planning' : 'Get Started'}
            </h3>
            <div className="flex items-center gap-1 sm:gap-2">
              <Calendar className="w-3 h-3 text-white/70" />
              <span className="text-white/70 text-xs sm:text-sm">{careerGoal.targetDate}</span>
            </div>
          </div>
        </div>
        <Link
          href={careerGoal.hasActiveGoal ? "/goals" : error ? "/goals" : "/career/recommendations"}
          className="text-white/60 hover:text-white active:text-white transition-colors p-2 -m-2 rounded-lg"
          style={{ minWidth: '44px', minHeight: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {careerGoal.hasActiveGoal ? (
            <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5" />
          ) : error ? (
            <Target className="w-4 h-4 sm:w-5 sm:h-5" />
          ) : (
            <Plus className="w-4 h-4 sm:w-5 sm:h-5" />
          )}
        </Link>
      </div>

      {/* Goal Title */}
      <div className="mb-3 sm:mb-4 relative z-10">
        <h4 className="text-white text-lg sm:text-xl font-semibold mb-1 sm:mb-2">
          {careerGoal.title}
        </h4>
        <p className="text-white/80 text-xs sm:text-sm leading-relaxed line-clamp-2">
          {careerGoal.description}
        </p>
      </div>

      {/* Progress */}
      <div className="mb-4 sm:mb-6 relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white text-xs sm:text-sm font-medium">
            {careerGoal.hasActiveGoal ? 'Progress' : 'Getting Started'}
          </span>
          <span className="text-white text-xs sm:text-sm font-semibold">{careerGoal.progress}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${careerGoal.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Milestones */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <span className="text-white text-sm font-medium">
            {careerGoal.hasActiveGoal ? 'Key Milestones' : 'Next Steps'}
          </span>
          <span className="text-white/70 text-xs">{completedMilestones}/{totalMilestones} completed</span>
        </div>
        
        <div className="space-y-2">
          {careerGoal.milestones.slice(0, 3).map((milestone, index) => (
            <div key={index} className="flex items-center gap-3">
              {milestone.completed ? (
                <CheckCircle className="w-4 h-4 text-white flex-shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-white/60 flex-shrink-0" />
              )}
              <span 
                className={`text-xs flex-1 ${
                  milestone.completed ? 'text-white' : 'text-white/70'
                }`}
              >
                {milestone.task}
              </span>
            </div>
          ))}
        </div>

        {/* Action Button */}
        <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-white/20">
          <Link
            href={careerGoal.hasActiveGoal ? "/goals" : error ? "/goals" : "/career/recommendations"}
            className="inline-flex items-center gap-2 text-white text-xs sm:text-sm font-medium hover:text-white/80 active:text-white/80 transition-colors p-2 -m-2 rounded-lg"
            style={{ minHeight: '44px' }}
          >
            <span>
              {careerGoal.hasActiveGoal ? 'View Details' : error ? 'Try Career Goals' : 'Explore Careers'}
            </span>
            <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
