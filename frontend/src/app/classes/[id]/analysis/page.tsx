'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, BookOpen } from 'lucide-react';
import Link from 'next/link';
import { courseAnalysisService, Course } from '@/services/courseAnalysisService';
import CareerAnalysisChat from '@/components/classes/CareerAnalysisChat';

export default function CourseAnalysisPage() {
  const params = useParams();
  const courseId = params ? parseInt(params.id as string) : null;
  
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (courseId) {
      fetchCourseDetails();
    }
  }, [courseId]);

  const fetchCourseDetails = async () => {
    if (!courseId) return;
    try {
      const courseData = await courseAnalysisService.getCourse(courseId);
      setCourse(courseData);
    } catch (err) {
      console.error('Error fetching course:', err);
      setError('Failed to load course details');
    } finally {
      setLoading(false);
    }
  };

  const handleInsightsDiscovered = (insights: any[]) => {
    console.log('New insights discovered:', insights);
    // Could trigger notifications or updates here
  };

  const handleSessionComplete = (summary: any) => {
    console.log('Analysis session complete:', summary);
    // Could redirect to insights page or show completion modal
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-300 rounded w-1/3"></div>
            <div className="h-96 bg-gray-300 rounded-lg"></div>
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
            href={`/classes/${courseId}`}
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Course Details
          </Link>
          
          <div className="flex items-center gap-4 mb-4">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Career Analysis Session
              </h1>
              <p className="text-lg text-gray-600">{course.course_name}</p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">About This Analysis</h3>
            <p className="text-blue-800 text-sm">
              This AI-powered conversation will help you discover your authentic career preferences 
              through thoughtful questions about your experience in {course.course_name}. 
              The insights discovered will be used to personalize your career recommendations 
              and guide your exploration of the ESCO career tree.
            </p>
          </div>
        </div>

        {/* Course Context Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Context</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-600">Subject</div>
              <div className="font-medium">{course.subject_category || 'Not specified'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Period</div>
              <div className="font-medium">{course.semester} {course.year}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Grade</div>
              <div className="font-medium">{course.grade || 'Not graded yet'}</div>
            </div>
          </div>
          {course.professor && (
            <div className="mt-4">
              <div className="text-sm text-gray-600">Professor</div>
              <div className="font-medium">{course.professor}</div>
            </div>
          )}
          {course.description && (
            <div className="mt-4">
              <div className="text-sm text-gray-600">Description</div>
              <div className="text-gray-700">{course.description}</div>
            </div>
          )}
        </div>

        {/* Analysis Chat Interface */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {courseId && (
            <CareerAnalysisChat
              courseId={courseId}
              courseName={course.course_name}
              onInsightsDiscovered={handleInsightsDiscovered}
              onSessionComplete={handleSessionComplete}
            />
          )}
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-gray-100 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Tips for Better Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
            <div>
              <h4 className="font-medium mb-2">Be Honest & Reflective</h4>
              <ul className="space-y-1 text-xs">
                <li>• Share your genuine feelings about the course</li>
                <li>• Reflect on what truly engaged or challenged you</li>
                <li>• Consider your natural reactions and preferences</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Provide Specific Examples</h4>
              <ul className="space-y-1 text-xs">
                <li>• Mention specific assignments or projects</li>
                <li>• Describe particular moments of clarity or confusion</li>
                <li>• Compare this course to others you've taken</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Think About Your Process</h4>
              <ul className="space-y-1 text-xs">
                <li>• How did you approach problem-solving?</li>
                <li>• What study methods worked best for you?</li>
                <li>• How did you interact with classmates and professors?</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Consider Your Future</h4>
              <ul className="space-y-1 text-xs">
                <li>• What aspects might relate to career work?</li>
                <li>• Which skills feel naturally developed?</li>
                <li>• What would you want to do more or less of?</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}