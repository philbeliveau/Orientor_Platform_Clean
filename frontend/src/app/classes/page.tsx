'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Filter, Brain, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { courseAnalysisService, Course } from '@/services/courseAnalysisService';
import { useAuth } from '@clerk/nextjs';

export default function ClassesPage() {
  const { getToken } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterSemester, setFilterSemester] = useState<string>('all');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }
      const coursesData = await courseAnalysisService.getCourses(token);
      setCourses(coursesData);
    } catch (err) {
      console.error('Error fetching courses:', err);
      setError('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.course_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.course_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.professor?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = filterCategory === 'all' || course.subject_category === filterCategory;
    
    const matchesSemester = filterSemester === 'all' || course.semester === filterSemester;
    
    return matchesSearch && matchesCategory && matchesSemester;
  });

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

  const uniqueCategories = Array.from(new Set(courses.map(c => c.subject_category).filter((cat): cat is string => Boolean(cat))));
  const uniqueSemesters = Array.from(new Set(courses.map(c => c.semester).filter((sem): sem is string => Boolean(sem))));

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/4 mb-6"></div>
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

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-blue-600" />
              My Classes
            </h1>
            <p className="text-gray-600 mt-2">
              Manage your courses and discover career insights
            </p>
          </div>
          <Link
            href="/classes/add"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Course
          </Link>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg p-6 mb-8 shadow-sm">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search courses, codes, or professors..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {uniqueCategories.map(category => (
                <option key={category} value={category}>
                  {courseAnalysisService.getInsightTypeLabel(category)}
                </option>
              ))}
            </select>

            {/* Semester Filter */}
            <select
              value={filterSemester}
              onChange={(e) => setFilterSemester(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Semesters</option>
              {uniqueSemesters.map(semester => (
                <option key={semester} value={semester}>
                  {semester}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {filteredCourses.length === 0 && !loading && (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {courses.length === 0 ? 'No courses added yet' : 'No courses match your filters'}
            </h3>
            <p className="text-gray-600 mb-6">
              {courses.length === 0
                ? 'Start by adding your first course to unlock career insights'
                : 'Try adjusting your search or filter criteria'
              }
            </p>
            {courses.length === 0 && (
              <Link
                href="/classes/add"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                <Plus className="w-5 h-5" />
                Add Your First Course
              </Link>
            )}
          </div>
        )}

        {/* Courses Grid */}
        {filteredCourses.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <div
                key={course.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200"
              >
                <div className="p-6">
                  {/* Course Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {course.subject_category && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSubjectColor(course.subject_category)}`}>
                            {course.subject_category}
                          </span>
                        )}
                        {course.course_code && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                            {course.course_code}
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {course.course_name}
                      </h3>
                      {course.professor && (
                        <p className="text-sm text-gray-600">Prof. {course.professor}</p>
                      )}
                    </div>
                    {course.grade && (
                      <div className="text-right">
                        <span className={`text-lg font-bold ${getGradeColor(course.grade)}`}>
                          {course.grade}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Course Details */}
                  <div className="space-y-2 mb-4">
                    {(course.semester || course.year) && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>{course.semester} {course.year}</span>
                        {course.credits && (
                          <>
                            <span>•</span>
                            <span>{course.credits} credits</span>
                          </>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  {course.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {course.description}
                    </p>
                  )}

                  {/* Action Buttons */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/classes/${course.id}/analysis`}
                        className="text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1 rounded-lg transition-colors flex items-center gap-1"
                      >
                        <Brain className="w-4 h-4" />
                        Analyze
                      </Link>
                      <Link
                        href={`/classes/${course.id}/insights`}
                        className="text-sm bg-green-100 hover:bg-green-200 text-green-700 px-3 py-1 rounded-lg transition-colors flex items-center gap-1"
                      >
                        <TrendingUp className="w-4 h-4" />
                        Insights
                      </Link>
                    </div>
                    <Link
                      href={`/classes/${course.id}`}
                      className="text-sm text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quick Stats */}
        {courses.length > 0 && (
          <div className="mt-12 bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{courses.length}</div>
                <div className="text-sm text-gray-600">Total Courses</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {courses.filter(c => ['A+', 'A', 'A-'].includes(c.grade?.toUpperCase() || '')).length}
                </div>
                <div className="text-sm text-gray-600">A Grades</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{uniqueCategories.length}</div>
                <div className="text-sm text-gray-600">Subject Areas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {courses.reduce((sum, c) => sum + (c.credits || 0), 0)}
                </div>
                <div className="text-sm text-gray-600">Total Credits</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}