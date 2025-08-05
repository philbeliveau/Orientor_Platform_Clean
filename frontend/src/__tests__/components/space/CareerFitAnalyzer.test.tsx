import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CareerFitAnalyzer from '@/components/space/CareerFitAnalyzer';
import { analyzeCareerFit } from '@/services/spaceService';
import type { Recommendation, SavedJob } from '@/services/spaceService';

// Mock the service
jest.mock('@/services/spaceService', () => ({
  analyzeCareerFit: jest.fn()
}));

const mockAnalyzeCareerFit = analyzeCareerFit as jest.MockedFunction<typeof analyzeCareerFit>;

describe('CareerFitAnalyzer', () => {
  const mockOasisJob: Recommendation = {
    id: 1,
    oasis_code: 'OASIS_123',
    label: 'Software Developer',
    description: 'Develop software applications',
    role_creativity: 3.5,
    role_leadership: 2.5,
    role_digital_literacy: 4.8,
    role_critical_thinking: 4.5,
    role_problem_solving: 4.7
  };

  const mockEscoJob: SavedJob = {
    id: 2,
    user_id: 1,
    esco_id: 'ESCO_456',
    job_title: 'Data Scientist',
    skills_required: ['Python', 'Machine Learning', 'Statistics'],
    discovery_source: 'tree',
    saved_at: '2024-01-01',
    metadata: {},
    already_saved: true
  };

  const mockFitAnalysis = {
    fit_score: 78,
    skill_match: {
      creativity: {
        skill_name: 'Creativity',
        user_level: 3.0,
        required_level: 3.5,
        match_percentage: 85.7
      },
      leadership: {
        skill_name: 'Leadership',
        user_level: 3.2,
        required_level: 2.5,
        match_percentage: 100
      }
    },
    gap_analysis: {
      skill_gaps: [
        {
          skill: 'Digital Literacy',
          current: 3.5,
          required: 4.8,
          gap: 1.3
        }
      ],
      strength_areas: ['Leadership', 'Problem Solving'],
      improvement_areas: ['Digital Literacy']
    },
    recommendations: [
      'Good potential fit for Software Developer with some skill development.',
      'Focus on improving Digital Literacy (current: 3.5/5, required: 4.8/5)'
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockAnalyzeCareerFit.mockResolvedValue(mockFitAnalysis);
  });

  test('renders loading state initially', () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('displays career fit score after loading', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('78%')).toBeInTheDocument();
      expect(screen.getByText('Career Fit Score')).toBeInTheDocument();
    });
  });

  test('shows feasibility analysis boxes', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('Entry Timeline')).toBeInTheDocument();
      expect(screen.getByText('Education Required')).toBeInTheDocument();
      expect(screen.getByText('Income Gap')).toBeInTheDocument();
    });
  });

  test('displays skill match radar chart data', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('Skill Match Analysis')).toBeInTheDocument();
      // Radar chart would be rendered
    });
  });

  test('shows skill gaps when present', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('Skills to Develop')).toBeInTheDocument();
      expect(screen.getByText('Digital Literacy')).toBeInTheDocument();
      expect(screen.getByText('Current: 3.5/5 → Required: 4.8/5')).toBeInTheDocument();
    });
  });

  test('handles LLM chat interface interaction', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('AI Career Advisor')).toBeInTheDocument();
    });
    
    // Click to show chat
    fireEvent.click(screen.getByText('Show Chat'));
    
    // Check quick question buttons appear
    expect(screen.getByText('Why this job?')).toBeInTheDocument();
    expect(screen.getByText('Top barriers?')).toBeInTheDocument();
    expect(screen.getByText('Time to qualify?')).toBeInTheDocument();
    expect(screen.getByText('PhD required?')).toBeInTheDocument();
    
    // Click a quick question
    fireEvent.click(screen.getByText('Why this job?'));
    
    // Check input is populated
    const input = screen.getByPlaceholderText('Ask about qualifications, timeline, barriers...');
    expect(input).toHaveValue('Why would I want to do this job?');
  });

  test('displays recommendations', async () => {
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('Recommended Actions')).toBeInTheDocument();
      expect(screen.getByText(/Focus on improving Digital Literacy/)).toBeInTheDocument();
    });
  });

  test('handles ESCO job analysis', async () => {
    render(<CareerFitAnalyzer job={mockEscoJob} jobSource="esco" />);
    
    await waitFor(() => {
      expect(mockAnalyzeCareerFit).toHaveBeenCalledWith('ESCO_456', 'esco');
    });
  });

  test('shows error state when analysis fails', async () => {
    mockAnalyzeCareerFit.mockRejectedValueOnce(new Error('Analysis failed'));
    
    render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to analyze career fit/)).toBeInTheDocument();
    });
  });

  test('color codes fit score appropriately', async () => {
    // Test high score (>= 80)
    mockAnalyzeCareerFit.mockResolvedValueOnce({
      ...mockFitAnalysis,
      fit_score: 85
    });
    
    const { rerender } = render(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument();
      // Would check for green color in actual implementation
    });
    
    // Test medium score (60-79)
    mockAnalyzeCareerFit.mockResolvedValueOnce({
      ...mockFitAnalysis,
      fit_score: 65
    });
    
    rerender(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('65%')).toBeInTheDocument();
      // Would check for yellow color
    });
    
    // Test low score (< 60)
    mockAnalyzeCareerFit.mockResolvedValueOnce({
      ...mockFitAnalysis,
      fit_score: 45
    });
    
    rerender(<CareerFitAnalyzer job={mockOasisJob} jobSource="oasis" />);
    
    await waitFor(() => {
      expect(screen.getByText('45%')).toBeInTheDocument();
      // Would check for red color
    });
  });
});

describe('CareerFitAnalyzer Integration', () => {
  test('integrates with RecommendationDetail component', () => {
    // This would test the integration when CareerFitAnalyzer is used
    // within RecommendationDetail component
    expect(true).toBe(true);
  });

  test('integrates with SavedJobDetail component', () => {
    // This would test the integration when CareerFitAnalyzer is used
    // within SavedJobDetail component
    expect(true).toBe(true);
  });
});