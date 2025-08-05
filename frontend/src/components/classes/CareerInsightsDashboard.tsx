'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, TrendingUp, Users, Target, Lightbulb, Star, 
  ArrowRight, Calendar, BookOpen, BarChart3, TreePine,
  CheckCircle, AlertTriangle, Clock
} from 'lucide-react';

interface PsychologicalInsight {
  id: number;
  insight_type: string;
  insight_value: any;
  confidence_score: number;
  evidence_source: string;
  extracted_at: string;
  course_id: number;
}

interface CareerSignal {
  id: number;
  signal_type: string;
  strength_score: number;
  evidence_source: string;
  pattern_metadata?: any;
  esco_skill_mapping?: any;
  trend_analysis?: any;
  created_at: string;
}

interface ProfileSummary {
  cognitive_preferences: any;
  work_style_indicators: any;
  subject_affinities: any;
  career_readiness: any;
  confidence_score: number;
}

interface ESCORecommendation {
  recommended_paths: any[];
  skill_development_areas: any[];
  occupation_clusters: any[];
  esco_tree_entry_points: any[];
}

interface CareerInsightsDashboardProps {
  userId: number;
}

const CareerInsightsDashboard: React.FC<CareerInsightsDashboardProps> = ({ userId }) => {
  const [insights, setInsights] = useState<PsychologicalInsight[]>([]);
  const [careerSignals, setCareerSignals] = useState<CareerSignal[]>([]);
  const [profileSummary, setProfileSummary] = useState<ProfileSummary | null>(null);
  const [escoRecommendations, setEscoRecommendations] = useState<ESCORecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'all' | 'semester' | 'year'>('all');

  useEffect(() => {
    fetchPsychologicalProfile();
  }, [userId, selectedTimeframe]);

  const fetchPsychologicalProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`/api/v1/psychological-profile/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch psychological profile');
      }

      const data = await response.json();
      setProfileSummary(data.profile_summary);
      setCareerSignals(data.career_signals);
      setEscoRecommendations(data.esco_recommendations);
      
      // Flatten insights from all courses
      const allInsights: PsychologicalInsight[] = [];
      Object.values(data.insights_by_course).forEach((courseInsights: any) => {
        allInsights.push(...courseInsights);
      });
      setInsights(allInsights);
      
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Unable to load career insights');
      // Load mock data for development
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadMockData = () => {
    // Mock data for development
    setInsights([
      {
        id: 1,
        insight_type: 'cognitive_preference',
        insight_value: { preference: 'analytical_thinking', strength: 0.8 },
        confidence_score: 0.85,
        evidence_source: 'Data Science course performance analysis',
        extracted_at: '2024-01-15T10:30:00Z',
        course_id: 1
      }
    ]);
    
    setCareerSignals([
      {
        id: 1,
        signal_type: 'analytical_thinking',
        strength_score: 0.85,
        evidence_source: 'Strong performance in quantitative analysis',
        created_at: '2024-01-15T10:30:00Z'
      }
    ]);
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'cognitive_preference':
        return <Brain className="w-5 h-5" />;
      case 'work_style':
        return <Users className="w-5 h-5" />;
      case 'subject_affinity':
        return <Lightbulb className="w-5 h-5" />;
      default:
        return <Star className="w-5 h-5" />;
    }
  };

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'analytical_thinking':
        return <BarChart3 className="w-5 h-5" />;
      case 'creative_problem_solving':
        return <Lightbulb className="w-5 h-5" />;
      case 'interpersonal_skills':
        return <Users className="w-5 h-5" />;
      case 'leadership_potential':
        return <Target className="w-5 h-5" />;
      default:
        return <TrendingUp className="w-5 h-5" />;
    }
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 0.8) return 'text-green-600 bg-green-100';
    if (strength >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const getConfidenceIndicator = (confidence: number) => {
    if (confidence >= 0.8) return <CheckCircle className="w-4 h-4 text-green-600" />;
    if (confidence >= 0.6) return <Clock className="w-4 h-4 text-yellow-600" />;
    return <AlertTriangle className="w-4 h-4 text-orange-600" />;
  };

  const formatInsightValue = (type: string, value: any) => {
    if (typeof value === 'object') {
      return Object.entries(value).map(([key, val]) => (
        <span key={key} className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm mr-2 mb-1">
          {key}: {String(val)}
        </span>
      ));
    }
    return String(value);
  };

  if (loading) {
    return (
      <div className="p-8 bg-gray-50 rounded-2xl">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-300 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-32 bg-gray-300 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-2xl">
        <div className="flex items-center gap-3 text-red-700">
          <AlertTriangle className="w-6 h-6" />
          <div>
            <h3 className="font-semibold">Unable to load career insights</h3>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6 bg-gray-50 rounded-2xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Career Insights Dashboard</h2>
          <p className="text-gray-600">
            Discover your career preferences through course analysis
          </p>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value as any)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Time</option>
            <option value="semester">This Semester</option>
            <option value="year">This Year</option>
          </select>
        </div>
      </div>

      {/* Profile Summary Cards */}
      {profileSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-blue-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Cognitive Style</h3>
                <p className="text-sm text-gray-600">Thinking Preferences</p>
              </div>
            </div>
            <div className="space-y-2">
              {profileSummary.cognitive_preferences && Object.entries(profileSummary.cognitive_preferences).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-sm text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                  <span className="text-sm font-medium">{(Number(value) * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-8 h-8 text-green-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Work Style</h3>
                <p className="text-sm text-gray-600">Collaboration Preferences</p>
              </div>
            </div>
            <div className="space-y-2">
              {profileSummary.work_style_indicators && Object.entries(profileSummary.work_style_indicators).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-sm text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                  <span className="text-sm font-medium">{(Number(value) * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center gap-3 mb-4">
              <Lightbulb className="w-8 h-8 text-yellow-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Interests</h3>
                <p className="text-sm text-gray-600">Subject Affinities</p>
              </div>
            </div>
            <div className="space-y-2">
              {profileSummary.subject_affinities?.authentic_interests?.length > 0 ? (
                profileSummary.subject_affinities.authentic_interests.slice(0, 3).map((interest: any, idx: number) => (
                  <div key={idx} className="text-sm">
                    <span className="font-medium text-gray-900">{interest.subject}</span>
                    <p className="text-gray-600 text-xs">{interest.reason}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No specific interests identified yet</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-8 h-8 text-purple-600" />
              <div>
                <h3 className="font-semibold text-gray-900">Career Readiness</h3>
                <p className="text-sm text-gray-600">Overall Score</p>
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {profileSummary.confidence_score ? Math.round(profileSummary.confidence_score * 100) : 0}%
              </div>
              <p className="text-sm text-gray-600">
                {profileSummary.career_readiness?.overall_readiness ? 
                  `${Math.round(profileSummary.career_readiness.overall_readiness * 100)}% ready` : 
                  'Building readiness'
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Career Signals */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Career Signals</h3>
          </div>
          <span className="text-sm text-gray-600">{careerSignals.length} signals detected</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {careerSignals.slice(0, 6).map((signal) => (
            <div key={signal.id} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getSignalIcon(signal.signal_type)}
                  <span className="font-medium text-gray-900 capitalize">
                    {signal.signal_type.replace('_', ' ')}
                  </span>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStrengthColor(signal.strength_score)}`}>
                  {Math.round(signal.strength_score * 100)}%
                </div>
              </div>
              <p className="text-sm text-gray-600">{signal.evidence_source}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Discovered Insights */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Lightbulb className="w-6 h-6 text-yellow-600" />
            <h3 className="text-lg font-semibold text-gray-900">Psychological Insights</h3>
          </div>
          <span className="text-sm text-gray-600">{insights.length} insights discovered</span>
        </div>
        
        <div className="space-y-4">
          {insights.slice(0, 5).map((insight) => (
            <div key={insight.id} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {getInsightIcon(insight.insight_type)}
                  <div>
                    <h4 className="font-medium text-gray-900 capitalize">
                      {insight.insight_type.replace('_', ' ')}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Course {insight.course_id} • {new Date(insight.extracted_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getConfidenceIndicator(insight.confidence_score)}
                  <span className="text-sm text-gray-600">
                    {Math.round(insight.confidence_score * 100)}% confidence
                  </span>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="text-sm text-gray-700">
                  {formatInsightValue(insight.insight_type, insight.insight_value)}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 italic">
                Evidence: {insight.evidence_source}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ESCO Career Recommendations */}
      {escoRecommendations && escoRecommendations.recommended_paths.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <TreePine className="w-6 h-6 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Career Path Recommendations</h3>
            </div>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
              Explore ESCO Tree
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {escoRecommendations.recommended_paths.slice(0, 4).map((path, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{path.career_cluster || 'Career Path'}</h4>
                  <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                    {Math.round((path.alignment_score || 0.5) * 100)}% match
                  </span>
                </div>
                
                {path.occupation_examples && (
                  <div className="mb-3">
                    <p className="text-xs text-gray-600 uppercase tracking-wide mb-1">Sample Roles</p>
                    <div className="flex flex-wrap gap-1">
                      {path.occupation_examples.slice(0, 3).map((occupation: string, idx: number) => (
                        <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {occupation}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {path.next_steps && (
                  <div>
                    <p className="text-xs text-gray-600 uppercase tracking-wide mb-1">Next Steps</p>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {path.next_steps.slice(0, 2).map((step: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-blue-600 mt-1">•</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-white rounded-lg hover:shadow-md transition-shadow text-left">
            <div className="flex items-center gap-3 mb-2">
              <BookOpen className="w-5 h-5 text-blue-600" />
              <span className="font-medium">Analyze More Courses</span>
            </div>
            <p className="text-sm text-gray-600">
              Complete career analysis for your remaining courses to get deeper insights.
            </p>
          </button>
          
          <button className="p-4 bg-white rounded-lg hover:shadow-md transition-shadow text-left">
            <div className="flex items-center gap-3 mb-2">
              <TreePine className="w-5 h-5 text-green-600" />
              <span className="font-medium">Explore Career Tree</span>
            </div>
            <p className="text-sm text-gray-600">
              Use your insights to navigate the ESCO career tree and discover new opportunities.
            </p>
          </button>
          
          <button className="p-4 bg-white rounded-lg hover:shadow-md transition-shadow text-left">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-purple-600" />
              <span className="font-medium">Connect with Peers</span>
            </div>
            <p className="text-sm text-gray-600">
              Find peers with similar career interests and learn from their experiences.
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CareerInsightsDashboard;