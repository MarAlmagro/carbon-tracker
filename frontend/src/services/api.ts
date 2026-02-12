import { useAuthStore } from '@/store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  message: string;
}

export interface Activity {
  id: string;
  category: string;
  type: string;
  value: number;
  co2e_kg: number;
  date: string;
  notes?: string;
  created_at: string;
}

export interface ActivityInput {
  category: string;
  type: string;
  value: number;
  date: string;
  notes?: string;
}

export interface EmissionFactor {
  id: number;
  category: string;
  type: string;
  factor: number;
  unit: string;
  source?: string;
}

export interface UserResponse {
  id: string;
  email: string;
  created_at: string;
}

export interface MigrateActivitiesResponse {
  migrated_count: number;
}

export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    const state = useAuthStore.getState();

    if (state.session?.access_token) {
      headers['Authorization'] = `Bearer ${state.session.access_token}`;
    }

    if (state.sessionId) {
      headers['X-Session-ID'] = state.sessionId;
    }

    return headers;
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const authHeaders = this.getAuthHeaders();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'An error occurred',
      }));
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/api/v1/health');
  }

  async createActivity(input: ActivityInput): Promise<Activity> {
    return this.request<Activity>('/api/v1/activities', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async listActivities(limit = 50): Promise<Activity[]> {
    return this.request<Activity[]>(`/api/v1/activities?limit=${limit}`);
  }

  async getEmissionFactors(category?: string): Promise<EmissionFactor[]> {
    const query = category ? `?category=${category}` : '';
    return this.request<EmissionFactor[]>(`/api/v1/emission-factors${query}`);
  }

  async getCurrentUser(): Promise<UserResponse> {
    return this.request<UserResponse>('/api/v1/users/me');
  }

  async migrateActivities(sessionId: string): Promise<MigrateActivitiesResponse> {
    return this.request<MigrateActivitiesResponse>(
      '/api/v1/users/me/migrate-activities',
      {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
      }
    );
  }
}

export const apiClient = new ApiClient();
