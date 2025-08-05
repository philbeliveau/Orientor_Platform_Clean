'use client';

import React, { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import CareerInsightsDashboard from '@/components/classes/CareerInsightsDashboard';

export default function OverallInsightsPage() {
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Get user ID from localStorage or context
    // For now, using a mock user ID
    setUserId(1); // This should be replaced with actual user authentication
  }, []);

  if (!userId) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              Authentication Required
            </h3>
            <p className="text-yellow-800">Please log in to view your career insights.</p>
            <Link
              href="/login"
              className="inline-block mt-4 text-blue-600 hover:text-blue-700"
            >
              Go to Login →
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/classes"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Classes
          </Link>
          
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Complete Career Insights
            </h1>
            <p className="text-lg text-gray-600">
              Your comprehensive psychological profile and career recommendations
            </p>
          </div>
        </div>

        {/* Dashboard */}
        <CareerInsightsDashboard userId={userId} />
      </div>
    </div>
  );
}