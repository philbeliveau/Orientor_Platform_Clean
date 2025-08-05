/**
 * TypeScript types for School Programs components
 */

export interface Program {
  id: string;
  title: string;
  title_fr?: string;
  description?: string;
  description_fr?: string;
  institution: {
    name: string;
    name_fr?: string;
    city: string;
    province: string;
    type: string;
    website?: string;
  };
  program_details: {
    type: string;
    level: string;
    duration_months?: number;
    language: string[];
    cip_code?: string;
    program_code?: string;
  };
  classification: {
    field_of_study?: string;
    category?: string;
  };
  admission: {
    requirements: string[];
    deadline?: string;
    application_method?: string;
  };
  academic_info: {
    credits?: number;
    internship_required?: boolean;
    coop_available?: boolean;
  };
  career_outcomes: {
    employment_rate?: number;
    job_titles: string[];
    average_salary?: {
      min: number;
      max: number;
      currency: string;
    };
  };
  costs: {
    tuition_domestic?: number;
    currency: string;
  };
  metadata: {
    search_rank?: number;
    last_updated: string;
  };
}

export interface SearchFilters {
  text: string;
  program_types: string[];
  levels: string[];
  location: {
    country?: string;
    province?: string;
    city?: string;
  };
  languages: string[];
  duration: {
    max_months?: number;
  };
  budget: {
    max_tuition?: number;
    currency: string;
  };
}

export interface SearchResults {
  results: Program[];
  pagination: {
    page: number;
    limit: number;
    total_pages: number;
    total_results: number;
    has_next: boolean;
    has_previous: boolean;
  };
  facets: {
    program_types: Record<string, number>;
    levels: Record<string, number>;
    provinces: Record<string, number>;
  };
  metadata: {
    search_time_ms: number;
    cache_hit: boolean;
  };
}

export interface UserProgramInteraction {
  program_id: string;
  interaction_type: 'viewed' | 'saved' | 'applied' | 'dismissed' | 'shared' | 'compared';
  metadata?: Record<string, any>;
}

export interface SaveProgramRequest {
  program_id: string;
  notes?: string;
  priority_level?: number;
  tags?: string[];
}