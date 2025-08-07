/**
 * Education Programs Service
 * Handles API calls for searching and fetching education programs
 */

export interface Institution {
  id: string;
  name: string;
  name_fr?: string;
  institution_type: 'cegep' | 'university' | 'college';
  city: string;
  province_state: string;
  website_url?: string;
  languages_offered: string[];
  active: boolean;
}

export interface Program {
  id: string;
  title: string;
  title_fr?: string;
  description: string;
  description_fr?: string;
  institution: Institution;
  program_type: string;
  level: 'certificate' | 'diploma' | 'associate' | 'bachelor' | 'master' | 'phd' | 'professional';
  field_of_study: string;
  duration_months?: number;
  language: string[];
  tuition_domestic?: number;
  tuition_international?: number;
  employment_rate?: number;
  admission_requirements: string[];
  career_outcomes: string[];
  cip_code?: string;
  noc_code?: string;
  holland_compatibility?: {
    R: number;
    I: number;
    A: number;
    S: number;
    E: number;
    C: number;
    overall: number;
  };
  active: boolean;
}

export interface ProgramSearchRequest {
  query?: string;
  institution_types?: ('cegep' | 'university' | 'college')[];
  program_levels?: ('certificate' | 'diploma' | 'associate' | 'bachelor' | 'master' | 'phd' | 'professional')[];
  fields_of_study?: string[];
  cities?: string[];
  languages?: string[];
  max_tuition?: number;
  min_employment_rate?: number;
  user_id?: number;
  holland_matching?: boolean;
  limit?: number;
  offset?: number;
}

export interface ProgramSearchResponse {
  programs: Program[];
  total_count: number;
  has_more: boolean;
  search_metadata: {
    search_query?: string;
    filters_applied: {
      institution_types?: string[];
      program_levels?: string[];
      cities?: string[];
      languages?: string[];
    };
    holland_matching_enabled: boolean;
    total_available_programs: number;
  };
}

export interface SearchMetadata {
  institution_types: string[];
  program_levels: string[];
  cities: string[];
  fields_of_study: string[];
  languages: string[];
  total_programs: number;
}

class EducationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async makeRequest<T>(endpoint: string, options?: RequestInit, token?: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options?.headers as Record<string, string>,
      };

      // Add auth header if token is provided
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(url, {
        headers,
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error making request to ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Search for education programs
   */
  async searchPrograms(searchRequest: ProgramSearchRequest, token?: string): Promise<ProgramSearchResponse> {
    return this.makeRequest<ProgramSearchResponse>('/api/v1/education/programs/search', {
      method: 'POST',
      body: JSON.stringify(searchRequest),
    }, token);
  }

  /**
   * Get detailed information about a specific program
   */
  async getProgramDetails(programId: string, token?: string): Promise<Program> {
    return this.makeRequest<Program>(`/api/v1/education/programs/${programId}`, {}, token);
  }

  /**
   * Get list of all institutions
   */
  async getInstitutions(token?: string): Promise<{ institutions: Institution[] }> {
    return this.makeRequest<{ institutions: Institution[] }>('/api/v1/education/institutions', {}, token);
  }

  /**
   * Get metadata for search filters
   */
  async getSearchMetadata(token?: string): Promise<SearchMetadata> {
    return this.makeRequest<SearchMetadata>('/api/v1/education/metadata', {}, token);
  }

  /**
   * Get user's Holland RIASEC scores for program matching
   */
  async getUserHollandScores(userId: number, token?: string): Promise<{ R: number; I: number; A: number; S: number; E: number; C: number } | null> {
    try {
      // This would connect to your existing Holland test results API
      const response = await this.makeRequest<any>(`/api/v1/holland/user/${userId}/latest`, {}, token);
      return {
        R: response.r_score || 0,
        I: response.i_score || 0,
        A: response.a_score || 0,
        S: response.s_score || 0,
        E: response.e_score || 0,
        C: response.c_score || 0,
      };
    } catch (error) {
      console.error('Error fetching Holland scores:', error);
      return null;
    }
  }

  /**
   * Get personalized program recommendations based on user profile
   */
  async getPersonalizedRecommendations(
    userId: number, 
    limit: number = 10
  ): Promise<ProgramSearchResponse> {
    const searchRequest: ProgramSearchRequest = {
      user_id: userId,
      holland_matching: true,
      limit,
      offset: 0,
    };

    return this.searchPrograms(searchRequest);
  }

  /**
   * Save a program to user's saved list
   */
  async saveProgram(programId: string, userId: number): Promise<void> {
    await this.makeRequest(`/api/v1/education/programs/${programId}/save`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  /**
   * Remove a program from user's saved list
   */
  async unsaveProgram(programId: string, userId: number): Promise<void> {
    await this.makeRequest(`/api/v1/education/programs/${programId}/save`, {
      method: 'DELETE',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  /**
   * Get user's saved programs
   */
  async getSavedPrograms(userId: number): Promise<Program[]> {
    const response = await this.makeRequest<{ programs: Program[] }>(`/api/v1/education/users/${userId}/saved-programs`);
    return response.programs;
  }

  /**
   * Format tuition for display
   */
  formatTuition(amount?: number, isDomestic: boolean = true): string {
    if (!amount) return 'Not specified';
    
    const currency = isDomestic ? 'CAD' : 'CAD';
    const formatted = new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

    // Add period indicator for context
    if (amount < 1000) {
      return `${formatted}/semester`;
    } else {
      return `${formatted}/year`;
    }
  }

  /**
   * Get Holland code display name
   */
  getHollandCodeName(code: string): string {
    const names: { [key: string]: string } = {
      'R': 'Realistic',
      'I': 'Investigative', 
      'A': 'Artistic',
      'S': 'Social',
      'E': 'Enterprising',
      'C': 'Conventional'
    };
    return names[code] || code;
  }

  /**
   * Calculate overall Holland compatibility percentage
   */
  calculateCompatibilityPercentage(compatibility?: Program['holland_compatibility']): number {
    if (!compatibility) return 0;
    return Math.round(compatibility.overall * 100);
  }

  /**
   * Get top Holland traits for a program
   */
  getTopHollandTraits(compatibility?: Program['holland_compatibility'], count: number = 3): string[] {
    if (!compatibility) return [];
    
    const traits = Object.entries(compatibility)
      .filter(([key]) => key !== 'overall')
      .sort(([, a], [, b]) => b - a)
      .slice(0, count)
      .map(([key]) => this.getHollandCodeName(key));
    
    return traits;
  }

  /**
   * Get user's education dashboard data
   */
  async getUserDashboard(userId: number): Promise<{
    user: { name: string; completedPrograms: number; totalPrograms: number; completionPercentage: number };
    progress: Array<{ id: number; subject: string; progress: number; lessonNumber: string }>;
    activities: Array<{ id: number; user: string; action: string; time: string; subject: string }>;
    upcomingSchedule: Array<{ time: string; title: string; type: string; date: string }>;
  }> {
    // In production, this would be a real API call
    // For now, return mock data that matches the UI
    return {
      user: {
        name: "Alex",
        completedPrograms: 204,
        totalPrograms: 300,
        completionPercentage: 68
      },
      progress: [
        { id: 1, subject: "Computer Science", progress: 65, lessonNumber: "#13" },
        { id: 2, subject: "Business Admin", progress: 80, lessonNumber: "#79" },
        { id: 3, subject: "Engineering", progress: 45, lessonNumber: "#101" }
      ],
      activities: [
        { id: 1, user: "Sia Lubich", action: "Added new assignment", time: "Jan 2, 12:30", subject: "Computer Science, Topic 1" },
        { id: 2, user: "Christian Driss", action: "Deadline approaching", time: "Jan 2, 12:25", subject: "Mathematics, Topic 2" },
        { id: 3, user: "Ann Golden", action: "New date of exam posted", time: "Jan 2, 12:04", subject: "History, Topic 1,2" }
      ],
      upcomingSchedule: [
        { time: "09:00", title: "Course Name: Lesson", type: "lesson", date: "Jan 2, 12:31pm" },
        { time: "10:00", title: "Course Name: Test", type: "test", date: "Jan 2, 12:31pm" },
        { time: "11:00", title: "Extracurricular activities", type: "activity", date: "Jan 2, 12:31pm" }
      ]
    };
  }

  /**
   * Get user's enrolled courses/programs
   */
  async getUserCourses(userId: number): Promise<Array<{
    id: number;
    title: string;
    instructor: string;
    section: string;
    enrolledStudents: number;
    image: string;
  }>> {
    // In production, this would connect to the actual enrollment API
    return [
      {
        id: 1,
        title: "Introduction to Computer Science",
        instructor: "Sara Goldman",
        section: "Section 9A • 9B",
        enrolledStudents: 24,
        image: "🧬"
      },
      {
        id: 2,
        title: "Master of Business Administration",
        instructor: "Jonathan Weston",
        section: "Section 10A",
        enrolledStudents: 18,
        image: "🗂️"
      },
      {
        id: 3,
        title: "Software Engineering Fundamentals",
        instructor: "Jonathan Weston",
        section: "Section 9A • 9B",
        enrolledStudents: 32,
        image: "🧮"
      }
    ];
  }

  /**
   * Mark activity as read
   */
  async markActivityAsRead(activityId: number, userId: number): Promise<void> {
    // In production, this would update the activity status
    console.log(`Marking activity ${activityId} as read for user ${userId}`);
  }

  /**
   * Get calendar events for a specific month
   */
  async getCalendarEvents(userId: number, year: number, month: number): Promise<Array<{
    date: number;
    type: 'lesson' | 'test' | 'activity';
    title: string;
    time?: string;
  }>> {
    // Mock calendar events
    return [
      { date: 11, type: 'lesson', title: 'Computer Science Lecture', time: '09:00' },
      { date: 15, type: 'test', title: 'Mathematics Exam', time: '14:00' },
      { date: 22, type: 'activity', title: 'Study Group', time: '16:00' },
      { date: 26, type: 'lesson', title: 'Business Workshop', time: '10:00' }
    ];
  }
}

// Export singleton instance
const educationService = new EducationService();
export default educationService;