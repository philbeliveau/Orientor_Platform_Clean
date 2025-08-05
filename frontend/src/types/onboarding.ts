export interface ChatMessage {
  id: string;
  type: 'system' | 'user';
  content: string;
  timestamp: Date;
}

export interface OnboardingResponse {
  questionId: string;
  question: string;
  response: string;
  timestamp: Date;
}

export interface HEXACODimension {
  honesty: number;
  emotionality: number;
  extraversion: number;
  agreeableness: number;
  conscientiousness: number;
  openness: number;
}

export interface RIASECDimension {
  realistic: number;
  investigative: number;
  artistic: number;
  social: number;
  enterprising: number;
  conventional: number;
}

export interface PsychProfile {
  hexaco: Partial<HEXACODimension>;
  riasec: Partial<RIASECDimension>;
  topTraits: string[];
  description: string;
}

export interface OnboardingQuestion {
  id: string;
  text: string;
  type: 'emotion' | 'hexaco' | 'riasec' | 'future';
  dimension?: keyof HEXACODimension | keyof RIASECDimension;
  weight?: number;
}

export interface OnboardingState {
  currentQuestionIndex: number;
  responses: OnboardingResponse[];
  messages: ChatMessage[];
  isTyping: boolean;
  isComplete: boolean;
  psychProfile?: PsychProfile;
}

export interface CareerRecommendation {
  id: string;
  title: string;
  description: string;
  match_percentage: number;
  oasis_code?: string;
  skills_required?: string[];
  education_level?: string;
}