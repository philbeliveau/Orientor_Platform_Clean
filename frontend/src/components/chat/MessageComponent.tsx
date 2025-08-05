import React from 'react';
import { SkillTreeMessage } from '../orientator/SkillTreeMessage';
import { SkillTreeMessageEnhanced } from '../orientator/SkillTreeMessageEnhanced';
import { CareerPathMessage } from '../orientator/CareerPathMessage';
import { CareerPathMessageEnhanced } from '../orientator/CareerPathMessageEnhanced';
import { JobCardMessage } from '../orientator/JobCardMessage';
import { JobCardMessageEnhanced } from '../orientator/JobCardMessageEnhanced';
import { PeerCardMessage } from '../orientator/PeerCardMessage';
import { TestResultMessage } from '../orientator/TestResultMessage';
import { ChallengeCardMessage } from '../orientator/ChallengeCardMessage';
import { SaveConfirmationMessage } from '../orientator/SaveConfirmationMessage';
import { ToolInvocationLoader } from './ToolInvocationLoader';

export enum MessageComponentType {
  TEXT = "text",
  SKILL_TREE = "skill_tree",
  CAREER_PATH = "career_path",
  JOB_CARD = "job_card",
  PEER_CARD = "peer_card",
  TEST_RESULT = "test_result",
  CHALLENGE_CARD = "challenge_card",
  SAVE_CONFIRMATION = "save_confirmation",
  TOOL_INVOCATION = "tool_invocation"
}

export interface ComponentAction {
  type: 'save' | 'expand' | 'explore' | 'share' | 'start';
  label: string;
  endpoint?: string;
  params?: Record<string, any>;
}

export interface MessageComponent {
  id: string;
  type: MessageComponentType;
  data: any;
  actions: ComponentAction[];
  saved?: boolean;
  metadata?: {
    tool_source: string;
    generated_at: string;
    relevance_score?: number;
  };
}

interface MessageComponentRendererProps {
  component: MessageComponent;
  onAction: (action: ComponentAction, componentId: string) => void;
  className?: string;
}

export const MessageComponentRenderer: React.FC<MessageComponentRendererProps> = ({
  component,
  onAction,
  className = ""
}) => {
  const handleAction = (action: ComponentAction) => {
    onAction(action, component.id);
  };

  // Render different component types
  switch (component.type) {
    case MessageComponentType.SKILL_TREE:
      return (
        <SkillTreeMessageEnhanced
          component={component}
          onAction={onAction}
        />
      );

    case MessageComponentType.CAREER_PATH:
      return (
        <CareerPathMessageEnhanced
          component={component}
          onAction={onAction}
        />
      );

    case MessageComponentType.JOB_CARD:
      return (
        <JobCardMessageEnhanced
          component={component}
          onAction={onAction}
        />
      );

    case MessageComponentType.PEER_CARD:
      return (
        <PeerCardMessage
          data={component.data}
          actions={component.actions}
          onAction={handleAction}
          saved={component.saved}
          className={className}
        />
      );

    case MessageComponentType.TEST_RESULT:
      return (
        <TestResultMessage
          data={component.data}
          actions={component.actions}
          onAction={handleAction}
          saved={component.saved}
          className={className}
        />
      );

    case MessageComponentType.CHALLENGE_CARD:
      return (
        <ChallengeCardMessage
          data={component.data}
          actions={component.actions}
          onAction={handleAction}
          saved={component.saved}
          className={className}
        />
      );

    case MessageComponentType.SAVE_CONFIRMATION:
      return (
        <SaveConfirmationMessage
          data={component.data}
          className={className}
        />
      );

    case MessageComponentType.TOOL_INVOCATION:
      return (
        <ToolInvocationLoader
          toolName={component.data.toolName}
          message={component.data.message}
          className={className}
        />
      );

    default:
      // For plain text, just return null - text is handled in the main message
      return null;
  }
};