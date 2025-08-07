'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import TimelineVisualization, { SkillNode, TimelineTier } from '@/components/career/TimelineVisualization';
import SkillRelationshipGraph from '@/components/career/SkillRelationshipGraph';
// import { motion } from 'framer-motion'; // Removed for build compatibility
import { toast } from 'react-hot-toast';
import { useClerkApi } from '@/services/api';
import { useRouter } from 'next/navigation';

// CareerGoal type definition (from the service)
export interface CareerGoal {
  id: number;
  user_id: number;
  esco_occupation_id?: string;
  oasis_code?: string;
  title: string;
  description?: string;
  target_date: string;
  is_active: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  achieved_at?: string;
  source?: string;
  milestones_count?: number;
  completed_milestones?: number;
}

// Mock data generator with GraphSage-style scoring
const generateMockCareerData = (): TimelineTier[] => {
  return [
    {
      id: 'tier-1',
      title: 'Foundation & Exploration',
      level: 1,
      timeline_months: 6,
      confidence_threshold: 0.8,
      skills: [
        {
          id: 'skill-1-1',
          label: 'Programming Fundamentals',
          confidence_score: 0.92,
          type: 'skill',
          level: 1,
          relationships: ['skill-1-2', 'skill-2-1'],
          metadata: {
            description: 'Learn core programming concepts and syntax',
            estimated_months: 3,
            prerequisites: [],
            learning_resources: ['Online courses', 'Practice projects']
          }
        },
        {
          id: 'skill-1-2',
          label: 'Problem Solving',
          confidence_score: 0.85,
          type: 'skill',
          level: 1,
          relationships: ['skill-1-1', 'skill-2-3'],
          metadata: {
            description: 'Develop analytical thinking and debugging skills',
            estimated_months: 2,
            prerequisites: [],
            learning_resources: ['Algorithm challenges', 'Code reviews']
          }
        },
        {
          id: 'skill-1-3',
          label: 'Version Control',
          confidence_score: 0.78,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-1', 'skill-2-2'],
          metadata: {
            description: 'Master Git and collaborative development workflows',
            estimated_months: 1,
            prerequisites: ['skill-1-1'],
            learning_resources: ['Git tutorials', 'GitHub projects']
          }
        },
        {
          id: 'skill-1-4',
          label: 'Web Technologies',
          confidence_score: 0.65,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-1', 'skill-2-4'],
          metadata: {
            description: 'Understanding of HTML, CSS, and JavaScript basics',
            estimated_months: 4,
            prerequisites: [],
            learning_resources: ['MDN docs', 'Frontend projects']
          }
        },
        {
          id: 'skill-1-5',
          label: 'Database Basics',
          confidence_score: 0.42,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-2', 'skill-3-2'],
          metadata: {
            description: 'SQL fundamentals and database design principles',
            estimated_months: 2,
            prerequisites: [],
            learning_resources: ['SQL tutorials', 'Database projects']
          }
        }
      ]
    },
    {
      id: 'tier-2',
      title: 'Skill Development',
      level: 2,
      timeline_months: 12,
      confidence_threshold: 0.7,
      skills: [
        {
          id: 'skill-2-1',
          label: 'Frontend Frameworks',
          confidence_score: 0.89,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-1', 'skill-1-4', 'skill-3-1'],
          metadata: {
            description: 'React, Vue, or Angular framework proficiency',
            estimated_months: 6,
            prerequisites: ['skill-1-1', 'skill-1-4'],
            learning_resources: ['Framework docs', 'Component libraries']
          }
        },
        {
          id: 'skill-2-2',
          label: 'Backend Development',
          confidence_score: 0.73,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-1', 'skill-1-5', 'skill-3-2'],
          metadata: {
            description: 'Server-side programming and API development',
            estimated_months: 8,
            prerequisites: ['skill-1-1', 'skill-1-5'],
            learning_resources: ['Node.js', 'Python', 'API design']
          }
        },
        {
          id: 'skill-2-3',
          label: 'Testing & QA',
          confidence_score: 0.61,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-2', 'skill-3-1', 'skill-3-3'],
          metadata: {
            description: 'Unit testing, integration testing, and QA practices',
            estimated_months: 4,
            prerequisites: ['skill-1-1', 'skill-1-2'],
            learning_resources: ['Testing frameworks', 'TDD practices']
          }
        },
        {
          id: 'skill-2-4',
          label: 'UI/UX Design',
          confidence_score: 0.55,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-4', 'skill-3-1'],
          metadata: {
            description: 'User interface design and user experience principles',
            estimated_months: 5,
            prerequisites: ['skill-1-4'],
            learning_resources: ['Design tools', 'UX research']
          }
        },
        {
          id: 'skill-2-5',
          label: 'DevOps Basics',
          confidence_score: 0.38,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-3', 'skill-3-3'],
          metadata: {
            description: 'CI/CD, containerization, and deployment strategies',
            estimated_months: 6,
            prerequisites: ['skill-1-3'],
            learning_resources: ['Docker', 'CI/CD tools', 'Cloud platforms']
          }
        }
      ]
    },
    {
      id: 'tier-3',
      title: 'Specialization & Leadership',
      level: 3,
      timeline_months: 18,
      confidence_threshold: 0.6,
      skills: [
        {
          id: 'skill-3-1',
          label: 'Full-Stack Architecture',
          confidence_score: 0.81,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-1', 'skill-2-2', 'skill-4-1'],
          metadata: {
            description: 'End-to-end application architecture and design patterns',
            estimated_months: 10,
            prerequisites: ['skill-2-1', 'skill-2-2'],
            learning_resources: ['System design', 'Architecture patterns']
          }
        },
        {
          id: 'skill-3-2',
          label: 'Database Optimization',
          confidence_score: 0.67,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Advanced database design, indexing, and performance tuning',
            estimated_months: 8,
            prerequisites: ['skill-1-5', 'skill-2-2'],
            learning_resources: ['Database internals', 'Performance analysis']
          }
        },
        {
          id: 'skill-3-3',
          label: 'Team Leadership',
          confidence_score: 0.52,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-3', 'skill-4-1', 'skill-4-3'],
          metadata: {
            description: 'Technical leadership, mentoring, and project management',
            estimated_months: 12,
            prerequisites: ['skill-2-3'],
            learning_resources: ['Leadership training', 'Agile methodologies']
          }
        },
        {
          id: 'skill-3-4',
          label: 'Security & Privacy',
          confidence_score: 0.44,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Application security, data privacy, and compliance',
            estimated_months: 6,
            prerequisites: ['skill-2-2'],
            learning_resources: ['Security frameworks', 'Compliance standards']
          }
        },
        {
          id: 'skill-3-5',
          label: 'Performance Optimization',
          confidence_score: 0.39,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-1', 'skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Application performance analysis and optimization techniques',
            estimated_months: 8,
            prerequisites: ['skill-2-1', 'skill-2-2'],
            learning_resources: ['Profiling tools', 'Optimization patterns']
          }
        }
      ]
    },
    {
      id: 'tier-4',
      title: 'Mastery & Innovation',
      level: 4,
      timeline_months: 24,
      confidence_threshold: 0.5,
      skills: [
        {
          id: 'skill-4-1',
          label: 'Technical Strategy',
          confidence_score: 0.72,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-3'],
          metadata: {
            description: 'Technology roadmapping, technical vision, and strategic planning',
            estimated_months: 15,
            prerequisites: ['skill-3-1', 'skill-3-3'],
            learning_resources: ['Strategy frameworks', 'Technology trends']
          }
        },
        {
          id: 'skill-4-2',
          label: 'System Scalability',
          confidence_score: 0.58,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-2', 'skill-3-5'],
          metadata: {
            description: 'Large-scale system design and scalability engineering',
            estimated_months: 18,
            prerequisites: ['skill-3-1', 'skill-3-2'],
            learning_resources: ['Distributed systems', 'Scalability patterns']
          }
        },
        {
          id: 'skill-4-3',
          label: 'Innovation Leadership',
          confidence_score: 0.45,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-3'],
          metadata: {
            description: 'Leading innovation initiatives and emerging technology adoption',
            estimated_months: 20,
            prerequisites: ['skill-3-3'],
            learning_resources: ['Innovation frameworks', 'Emerging technologies']
          }
        },
        {
          id: 'skill-4-4',
          label: 'Cross-Domain Expertise',
          confidence_score: 0.33,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-4'],
          metadata: {
            description: 'Expertise spanning multiple technology domains and business areas',
            estimated_months: 24,
            prerequisites: ['skill-3-1'],
            learning_resources: ['Domain knowledge', 'Business understanding']
          }
        }
      ]
    }
  ];
};

const GoalsPage: React.FC = () => {
  const [careerData, setCareerData] = useState<TimelineTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<SkillNode | null>(null);
  const [activeView, setActiveView] = useState<'timeline' | 'graph'>('timeline');
  const [activeGoal, setActiveGoal] = useState<CareerGoal | null>(null);
  const [milestones, setMilestones] = useState<any[]>([]);
  const router = useRouter();
  const api = useClerkApi();

  useEffect(() => {
    loadActiveGoalAndProgression();
  }, []);

  const loadActiveGoalAndProgression = async () => {
    setLoading(true);
    
    try {
      // Fetch active career goal using useClerkApi pattern
      const response = await api.request<{
        goal: CareerGoal | null;
        progression: any;
        milestones: any[];
      }>('/api/v1/career-goals/active', {
        method: 'GET'
      });
      const { goal, progression, milestones: goalMilestones } = response;
      
      if (goal) {
        setActiveGoal(goal);
        setMilestones(goalMilestones || []);
        
        // Convert progression to timeline format if available
        if (progression && progression.tiers) {
          const timelineData = convertProgressionToTimeline(progression.tiers);
          setCareerData(timelineData);
          toast.success(`Loaded progression for: ${goal.title}`);
        } else {
          // Use mock data if no progression available
          const mockData = generateMockCareerData();
          setCareerData(mockData);
        }
      } else {
        // No active goal - use mock data
        const mockData = generateMockCareerData();
        setCareerData(mockData);
      }
    } catch (error) {
      console.error('Error loading career goal:', error);
      toast.error('Failed to load career progression');
      // Fallback to mock data
      const mockData = generateMockCareerData();
      setCareerData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const convertProgressionToTimeline = (tiers: any[]): TimelineTier[] => {
    return tiers.map((tier, index) => ({
      id: `tier-${tier.tier_number || index + 1}`,
      title: tier.title || `Tier ${tier.tier_number || index + 1}`,
      level: tier.tier_number || index + 1,
      timeline_months: tier.timeline_months || 6 * (index + 1),
      confidence_threshold: tier.confidence_threshold || 0.8 - (index * 0.1),
      skills: (tier.skills || []).map((skill: any) => ({
        id: skill.id,
        label: skill.label,
        confidence_score: skill.graphsage_score || skill.confidence_score || 0.5,
        type: 'skill',
        level: tier.tier_number || index + 1,
        relationships: skill.relationships || [],
        metadata: {
          description: skill.description || '',
          estimated_months: skill.estimated_months || 3,
          prerequisites: skill.prerequisites || [],
          learning_resources: skill.learning_resources || []
        }
      }))
    }));
  };

  const handleSkillClick = (skill: SkillNode) => {
    setSelectedSkill(skill);
    toast(`Selected: ${skill.label}`, {
      icon: '🎯',
      duration: 2000,
    });
  };

  const handleSetCareerGoal = (skill: SkillNode) => {
    toast.success(`Set "${skill.label}" as career goal!`);
    // TODO: Implement actual career goal setting API
  };

  const totalSkills = careerData.reduce((sum, tier) => sum + tier.skills.length, 0);
  const highConfidenceSkills = careerData.reduce(
    (sum, tier) => sum + tier.skills.filter(s => s.confidence_score >= tier.confidence_threshold).length,
    0
  );

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your career progression...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Active Goal Header */}
        {activeGoal ? (
          <div className="mb-8 animate-in slide-in-from-top duration-300">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-blue-900">
                    Current Goal: {activeGoal.title}
                  </h2>
                  <p className="text-blue-700 mt-1">
                    Target: {new Date(activeGoal.target_date).toLocaleDateString()}
                  </p>
                  {activeGoal.description && (
                    <p className="text-gray-600 mt-2">{activeGoal.description}</p>
                  )}
                  <div className="flex items-center mt-3 space-x-4">
                    <div className="text-sm">
                      <span className="text-gray-500">Progress:</span>
                      <span className="font-semibold text-blue-900 ml-1">
                        {Math.round(activeGoal.progress_percentage)}%
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Milestones:</span>
                      <span className="font-semibold text-blue-900 ml-1">
                        {activeGoal.completed_milestones || 0} / {activeGoal.milestones_count || 0}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => router.push('/find-your-way')}
                    className="px-4 py-2 bg-white text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    Change Goal
                  </button>
                  <button
                    onClick={() => router.push('/saved')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Saved Jobs
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-8 animate-in slide-in-from-top duration-300">
            <div className="bg-gray-50 rounded-xl p-8 border border-gray-200 text-center">
              <h2 className="text-xl font-semibold text-gray-700 mb-2">
                No Career Goal Set
              </h2>
              <p className="text-gray-600 mb-6">
                Set a career goal from any job card to see your personalized progression timeline
              </p>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => router.push('/find-your-way')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Explore Careers
                </button>
                <button
                  onClick={() => router.push('/saved')}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  View Saved Jobs
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Section Header */}
        <div className="mb-8 animate-in slide-in-from-top duration-300">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {activeGoal ? 'Career Progression Timeline' : 'Career Goals'}
              </h1>
              <p className="text-gray-600 mt-2">
                Track your progression with GraphSage-powered confidence scoring
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="bg-gray-100 rounded-lg p-1 flex">
                <button
                  onClick={() => setActiveView('timeline')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'timeline'
                      ? 'bg-white text-gray-900 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Timeline View
                </button>
                <button
                  onClick={() => setActiveView('graph')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'graph'
                      ? 'bg-white text-gray-900 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Graph View
                </button>
              </div>
              
              {/* Stats */}
              <div className="text-right">
                <div className="text-sm text-gray-600">Progress Overview</div>
                <div className="text-lg font-semibold text-gray-900">
                  {highConfidenceSkills} / {totalSkills} skills ready
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        {activeView === 'timeline' ? (
          <div className="animate-in slide-in-from-left duration-300">
            <TimelineVisualization
              tiers={careerData}
              onSkillClick={handleSkillClick}
              className="mb-8"
            />
          </div>
        ) : (
          <div className="animate-in slide-in-from-right duration-300">
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-900">Skill Relationship Graph</h3>
                <p className="text-gray-600 mb-4">
                  Interactive visualization of skill connections and GraphSage confidence scores
                </p>
                
                <SkillRelationshipGraph
                  skills={careerData.flatMap(tier => tier.skills)}
                  onSkillClick={handleSkillClick}
                  highlightedSkills={selectedSkill ? new Set([selectedSkill.id, ...(selectedSkill.relationships || [])]) : new Set()}
                  className="h-96"
                />
              </div>
              
              {/* Graph Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Skills</div>
                  <div className="text-2xl font-bold text-gray-900">{totalSkills}</div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">High Confidence</div>
                  <div className="text-2xl font-bold text-green-600">{highConfidenceSkills}</div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Skill Connections</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {careerData.reduce((sum, tier) => 
                      sum + tier.skills.reduce((skillSum, skill) => 
                        skillSum + (skill.relationships?.length || 0), 0
                      ), 0
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Panel */}
        {selectedSkill && (
          <div className="fixed bottom-4 right-4 bg-white rounded-xl shadow-lg border border-gray-200 p-6 max-w-sm animate-in slide-in-from-bottom duration-200">
            <h3 className="font-semibold text-gray-900 mb-2">Selected Skill</h3>
            <p className="text-gray-600 mb-4">{selectedSkill.label}</p>
            
            <div className="flex space-x-2">
              <button
                onClick={() => handleSetCareerGoal(selectedSkill)}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Set as Goal
              </button>
              <button
                onClick={() => setSelectedSkill(null)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default GoalsPage;