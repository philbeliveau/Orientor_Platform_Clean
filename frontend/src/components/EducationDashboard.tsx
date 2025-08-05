import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ProgramCard } from './ProgramCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  GraduationCap, 
  Brain, 
  Target, 
  Sparkles, 
  Search,
  BookOpen,
  TrendingUp,
  Users
} from 'lucide-react';

interface EducationDashboardProps {
  className?: string;
}

// Mock data - in production, this would come from your API
const mockHollandProfile = {
  top_3_code: 'IRA',
  scores: {
    I: 8.2, // Investigative
    R: 7.5, // Realistic  
    A: 5.1, // Artistic
    S: 6.3, // Social
    E: 4.8, // Enterprising
    C: 5.9  // Conventional
  },
  assessment_date: '2024-01-15T10:30:00Z'
};

const mockPersonalizedPrograms = [
  {
    id: 'prog-1',
    title: 'Computer Science Technology',
    title_fr: 'Techniques de l\'informatique',
    institution_name: 'Dawson College',
    institution_city: 'Montreal',
    program_type: 'technical',
    level: 'diploma',
    duration_months: 36,
    tuition_domestic: 1200,
    employment_rate: 0.89,
    holland_compatibility: {
      score: 0.85,
      codes: ['I', 'R']
    },
    career_alignment_score: 0.8,
    skill_match_score: 0.7,
    recommendation_reasons: [
      'Strong match with your Investigative personality',
      'High employment rate in technology sector',
      'Builds on your analytical thinking strengths'
    ]
  },
  {
    id: 'prog-2',
    title: 'Software Engineering',
    institution_name: 'McGill University',
    institution_city: 'Montreal',
    program_type: 'academic',
    level: 'bachelor',
    duration_months: 48,
    tuition_domestic: 3500,
    employment_rate: 0.92,
    holland_compatibility: {
      score: 0.82,
      codes: ['I', 'R']
    },
    career_alignment_score: 0.9,
    skill_match_score: 0.8,
    recommendation_reasons: [
      'Perfect match for software development career',
      'Excellent employment prospects',
      'Matches your problem-solving skills'
    ]
  },
  {
    id: 'prog-3',
    title: 'Data Science',
    institution_name: 'Université de Montréal',
    institution_city: 'Montreal',
    program_type: 'academic',
    level: 'bachelor',
    duration_months: 48,
    tuition_domestic: 2800,
    employment_rate: 0.87,
    holland_compatibility: {
      score: 0.78,
      codes: ['I', 'A']
    },
    career_alignment_score: 0.7,
    skill_match_score: 0.85,
    recommendation_reasons: [
      'Great fit for analytical minds',
      'Growing field with high demand',
      'Combines math and technology'
    ]
  }
];

const mockCareerPathways = [
  {
    career_code: '2171',
    career_title: 'Software Developer',
    career_description: 'Design, develop and test software applications',
    recommended_programs: mockPersonalizedPrograms.slice(0, 2),
    pathway_strength: 0.85,
    timeline_years: 3
  },
  {
    career_code: '2172',
    career_title: 'Data Scientist',
    career_description: 'Analyze complex data to help organizations make decisions',
    recommended_programs: [mockPersonalizedPrograms[2]],
    pathway_strength: 0.78,
    timeline_years: 4
  }
];

export function EducationDashboard({ className = '' }: EducationDashboardProps) {
  const [personalizedPrograms, setPersonalizedPrograms] = useState(mockPersonalizedPrograms);
  const [careerPathways, setCareerPathways] = useState(mockCareerPathways);
  const [savedPrograms, setSavedPrograms] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSaveProgram = (programId: string) => {
    setSavedPrograms(prev => 
      prev.includes(programId) 
        ? prev.filter(id => id !== programId)
        : [...prev, programId]
    );
    // In production, this would make an API call
    console.log('Program saved:', programId);
  };

  const handleViewDetails = (programId: string) => {
    // In production, this would navigate to program details page
    console.log('View program details:', programId);
  };

  const getHollandCodeDescription = (code: string) => {
    const descriptions = {
      R: 'Realistic (hands-on, practical)',
      I: 'Investigative (analytical, scientific)',
      A: 'Artistic (creative, expressive)',
      S: 'Social (helping, teaching)',
      E: 'Enterprising (leadership, business)',
      C: 'Conventional (organized, detail-oriented)'
    };
    return descriptions[code as keyof typeof descriptions] || code;
  };

  return (
    <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <GraduationCap className="w-8 h-8 mr-3 text-blue-600" />
          Your Education Journey
        </h1>
        <p className="text-lg text-gray-600">
          Discover programs tailored to your personality and career goals
        </p>
      </motion.div>

      {/* Personality Profile Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mb-8"
      >
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Brain className="w-5 h-5 mr-2 text-blue-600" />
              Your Personality Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-3">
              {mockHollandProfile.top_3_code.split('').map((code) => (
                <Badge key={code} variant="default" className="bg-blue-600">
                  {getHollandCodeDescription(code)}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-gray-600">
              Programs below are specifically matched to your {mockHollandProfile.top_3_code} personality type,
              which indicates strong analytical and practical problem-solving abilities.
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Holland-Based Program Recommendations */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-12"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
            <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
            Programs Matching Your Personality
          </h2>
          <Button variant="outline" className="flex items-center">
            <Search className="w-4 h-4 mr-2" />
            Search All Programs
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {personalizedPrograms.map((program, index) => (
            <motion.div
              key={program.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <ProgramCard
                program={program}
                onSave={handleSaveProgram}
                onViewDetails={handleViewDetails}
              />
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Career-Education Pathways */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mb-12"
      >
        <div className="flex items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
            <Target className="w-6 h-6 mr-2 text-green-600" />
            Education Paths for Your Career Goals
          </h2>
        </div>
        
        <div className="space-y-6">
          {careerPathways.map((pathway, index) => (
            <motion.div
              key={pathway.career_code}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card className="border-l-4 border-l-green-500">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                      {pathway.career_title}
                    </CardTitle>
                    <Badge variant="success">
                      {Math.round(pathway.pathway_strength * 100)}% Match
                    </Badge>
                  </div>
                  <p className="text-gray-600">{pathway.career_description}</p>
                  <div className="flex items-center text-sm text-gray-500 mt-2">
                    <BookOpen className="w-4 h-4 mr-1" />
                    <span>Estimated timeline: {pathway.timeline_years} years</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <h4 className="font-medium text-gray-900 mb-3">Recommended Programs:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {pathway.recommended_programs.map((program) => (
                      <div key={program.id} className="border rounded-lg p-4 bg-gray-50">
                        <h5 className="font-medium text-gray-900 mb-1">{program.title}</h5>
                        <p className="text-sm text-gray-600 mb-2">{program.institution_name}</p>
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="text-xs">
                            {program.level}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {program.duration_months && `${Math.floor(program.duration_months / 12)} years`}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Quick Stats */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="mb-8"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{personalizedPrograms.length}</h3>
              <p className="text-sm text-gray-600">Personalized Matches</p>
            </CardContent>
          </Card>
          
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{careerPathways.length}</h3>
              <p className="text-sm text-gray-600">Career Pathways</p>
            </CardContent>
          </Card>
          
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BookOpen className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">{savedPrograms.length}</h3>
              <p className="text-sm text-gray-600">Saved Programs</p>
            </CardContent>
          </Card>
        </div>
      </motion.section>
    </div>
  );
}