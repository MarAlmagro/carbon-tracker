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

export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
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

  async createActivity(input: ActivityInput, sessionId: string): Promise<Activity> {
    return this.request<Activity>('/api/v1/activities', {
      method: 'POST',
      headers: {
        'X-Session-ID': sessionId,
      },
      body: JSON.stringify(input),
    });
  }

  async listActivities(sessionId: string, limit = 50): Promise<Activity[]> {
    return this.request<Activity[]>(`/api/v1/activities?limit=${limit}`, {
      headers: {
        'X-Session-ID': sessionId,
      },
    });
  }

  async getEmissionFactors(category?: string): Promise<EmissionFactor[]> {
    const query = category ? `?category=${category}` : '';
    return this.request<EmissionFactor[]>(`/api/v1/emission-factors${query}`);
  }
}

export const apiClient = new ApiClient();
