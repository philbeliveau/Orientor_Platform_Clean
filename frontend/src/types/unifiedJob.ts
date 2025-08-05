// Unified job type definitions for both ESCO and OaSIS sources

export type DataSource = 'ESCO' | 'OaSIS';

// Base interface for common job properties
export interface BaseJob {
  id: string | number;
  title: string;
  description?: string;
  dataSource: DataSource;
  savedAt?: string;
  relevanceScore?: number;
}

// ESCO-specific job properties
export interface ESCOJob extends BaseJob {
  dataSource: 'ESCO';
  escoId: string;
  skillsRequired: string[];
  educationLevel?: string;
  experienceYears?: string;
  industry?: string;
  alternativeLabels?: string[];
  broaderOccupations?: string[];
  narrowerOccupations?: string[];
  iscoCode?: string;
  regulatedProfession?: boolean;
  metadata?: Record<string, any>;
}

// OaSIS-specific job properties
export interface OaSISJob extends BaseJob {
  dataSource: 'OaSIS';
  oasisCode: string;
  mainDuties?: string;
  entryQualifications?: string;
  
  // Role skills (1-5 scale)
  roleCreativity?: number;
  roleLeadership?: number;
  roleDigitalLiteracy?: number;
  roleCriticalThinking?: number;
  roleProblemSolving?: number;
  
  // Work characteristics (1-5 scale)
  analyticalThinking?: number;
  attentionToDetail?: number;
  collaboration?: number;
  adaptability?: number;
  independence?: number;
  evaluation?: number;
  decisionMaking?: number;
  stressTolerance?: number;
  
  // LLM Analysis
  personalAnalysis?: string;
  suggestedImprovements?: string;
  
  // Additional fields
  allFields?: Record<string, string>;
}

// Unified job type
export type UnifiedJob = ESCOJob | OaSISJob;

// Type guards
export const isESCOJob = (job: UnifiedJob): job is ESCOJob => {
  return job.dataSource === 'ESCO';
};

export const isOaSISJob = (job: UnifiedJob): job is OaSISJob => {
  return job.dataSource === 'OaSIS';
};

// Feasibility data for career transitions
export interface FeasibilityData {
  barriers: Barrier[];
  timeline: TimelineItem[];
  requirements: Requirement[];
  feasibilityScore: number; // 0-100
}

export interface Barrier {
  type: 'education' | 'skill' | 'experience' | 'certification' | 'financial';
  description: string;
  severity: 'low' | 'medium' | 'high';
  estimatedTimeToOvercome?: string;
  suggestedActions?: string[];
}

export interface TimelineItem {
  phase: string;
  duration: string;
  activities: string[];
  milestones: string[];
}

export interface Requirement {
  category: 'mandatory' | 'recommended' | 'nice-to-have';
  description: string;
  currentStatus: 'met' | 'not-met' | 'partial';
  details?: string;
}

// Skill comparison data
export interface SkillDelta {
  skillName: string;
  requiredLevel: number;
  currentLevel: number;
  gap: number;
  priority: 'critical' | 'important' | 'beneficial';
  improvementPath?: string[];
}

// User skills interface
export interface UserSkills {
  creativity: number;
  leadership: number;
  digitalLiteracy: number;
  criticalThinking: number;
  problemSolving: number;
  analyticalThinking: number;
  attentionToDetail: number;
  collaboration: number;
  adaptability: number;
  independence: number;
  evaluation: number;
  decisionMaking: number;
  stressTolerance: number;
}