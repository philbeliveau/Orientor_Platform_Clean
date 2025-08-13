// Common API types for type-safe API client
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: string;
}

// Career Goals types
export interface CareerGoal {
  id: number;
  title: string;
  description?: string;
  target_date: string;
  progress_percentage: number;
  created_at?: string;
  updated_at?: string;
}

export interface CreateCareerGoalRequest {
  title: string;
  description?: string;
  target_date: string;
}

export interface UpdateCareerGoalRequest {
  title?: string;
  description?: string;
  target_date?: string;
  progress_percentage?: number;
}

// Avatar types
export interface AvatarData {
  success: boolean;
  avatar_name?: string;
  avatar_description?: string;
  avatar_image_url?: string;
  user_id?: number;
}

export interface UpdateAvatarRequest {
  avatar_name?: string;
  avatar_description?: string;
  avatar_image_url?: string;
}

// User Profile types
export interface UserProfile {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  created_at: string;
  updated_at: string;
  onboarding_completed?: boolean;
}

// Job Recommendation types
export interface JobRecommendation {
  id: number;
  title: string;
  description?: string;
  company?: string;
  location?: string;
  salary_range?: string;
  skills_required?: string[];
  match_score?: number;
}

// Holland Test types
export interface HollandResults {
  id: number;
  user_id: number;
  realistic_score: number;
  investigative_score: number;
  artistic_score: number;
  social_score: number;
  enterprising_score: number;
  conventional_score: number;
  holland_code: string;
  created_at: string;
}

// Skills Tree types
export interface SkillNode {
  id: string;
  name: string;
  description?: string;
  level: number;
  prerequisites?: string[];
  children?: SkillNode[];
}

export interface SkillsTreeData {
  tree_data: SkillNode[];
  job_id?: string;
  job_title?: string;
}

// Note/Space types
export interface UserNote {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// Peer types
export interface CompatiblePeer {
  id: number;
  user_id: number;
  first_name?: string;
  last_name?: string;
  holland_code?: string;
  compatibility_score: number;
  shared_interests?: string[];
}

// Career/Job Save types
export interface SaveCareerRequest {
  id: number;
  title: string;
}

export interface SaveCareerResponse {
  success: boolean;
  message: string;
  career_id: number;
}

// Onboarding types
export interface OnboardingStatus {
  onboarding_completed: boolean;
  has_started: boolean;
  is_complete: boolean;
  message: string;
}

// Generic pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Request options for API calls
export interface ApiRequestOptions extends RequestInit {
  token?: string;
}

// Type guards for runtime validation
export function isApiResponse<T>(obj: any): obj is ApiResponse<T> {
  return obj && typeof obj === 'object' && 'data' in obj;
}

export function isApiError(obj: any): obj is ApiError {
  return obj && typeof obj === 'object' && 'status' in obj && 'message' in obj;
}