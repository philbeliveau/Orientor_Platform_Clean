// In components/branches/career_growth.ts
export interface SkillNode {
    id: string;
    skillDescription: string;
    improvementSuggestion?: string;
    taskSuggestion?: string;
    nextSkills?: SkillNode[];
    reachableJobs?: {
      jobTitle: string;
      jobDomain?: string;
      requiredSkills: string[];
    }[];
  }
  