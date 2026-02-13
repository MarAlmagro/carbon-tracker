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
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface ActivityInput {
  category: string;
  type: string;
  value: number;
  date: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export interface ActivityUpdateInput {
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

export interface FootprintSummary {
  period: string;
  start_date: string;
  end_date: string;
  total_co2e_kg: number;
  activity_count: number;
  previous_period_co2e_kg: number;
  change_percentage: number;
  average_daily_co2e_kg: number;
}

export interface CategoryBreakdown {
  period: string;
  breakdown: Array<{
    category: string;
    co2e_kg: number;
    percentage: number;
    activity_count: number;
  }>;
  total_co2e_kg: number;
}

export interface FootprintTrend {
  period: string;
  granularity: string;
  data_points: Array<{
    date: string;
    co2e_kg: number;
    activity_count: number;
  }>;
  total_co2e_kg: number;
  average_co2e_kg: number;
}

export interface Airport {
  iata_code: string;
  name: string;
  city: string;
  country: string;
  country_code: string;
  latitude: number;
  longitude: number;
}

export interface AirportSearchResponse {
  results: Airport[];
}

export interface FlightCalculationRequest {
  origin_iata: string;
  destination_iata: string;
}

export interface FlightCalculation {
  origin_iata: string;
  destination_iata: string;
  distance_km: number;
  flight_type: string;
  is_domestic: boolean;
  haul_type: string;
}

export interface Region {
  code: string;
  name: string;
  average_annual_co2e_kg: number;
}

export interface ComparisonResult {
  user_footprint: {
    period: string;
    total_co2e_kg: number;
    start_date: string;
    end_date: string;
    activity_count: number;
  };
  regional_average: {
    region_code: string;
    region_name: string;
    average_annual_co2e_kg: number;
  };
  comparison: {
    difference_kg: number;
    difference_percentage: number;
    percentile: number;
    rating: string;
    insights: string[];
  };
  breakdown: {
    user_by_category: Record<string, number>;
    regional_avg_by_category: Record<string, number>;
  };
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

  async updateActivity(id: string, input: ActivityUpdateInput): Promise<Activity> {
    return this.request<Activity>(`/api/v1/activities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(input),
    });
  }

  async deleteActivity(id: string): Promise<void> {
    const authHeaders = this.getAuthHeaders();

    const response = await fetch(`${this.baseUrl}/api/v1/activities/${id}`, {
      method: 'DELETE',
      headers: {
        ...authHeaders,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'An error occurred',
      }));
      throw new Error(error.detail || 'API request failed');
    }
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
  async getFootprintSummary(period: string = 'month'): Promise<FootprintSummary> {
    return this.request<FootprintSummary>(`/api/v1/footprint/summary?period=${period}`);
  }

  async getFootprintBreakdown(period: string = 'month'): Promise<CategoryBreakdown> {
    return this.request<CategoryBreakdown>(`/api/v1/footprint/breakdown?period=${period}`);
  }

  async getFootprintTrend(period: string = 'month'): Promise<FootprintTrend> {
    return this.request<FootprintTrend>(`/api/v1/footprint/trend?period=${period}`);
  }

  async searchAirports(query: string, limit: number = 10): Promise<AirportSearchResponse> {
    const params = new URLSearchParams({ q: query, limit: limit.toString() });
    return this.request<AirportSearchResponse>(`/api/v1/airports/search?${params}`);
  }

  async calculateFlight(request: FlightCalculationRequest): Promise<FlightCalculation> {
    return this.request<FlightCalculation>('/api/v1/flights/calculate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getRegions(): Promise<Region[]> {
    const response = await this.request<{ regions: Region[] }>('/api/v1/comparison/regions');
    return response.regions;
  }

  async compareToRegion(regionCode: string, period: string = 'year'): Promise<ComparisonResult> {
    return this.request<ComparisonResult>(
      `/api/v1/comparison/compare?region_code=${regionCode}&period=${period}`
    );
  }
}

export const apiClient = new ApiClient();
