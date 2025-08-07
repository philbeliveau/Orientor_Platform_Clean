'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  BookOpen, ArrowLeft, Edit, Trash2, Brain, TrendingUp, 
  Calendar, User, Award, Clock, Hash, FileText, Target 
} from 'lucide-react';
import Link from 'next/link';
import { courseAnalysisService, Course, PsychologicalInsight } from '@/services/courseAnalysisService';
import { useAuth } from '@clerk/nextjs';

export default function CourseDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params ? parseInt(params.id as string) : null;
  const { getToken } = useAuth();
  
  const [course, setCourse] = useState<Course | null>(null);
  const [insights, setInsights] = useState<PsychologicalInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  useEffect(() => {
    if (courseId) {
      fetchCourseDetails();
      fetchCourseInsights();
    }
  }, [courseId]);

  const fetchCourseDetails = async () => {
    if (!courseId) return;
    try {
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }
      const courseData = await courseAnalysisService.getCourse(courseId, token);
      setCourse(courseData);
    } catch (err) {
      console.error('Error fetching course:', err);
      setError('Failed to load course details');
    }
  };

  const fetchCourseInsights = async () => {
    if (!courseId) return;
    try {
      const token = await getToken();
      if (!token) return;
      const insightsData = await courseAnalysisService.getCourseInsights(courseId, token);
      setInsights(insightsData);
    } catch (err) {
      console.error('Error fetching insights:', err);
      // Don't set error for insights as they might not exist yet
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) {
      setDeleteConfirm(true);
      return;
    }

    if (!courseId) return;

    try {
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }
      await courseAnalysisService.deleteCourse(courseId, token);
      router.push('/classes');
    } catch (err) {
      console.error('Error deleting course:', err);
      setError('Failed to delete course');
      setDeleteConfirm(false);
    }
  };

  const getSubjectColor = (category?: string) => {
    const colors = {
      'STEM': 'bg-blue-100 text-blue-800',
      'business': 'bg-green-100 text-green-800',
      'humanities': 'bg-purple-100 text-purple-800',
      'arts': 'bg-pink-100 text-pink-800',
      'social_sciences': 'bg-teal-100 text-teal-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getGradeColor = (grade?: string) => {
    if (!grade) return 'text-gray-400';
    const gradeUpper = grade.toUpperCase();
    if (['A+', 'A', 'A-'].includes(gradeUpper)) return 'text-green-600';
    if (['B+', 'B', 'B-'].includes(gradeUpper)) return 'text-blue-600';
    if (['C+', 'C', 'C-'].includes(gradeUpper)) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'cognitive_preference':
        return <Brain className="w-5 h-5" />;
      case 'work_style':
        return <TrendingUp className="w-5 h-5" />;
      case 'subject_affinity':
        return <Target className="w-5 h-5" />;
      default:
        return <Brain className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="h-64 bg-gray-300 rounded-lg"></div>
            <div className="h-48 bg-gray-300 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
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

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/classes"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Classes
          </Link>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {course.subject_category && (
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSubjectColor(course.subject_category)}`}>
                    {course.subject_category}
                  </span>
                )}
                {course.course_code && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm font-medium">
                    {course.course_code}
                  </span>
                )}
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {course.course_name}
              </h1>
              {course.professor && (
                <p className="text-lg text-gray-600">Prof. {course.professor}</p>
              )}
            </div>
            
            {course.grade && (
              <div className="text-right">
                <div className="text-sm text-gray-600 mb-1">Final Grade</div>
                <div className={`text-3xl font-bold ${getGradeColor(course.grade)}`}>
                  {course.grade}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Course Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Course Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {(course.semester || course.year) && (
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-sm text-gray-600">Semester</div>
                      <div className="font-medium">{course.semester} {course.year}</div>
                    </div>
                  </div>
                )}

                {course.credits && (
                  <div className="flex items-center gap-3">
                    <Hash className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="text-sm text-gray-600">Credits</div>
                      <div className="font-medium">{course.credits}</div>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Added</div>
                    <div className="font-medium">
                      {new Date(course.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Insights</div>
                    <div className="font-medium">{insights.length} discovered</div>
                  </div>
                </div>
              </div>

              {course.description && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                  <p className="text-gray-700 leading-relaxed">{course.description}</p>
                </div>
              )}

              {course.learning_outcomes && course.learning_outcomes.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Learning Outcomes</h4>
                  <ul className="space-y-2">
                    {course.learning_outcomes.map((outcome, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Target className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{outcome}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Psychological Insights */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Career Insights</h3>
                <Link
                  href={`/classes/${courseId}/analysis`}
                  className="text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-2 rounded-lg transition-colors flex items-center gap-1"
                >
                  <Brain className="w-4 h-4" />
                  Start Analysis
                </Link>
              </div>

              {insights.length === 0 ? (
                <div className="text-center py-8">
                  <Brain className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <h4 className="font-medium text-gray-900 mb-2">No insights discovered yet</h4>
                  <p className="text-gray-600 mb-4">
                    Start a career analysis conversation to discover insights about your preferences and strengths.
                  </p>
                  <Link
                    href={`/classes/${courseId}/analysis`}
                    className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    <Brain className="w-4 h-4" />
                    Discover Career Preferences
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {insights.map((insight) => (
                    <div key={insight.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getInsightIcon(insight.insight_type)}
                          <span className="font-medium text-gray-900">
                            {courseAnalysisService.getInsightTypeLabel(insight.insight_type)}
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">
                          {Math.round(insight.confidence_score * 100)}% confidence
                        </span>
                      </div>
                      <div className="text-gray-700 mb-2">
                        {courseAnalysisService.formatInsightValue(insight.insight_type, insight.insight_value)}
                      </div>
                      <div className="text-xs text-gray-500 italic">
                        Evidence: {insight.evidence_source}
                      </div>
                    </div>
                  ))}
                  
                  <div className="text-center pt-4">
                    <Link
                      href={`/classes/${courseId}/insights`}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      View Complete Insights Report →
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Actions */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
              <div className="space-y-3">
                <Link
                  href={`/classes/${courseId}/analysis`}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Brain className="w-5 h-5" />
                  Career Analysis
                </Link>
                
                <Link
                  href={`/classes/${courseId}/insights`}
                  className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <TrendingUp className="w-5 h-5" />
                  View Insights
                </Link>
                
                <Link
                  href={`/classes/${courseId}/edit`}
                  className="w-full border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Edit className="w-5 h-5" />
                  Edit Course
                </Link>
                
                <button
                  onClick={handleDelete}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                    deleteConfirm 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'border border-red-300 text-red-700 hover:bg-red-50'
                  }`}
                >
                  <Trash2 className="w-5 h-5" />
                  {deleteConfirm ? 'Confirm Delete' : 'Delete Course'}
                </button>
                
                {deleteConfirm && (
                  <button
                    onClick={() => setDeleteConfirm(false)}
                    className="w-full border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg text-sm transition-colors"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>

            {/* Course Stats */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Stats</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Insights Discovered</span>
                  <span className="font-semibold">{insights.length}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Analysis Confidence</span>
                  <span className="font-semibold">
                    {insights.length > 0 
                      ? `${Math.round((insights.reduce((sum, i) => sum + i.confidence_score, 0) / insights.length) * 100)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Last Updated</span>
                  <span className="font-semibold text-sm">
                    {new Date(course.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}