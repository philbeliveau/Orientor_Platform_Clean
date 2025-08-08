'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Send, Brain, Lightbulb, TrendingUp, MessageCircle, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { getAuthHeader, endpoint } from '@/services/api';

interface Question {
  id: string;
  question: string;
  intent: string;
  follow_up_triggers: string[];
}

interface Insight {
  type: string;
  value: any;
  confidence: number;
  evidence: string;
}

interface CareerSignal {
  type: string;
  strength: number;
  evidence: string;
  metadata?: any;
}

interface AnalysisResponse {
  insights: Insight[];
  career_signals: CareerSignal[];
  sentiment: {
    engagement_level: number;
    authenticity: number;
    emotional_indicators: string[];
  };
  next_questions: Question[];
  session_complete: boolean;
  career_implications: {
    immediate_insights: string[];
    esco_connections: string[];
    recommended_exploration: string[];
  };
}

interface ConversationMessage {
  id: string;
  type: 'question' | 'response' | 'insight' | 'system';
  content: string;
  timestamp: Date;
  metadata?: any;
}

interface CareerAnalysisChatProps {
  courseId: number;
  courseName: string;
  onInsightsDiscovered?: (insights: Insight[]) => void;
  onSessionComplete?: (summary: any) => void;
}

const CareerAnalysisChat: React.FC<CareerAnalysisChatProps> = ({
  courseId,
  courseName,
  onInsightsDiscovered,
  onSessionComplete
}) => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [userResponse, setUserResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [discoveredInsights, setDiscoveredInsights] = useState<Insight[]>([]);
  const [careerSignals, setCareerSignals] = useState<CareerSignal[]>([]);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (sessionStarted && !sessionId) {
      startAnalysisSession();
    }
  }, [sessionStarted, sessionId]);

  const startAnalysisSession = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint(`/courses/${courseId}/targeted-analysis/`), {
        method: 'POST',
        headers,
        body: JSON.stringify({
          focus_areas: ['career_preferences', 'authentic_interests', 'work_style']
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      
      // Add welcome message
      const welcomeMessage: ConversationMessage = {
        id: 'welcome',
        type: 'system',
        content: `Let's explore your career preferences through your experience in ${courseName}. I'll ask you a few thoughtful questions to help discover your authentic interests and work style preferences.`,
        timestamp: new Date()
      };
      
      setMessages([welcomeMessage]);
      
      // Set first question
      if (data.next_questions && data.next_questions.length > 0) {
        const firstQuestion = data.next_questions[0];
        setCurrentQuestion(firstQuestion);
        
        const questionMessage: ConversationMessage = {
          id: firstQuestion.id,
          type: 'question',
          content: firstQuestion.question,
          timestamp: new Date(),
          metadata: { intent: firstQuestion.intent }
        };
        
        setMessages(prev => [...prev, questionMessage]);
      }
      
    } catch (err) {
      console.error('Error starting analysis session:', err);
      setError('Failed to start career analysis. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResponseSubmit = async () => {
    if (!userResponse.trim() || !currentQuestion || !sessionId) return;

    try {
      setIsLoading(true);
      setError(null);
      
      // Add user response to messages
      const responseMessage: ConversationMessage = {
        id: `response_${Date.now()}`,
        type: 'response',
        content: userResponse,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, responseMessage]);
      
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint(`/conversations/${sessionId}/respond`), {
        method: 'POST',
        headers,
        body: JSON.stringify({
          question_id: currentQuestion.id,
          response: userResponse
        })
      });

      if (!response.ok) {
        throw new Error('Failed to process response');
      }

      const analysisResult: AnalysisResponse = await response.json();
      
      // Process discovered insights
      if (analysisResult.insights && analysisResult.insights.length > 0) {
        const newInsights = analysisResult.insights;
        setDiscoveredInsights(prev => [...prev, ...newInsights]);
        
        // Add insight message
        const insightMessage: ConversationMessage = {
          id: `insight_${Date.now()}`,
          type: 'insight',
          content: `💡 Insight discovered: ${formatInsights(newInsights)}`,
          timestamp: new Date(),
          metadata: { insights: newInsights }
        };
        
        setMessages(prev => [...prev, insightMessage]);
        
        if (onInsightsDiscovered) {
          onInsightsDiscovered(newInsights);
        }
      }
      
      // Process career signals
      if (analysisResult.career_signals) {
        setCareerSignals(prev => [...prev, ...analysisResult.career_signals]);
      }
      
      // Handle next question or session completion
      if (analysisResult.session_complete) {
        setSessionComplete(true);
        setCurrentQuestion(null);
        
        const completionMessage: ConversationMessage = {
          id: 'completion',
          type: 'system',
          content: `🎉 Analysis complete! I've discovered ${discoveredInsights.length + (analysisResult.insights?.length || 0)} insights about your career preferences. You can view the full summary and recommendations below.`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, completionMessage]);
        
        if (onSessionComplete) {
          const summary = await generateSessionSummary();
          onSessionComplete(summary);
        }
        
      } else if (analysisResult.next_questions && analysisResult.next_questions.length > 0) {
        const nextQuestion = analysisResult.next_questions[0];
        setCurrentQuestion(nextQuestion);
        
        const questionMessage: ConversationMessage = {
          id: nextQuestion.id,
          type: 'question',
          content: nextQuestion.question,
          timestamp: new Date(),
          metadata: { intent: nextQuestion.intent }
        };
        
        setMessages(prev => [...prev, questionMessage]);
      }
      
      setUserResponse('');
      
    } catch (err) {
      console.error('Error processing response:', err);
      setError('Failed to process your response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const generateSessionSummary = async () => {
    if (!sessionId) return null;
    
    try {
      const headers = await getAuthHeader(getToken);
      const response = await fetch(endpoint(`/conversations/${sessionId}/summary`), {
        headers
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      console.error('Error generating summary:', err);
    }
    
    return null;
  };

  const formatInsights = (insights: Insight[]): string => {
    return insights.map(insight => {
      switch (insight.type) {
        case 'cognitive_preference':
          return `You show a preference for ${JSON.stringify(insight.value)} thinking patterns`;
        case 'work_style':
          return `Your work style indicates ${JSON.stringify(insight.value)} preferences`;
        case 'subject_affinity':
          return `You demonstrate authentic interest in ${JSON.stringify(insight.value)}`;
        default:
          return `${insight.type}: ${JSON.stringify(insight.value)}`;
      }
    }).join(', ');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleResponseSubmit();
    }
  };

  const getIntentIcon = (intent: string) => {
    switch (intent) {
      case 'cognitive_preference':
        return <Brain className="w-4 h-4" />;
      case 'work_style':
        return <TrendingUp className="w-4 h-4" />;
      case 'subject_affinity':
        return <Lightbulb className="w-4 h-4" />;
      default:
        return <MessageCircle className="w-4 h-4" />;
    }
  };

  if (!sessionStarted) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl">
        <Brain className="w-16 h-16 text-blue-600 mb-4" />
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Discover Your Career Preferences
        </h3>
        <p className="text-gray-600 text-center mb-6 max-w-md">
          I'll guide you through a personalized conversation about your experience in {courseName} 
          to uncover insights about your authentic career interests and work style preferences.
        </p>
        <button
          onClick={() => setSessionStarted(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <MessageCircle className="w-5 h-5" />
          Start Career Analysis
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6" />
            <div>
              <h3 className="font-semibold">Career Analysis Session</h3>
              <p className="text-blue-100 text-sm">{courseName}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-blue-100">
              {discoveredInsights.length} insights discovered
            </div>
            {sessionComplete && (
              <CheckCircle className="w-5 h-5 text-green-300" />
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'response' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'response'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'insight'
                  ? 'bg-green-100 text-green-800 border border-green-200'
                  : message.type === 'system'
                  ? 'bg-gray-100 text-gray-700'
                  : 'bg-gray-50 text-gray-800'
              }`}
            >
              {message.type === 'question' && message.metadata?.intent && (
                <div className="flex items-center gap-2 mb-2 text-sm opacity-70">
                  {getIntentIcon(message.metadata.intent)}
                  <span className="capitalize">
                    {message.metadata.intent.replace('_', ' ')}
                  </span>
                </div>
              )}
              <p className="whitespace-pre-wrap">{message.content}</p>
              <div className="text-xs opacity-60 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-gray-600">Analyzing your response...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Input Area */}
      {currentQuestion && !sessionComplete && (
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <textarea
              ref={textareaRef}
              value={userResponse}
              onChange={(e) => setUserResponse(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Share your thoughts and experiences..."
              className="flex-1 resize-none border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              disabled={isLoading}
            />
            <button
              onClick={handleResponseSubmit}
              disabled={!userResponse.trim() || isLoading}
              className="self-end bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-3 rounded-lg transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Session Complete Actions */}
      {sessionComplete && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Analysis complete! Review your insights and career recommendations.
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => window.location.href = `/classes/${courseId}/insights`}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                View Full Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerAnalysisChat;
