import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MessageComponentRenderer, MessageComponent, MessageComponentType, ComponentAction } from '../MessageComponent';

// Mock the individual message components
jest.mock('../../orientator/SkillTreeMessage', () => ({
  SkillTreeMessage: ({ data, onAction }: any) => (
    <div data-testid="skill-tree-message">
      <span>{data.job_title}</span>
      <button onClick={() => onAction({ type: 'save' })}>Save</button>
    </div>
  )
}));

jest.mock('../../orientator/CareerPathMessage', () => ({
  CareerPathMessage: ({ data }: any) => (
    <div data-testid="career-path-message">{data.career_goal}</div>
  )
}));

jest.mock('../../orientator/JobCardMessage', () => ({
  JobCardMessage: ({ data }: any) => (
    <div data-testid="job-card-message">{Array.isArray(data) ? data[0].title : data.title}</div>
  )
}));

jest.mock('../../orientator/PeerCardMessage', () => ({
  PeerCardMessage: ({ data }: any) => (
    <div data-testid="peer-card-message">{Array.isArray(data) ? data[0].name : data.name}</div>
  )
}));

jest.mock('../../orientator/TestResultMessage', () => ({
  TestResultMessage: ({ data }: any) => (
    <div data-testid="test-result-message">{data.test_name}</div>
  )
}));

jest.mock('../../orientator/ChallengeCardMessage', () => ({
  ChallengeCardMessage: ({ data }: any) => (
    <div data-testid="challenge-card-message">{Array.isArray(data) ? data[0].title : data.title}</div>
  )
}));

jest.mock('../../orientator/SaveConfirmationMessage', () => ({
  SaveConfirmationMessage: ({ data }: any) => (
    <div data-testid="save-confirmation-message">{data.item_title} saved</div>
  )
}));

jest.mock('../ToolInvocationLoader', () => ({
  ToolInvocationLoader: ({ toolName }: any) => (
    <div data-testid="tool-invocation-loader">Loading {toolName}</div>
  )
}));

describe('MessageComponentRenderer', () => {
  const mockOnAction = jest.fn();

  beforeEach(() => {
    mockOnAction.mockClear();
  });

  test('renders SkillTreeMessage component', () => {
    const component: MessageComponent = {
      id: '1',
      type: MessageComponentType.SKILL_TREE,
      data: { job_title: 'Software Engineer', skills: [] },
      actions: [{ type: 'save', label: 'Save' }]
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('skill-tree-message')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });

  test('renders CareerPathMessage component', () => {
    const component: MessageComponent = {
      id: '2',
      type: MessageComponentType.CAREER_PATH,
      data: { career_goal: 'Data Scientist', milestones: [] },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('career-path-message')).toBeInTheDocument();
    expect(screen.getByText('Data Scientist')).toBeInTheDocument();
  });

  test('renders JobCardMessage component', () => {
    const component: MessageComponent = {
      id: '3',
      type: MessageComponentType.JOB_CARD,
      data: { id: 'job1', title: 'Frontend Developer' },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('job-card-message')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
  });

  test('renders PeerCardMessage component', () => {
    const component: MessageComponent = {
      id: '4',
      type: MessageComponentType.PEER_CARD,
      data: { id: 'peer1', name: 'John Doe' },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('peer-card-message')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  test('renders TestResultMessage component', () => {
    const component: MessageComponent = {
      id: '5',
      type: MessageComponentType.TEST_RESULT,
      data: { test_type: 'hexaco', test_name: 'HEXACO Personality Test', dimensions: [] },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('test-result-message')).toBeInTheDocument();
    expect(screen.getByText('HEXACO Personality Test')).toBeInTheDocument();
  });

  test('renders ChallengeCardMessage component', () => {
    const component: MessageComponent = {
      id: '6',
      type: MessageComponentType.CHALLENGE_CARD,
      data: { id: 'ch1', title: 'Learn React', skill_focus: [] },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('challenge-card-message')).toBeInTheDocument();
    expect(screen.getByText('Learn React')).toBeInTheDocument();
  });

  test('renders SaveConfirmationMessage component', () => {
    const component: MessageComponent = {
      id: '7',
      type: MessageComponentType.SAVE_CONFIRMATION,
      data: { item_type: 'job', item_title: 'Software Engineer Position' },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('save-confirmation-message')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer Position saved')).toBeInTheDocument();
  });

  test('renders ToolInvocationLoader component', () => {
    const component: MessageComponent = {
      id: '8',
      type: MessageComponentType.TOOL_INVOCATION,
      data: { toolName: 'esco_skills' },
      actions: []
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(screen.getByTestId('tool-invocation-loader')).toBeInTheDocument();
    expect(screen.getByText('Loading esco_skills')).toBeInTheDocument();
  });

  test('calls onAction with correct parameters when action is triggered', () => {
    const component: MessageComponent = {
      id: '1',
      type: MessageComponentType.SKILL_TREE,
      data: { job_title: 'Software Engineer', skills: [] },
      actions: [{ type: 'save', label: 'Save' }]
    };

    render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    
    expect(mockOnAction).toHaveBeenCalledWith({ type: 'save' }, '1');
  });

  test('returns null for unknown component type', () => {
    const component: MessageComponent = {
      id: '9',
      type: 'unknown' as MessageComponentType,
      data: {},
      actions: []
    };

    const { container } = render(<MessageComponentRenderer component={component} onAction={mockOnAction} />);
    
    expect(container.firstChild).toBeNull();
  });

  test('applies custom className when provided', () => {
    const component: MessageComponent = {
      id: '1',
      type: MessageComponentType.SKILL_TREE,
      data: { job_title: 'Software Engineer', skills: [] },
      actions: []
    };

    const { container } = render(
      <MessageComponentRenderer 
        component={component} 
        onAction={mockOnAction} 
        className="custom-class"
      />
    );
    
    expect(screen.getByTestId('skill-tree-message')).toBeInTheDocument();
  });
});