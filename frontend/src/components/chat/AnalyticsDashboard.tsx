import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  ClockIcon,
  FireIcon,
  HashtagIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

interface Analytics {
  user_analytics: {
    period: string;
    total_messages: number;
    total_conversations: number;
    total_tokens_used: number;
    avg_response_time_ms: number;
    active_days: number;
    conversation_count: number;
    favorite_categories: Array<{ name: string; count: number }>;
  };
  usage_trends: {
    period_days: number;
    daily_messages: Array<{ date: string; count: number }>;
    growth_rate_percent: number;
  };
  popular_topics: Array<{
    name: string;
    count: number;
    percentage: number;
  }>;
}

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<'week' | 'month' | 'year'>('month');

  useEffect(() => {
    fetchAnalytics();
  }, [period]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/analytics/summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12 text-gray-500">
        <ChartBarIcon className="w-16 h-16 mx-auto mb-4 opacity-20" />
        <p>No analytics data available</p>
      </div>
    );
  }

  const { user_analytics, usage_trends, popular_topics } = analytics;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center">
          <ChartBarIcon className="w-6 h-6 mr-2" />
          Chat Analytics
        </h2>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value as typeof period)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="week">Last 7 days</option>
          <option value="month">Last 30 days</option>
          <option value="year">Last year</option>
        </select>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-500" />
            <span className="text-sm text-gray-500">Messages</span>
          </div>
          <div className="text-2xl font-bold">{user_analytics.total_messages}</div>
          <div className="text-sm text-gray-500">
            {user_analytics.total_conversations} conversations
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <ClockIcon className="w-8 h-8 text-green-500" />
            <span className="text-sm text-gray-500">Avg Response</span>
          </div>
          <div className="text-2xl font-bold">
            {(user_analytics.avg_response_time_ms / 1000).toFixed(1)}s
          </div>
          <div className="text-sm text-gray-500">response time</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <FireIcon className="w-8 h-8 text-orange-500" />
            <span className="text-sm text-gray-500">Activity</span>
          </div>
          <div className="text-2xl font-bold">{user_analytics.active_days}</div>
          <div className="text-sm text-gray-500">active days</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <HashtagIcon className="w-8 h-8 text-purple-500" />
            <span className="text-sm text-gray-500">Tokens</span>
          </div>
          <div className="text-2xl font-bold">
            {(user_analytics.total_tokens_used / 1000).toFixed(1)}k
          </div>
          <div className="text-sm text-gray-500">tokens used</div>
        </div>
      </div>

      {/* Growth Indicator */}
      {usage_trends.growth_rate_percent !== 0 && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow flex items-center">
          <ArrowTrendingUpIcon className={`w-6 h-6 mr-3 ${
            usage_trends.growth_rate_percent > 0 ? 'text-green-500' : 'text-red-500'
          }`} />
          <div>
            <span className={`text-lg font-semibold ${
              usage_trends.growth_rate_percent > 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {usage_trends.growth_rate_percent > 0 ? '+' : ''}
              {usage_trends.growth_rate_percent.toFixed(1)}%
            </span>
            <span className="text-gray-500 ml-2">
              message volume change vs previous period
            </span>
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Popular Topics */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Popular Topics</h3>
          {popular_topics.length > 0 ? (
            <div className="space-y-3">
              {popular_topics.slice(0, 5).map((topic, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="font-medium">{topic.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full"
                        style={{ width: `${topic.percentage}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-500 w-12 text-right">
                      {topic.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No topics data yet</p>
          )}
        </div>

        {/* Category Usage */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Category Usage</h3>
          {user_analytics.favorite_categories.length > 0 ? (
            <div className="space-y-3">
              {user_analytics.favorite_categories.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="font-medium">{category.name}</span>
                  <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                    {category.count} conversations
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No categories used yet</p>
          )}
        </div>
      </div>

      {/* Daily Activity Chart */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Daily Activity</h3>
        <div className="h-64 flex items-end space-x-1">
          {usage_trends.daily_messages.slice(-30).map((day, index) => {
            const maxCount = Math.max(...usage_trends.daily_messages.map(d => d.count), 1);
            const height = (day.count / maxCount) * 100;
            
            return (
              <div
                key={index}
                className="flex-1 bg-primary/20 hover:bg-primary/40 transition-colors rounded-t"
                style={{ height: `${height}%` }}
                title={`${day.date}: ${day.count} messages`}
              >
                <div 
                  className="w-full bg-primary rounded-t"
                  style={{ height: '100%' }}
                />
              </div>
            );
          })}
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Last 30 days message activity
        </div>
      </div>
    </div>
  );
}