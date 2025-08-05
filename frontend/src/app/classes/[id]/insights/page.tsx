'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, BookOpen, Brain, TrendingUp, Target, Download, Share2 } from 'lucide-react';
import Link from 'next/link';
import { courseAnalysisService, Course, PsychologicalInsight } from '@/services/courseAnalysisService';

export default function CourseInsightsPage() {
  const params = useParams();
  const courseId = params ? parseInt(params.id as string) : null;
  
  const [course, setCourse] = useState<Course | null>(null);
  const [insights, setInsights] = useState<PsychologicalInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (courseId) {
      fetchData();
    }
  }, [courseId]);

  const fetchData = async () => {
    if (!courseId) return;
    try {
      const [courseData, insightsData] = await Promise.all([
        courseAnalysisService.getCourse(courseId),
        courseAnalysisService.getCourseInsights(courseId)
      ]);
      
      setCourse(courseData);
      setInsights(insightsData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load course insights');
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'cognitive_preference':
        return <Brain className="w-6 h-6 text-blue-600" />;
      case 'work_style':
        return <TrendingUp className="w-6 h-6 text-green-600" />;
      case 'subject_affinity':
        return <Target className="w-6 h-6 text-purple-600" />;
      default:
        return <Brain className="w-6 h-6 text-gray-600" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'cognitive_preference':
        return 'bg-blue-50 border-blue-200';
      case 'work_style':
        return 'bg-green-50 border-green-200';
      case 'subject_affinity':
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const groupInsightsByType = (insights: PsychologicalInsight[]) => {
    return insights.reduce((groups, insight) => {
      const type = insight.insight_type;
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(insight);
      return groups;
    }, {} as Record<string, PsychologicalInsight[]>);
  };

  const calculateAverageConfidence = (insights: PsychologicalInsight[]) => {
    if (insights.length === 0) return 0;
    return insights.reduce((sum, insight) => sum + insight.confidence_score, 0) / insights.length;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-48 bg-gray-300 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-red-900 mb-2">
              {error || 'Course not found'}
            </h3>
            <Link
              href="/classes"
              className="text-blue-600 hover:text-blue-700"
            >
              ← Back to Classes
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const groupedInsights = groupInsightsByType(insights);
  const averageConfidence = calculateAverageConfidence(insights);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/classes/${courseId}`}
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Course Details
          </Link>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BookOpen className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Career Insights Report
                </h1>
                <p className="text-lg text-gray-600">{course.course_name}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">{insights.length}</div>
            <div className="text-sm text-gray-600">Total Insights</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {Math.round(averageConfidence * 100)}%
            </div>
            <div className="text-sm text-gray-600">Avg. Confidence</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {Object.keys(groupedInsights).length}
            </div>
            <div className="text-sm text-gray-600">Insight Types</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">
              {course.grade || 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Course Grade</div>
          </div>
        </div>

        {/* No Insights State */}
        {insights.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Career Insights Yet
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Start a career analysis conversation to discover insights about your preferences, 
              work style, and authentic interests related to this course.
            </p>
            <Link
              href={`/classes/${courseId}/analysis`}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              <Brain className="w-5 h-5" />
              Start Career Analysis
            </Link>
          </div>
        )}

        {/* Insights by Type */}
        {Object.entries(groupedInsights).map(([type, typeInsights]) => (
          <div key={type} className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              {getInsightIcon(type)}
              <h2 className="text-xl font-semibold text-gray-900">
                {courseAnalysisService.getInsightTypeLabel(type)}
              </h2>
              <span className="text-sm text-gray-500">
                ({typeInsights.length} insight{typeInsights.length !== 1 ? 's' : ''})
              </span>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {typeInsights.map((insight) => (
                <div
                  key={insight.id}
                  className={`rounded-lg border p-6 ${getInsightColor(type)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                      {getInsightIcon(type)}
                      <span className="font-medium text-gray-900">
                        Insight #{insight.id}
                      </span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(insight.confidence_score)}`}>
                      {Math.round(insight.confidence_score * 100)}% confidence
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Discovery</h4>
                    <div className="text-gray-700">
                      {courseAnalysisService.formatInsightValue(insight.insight_type, insight.insight_value)}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Evidence</h4>
                    <p className="text-sm text-gray-600 italic">
                      {insight.evidence_source}
                    </p>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    Discovered on {new Date(insight.extracted_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Career Implications */}
        {insights.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-3">
              <Target className="w-6 h-6 text-blue-600" />
              Career Implications
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-3">Recommended Actions</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    Explore ESCO career paths that align with your discovered preferences
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    Take additional courses in areas where you show strong affinity
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    Connect with peers who have similar cognitive preferences
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    Seek internships or projects that match your work style preferences
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-3">Next Steps</h3>
                <div className="space-y-3">
                  <Link
                    href="/tree"
                    className="block p-3 bg-white rounded-lg border border-blue-200 hover:bg-blue-50 transition-colors"
                  >
                    <div className="font-medium text-blue-900">Explore Career Tree</div>
                    <div className="text-sm text-blue-700">Navigate ESCO paths based on your insights</div>
                  </Link>
                  
                  <Link
                    href="/peers"
                    className="block p-3 bg-white rounded-lg border border-blue-200 hover:bg-blue-50 transition-colors"
                  >
                    <div className="font-medium text-blue-900">Find Similar Peers</div>
                    <div className="text-sm text-blue-700">Connect with students who have similar profiles</div>
                  </Link>
                  
                  <Link
                    href="/career/recommendations"
                    className="block p-3 bg-white rounded-lg border border-blue-200 hover:bg-blue-50 transition-colors"
                  >
                    <div className="font-medium text-blue-900">View Career Recommendations</div>
                    <div className="text-sm text-blue-700">Get personalized job suggestions</div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}