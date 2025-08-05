import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SkillTreeMessage } from '../SkillTreeMessage';
import { ComponentAction } from '../../chat/MessageComponent';

// Mock SaveActionButton
jest.mock('../../chat/SaveActionButton', () => ({
  SaveActionButton: ({ onSave, saved }: any) => (
    <button onClick={onSave} disabled={saved}>
      {saved ? 'Saved' : 'Save'}
    </button>
  )
}));

describe('SkillTreeMessage', () => {
  const mockOnAction = jest.fn();

  const mockData = {
    job_title: 'Software Engineer',
    skills: [
      {
        id: '1',
        name: 'Programming',
        description: 'Core programming skills',
        proficiency_level: 'Expert',
        importance: 'required' as const,
        children: [
          {
            id: '1.1',
            name: 'JavaScript',
            proficiency_level: 'Advanced'
          },
          {
            id: '1.2',
            name: 'Python',
            proficiency_level: 'Intermediate'
          }
        ]
      },
      {
        id: '2',
        name: 'Database Management',
        importance: 'preferred' as const
      },
      {
        id: '3',
        name: 'Cloud Computing',
        importance: 'optional' as const
      },
      {
        id: '4',
        name: 'Testing'
      },
      {
        id: '5',
        name: 'DevOps'
      },
      {
        id: '6',
        name: 'Security'
      }
    ],
    total_skills: 15,
    source: 'ESCO Database'
  };

  const mockActions: ComponentAction[] = [
    { type: 'save', label: 'Save Skills' },
    { type: 'explore', label: 'Explore Skills' }
  ];

  beforeEach(() => {
    mockOnAction.mockClear();
  });

  test('renders job title and skill count', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Skills for Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('15 skills identified')).toBeInTheDocument();
  });

  test('renders skill nodes with correct styling', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Programming')).toBeInTheDocument();
    expect(screen.getByText('Expert')).toBeInTheDocument();
    expect(screen.getByText('required')).toBeInTheDocument();
    expect(screen.getByText('preferred')).toBeInTheDocument();
    expect(screen.getByText('optional')).toBeInTheDocument();
  });

  test('expands and collapses skill nodes', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    // Initially expanded (level 0)
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
    
    // Click to collapse
    const programmingNode = screen.getByText('Programming').closest('div');
    fireEvent.click(programmingNode!);
    
    expect(screen.queryByText('JavaScript')).not.toBeInTheDocument();
    expect(screen.queryByText('Python')).not.toBeInTheDocument();
    
    // Click to expand again
    fireEvent.click(programmingNode!);
    
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  test('shows only first 5 skills initially', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Programming')).toBeInTheDocument();
    expect(screen.getByText('Database Management')).toBeInTheDocument();
    expect(screen.getByText('Cloud Computing')).toBeInTheDocument();
    expect(screen.getByText('Testing')).toBeInTheDocument();
    expect(screen.getByText('DevOps')).toBeInTheDocument();
    expect(screen.queryByText('Security')).not.toBeInTheDocument();
    
    expect(screen.getByText('Show 1 more skills')).toBeInTheDocument();
  });

  test('shows all skills when "Show more" is clicked', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    fireEvent.click(screen.getByText('Show 1 more skills'));
    
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.queryByText('Show 1 more skills')).not.toBeInTheDocument();
  });

  test('calls onAction for save action', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    fireEvent.click(screen.getByText('Save'));
    
    expect(mockOnAction).toHaveBeenCalledWith(mockActions[0]);
  });

  test('renders non-save action buttons', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    const exploreButton = screen.getByText('Explore Skills');
    expect(exploreButton).toBeInTheDocument();
    
    fireEvent.click(exploreButton);
    expect(mockOnAction).toHaveBeenCalledWith(mockActions[1]);
  });

  test('shows saved state', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
        saved={true}
      />
    );
    
    expect(screen.getByText('Saved')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Saved' })).toBeDisabled();
  });

  test('displays source information', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Source: ESCO Database')).toBeInTheDocument();
  });

  test('renders skill descriptions when available', () => {
    render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Core programming skills')).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const { container } = render(
      <SkillTreeMessage 
        data={mockData} 
        actions={mockActions} 
        onAction={mockOnAction} 
        className="custom-class"
      />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  test('handles empty skills array gracefully', () => {
    const emptyData = {
      ...mockData,
      skills: []
    };
    
    render(
      <SkillTreeMessage 
        data={emptyData} 
        actions={mockActions} 
        onAction={mockOnAction} 
      />
    );
    
    expect(screen.getByText('Skills for Software Engineer')).toBeInTheDocument();
  });
});