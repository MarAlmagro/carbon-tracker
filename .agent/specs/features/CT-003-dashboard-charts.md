# Feature: Dashboard with Charts & Visualizations

## Metadata
- **ID**: CT-003
- **Priority**: MEDIUM-HIGH
- **Estimated Effort**: 8-10 hours
- **Dependencies**: CT-000 (Project Foundation), CT-001 (Transport Logging), CT-002 (Authentication - optional)

## Summary
Implement a comprehensive dashboard with data visualizations including footprint summary cards, category breakdown pie chart, and time-based trend line chart with period selection (day/week/month/year).

## User Story
As a **Carbon Tracker user**, I want to **visualize my carbon footprint over time with charts and statistics** so that **I can understand my environmental impact and identify areas for improvement**.

## Acceptance Criteria
- [ ] AC1: Dashboard displays total CO2e for selected period (day/week/month/year/all)
- [ ] AC2: Summary card shows total emissions with period comparison (vs previous period)
- [ ] AC3: Pie chart shows breakdown by category (transport, energy, food) with percentages
- [ ] AC4: Line chart shows daily emissions trend over selected period
- [ ] AC5: Period selector switches between day/week/month/year/all views
- [ ] AC6: Empty state displayed when no activities exist for period
- [ ] AC7: All charts are responsive and mobile-friendly
- [ ] AC8: Data updates automatically when new activity is logged
- [ ] AC9: Charts display loading states during data fetch
- [ ] AC10: User-specific data shown if authenticated, session-based if guest

## API Contract

### 1. Get Footprint Summary
**Endpoint:** `GET /api/v1/footprint/summary`

**Query Parameters:**
- `period` (optional): `day` | `week` | `month` | `year` | `all` (default: `month`)
- `start_date` (optional): ISO 8601 date (e.g., `2026-02-01`)
- `end_date` (optional): ISO 8601 date (e.g., `2026-02-28`)

**Request Headers:**
```http
Authorization: Bearer eyJhbGc... (optional - for authenticated users)
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000 (required for guests)
```

**Response (200 OK):**
```json
{
  "period": "month",
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "total_co2e_kg": 145.67,
  "activity_count": 23,
  "previous_period_co2e_kg": 132.45,
  "change_percentage": 9.98,
  "average_daily_co2e_kg": 5.20
}
```

### 2. Get Footprint Breakdown by Category
**Endpoint:** `GET /api/v1/footprint/breakdown`

**Query Parameters:**
- `period` (optional): `day` | `week` | `month` | `year` | `all` (default: `month`)
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date

**Request Headers:**
```http
Authorization: Bearer eyJhbGc... (optional)
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "period": "month",
  "breakdown": [
    {
      "category": "transport",
      "co2e_kg": 89.34,
      "percentage": 61.3,
      "activity_count": 15
    },
    {
      "category": "energy",
      "co2e_kg": 42.12,
      "percentage": 28.9,
      "activity_count": 6
    },
    {
      "category": "food",
      "co2e_kg": 14.21,
      "percentage": 9.8,
      "activity_count": 2
    }
  ],
  "total_co2e_kg": 145.67
}
```

### 3. Get Footprint Trend
**Endpoint:** `GET /api/v1/footprint/trend`

**Query Parameters:**
- `period` (optional): `day` | `week` | `month` | `year` (default: `month`)
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date
- `granularity` (optional): `daily` | `weekly` | `monthly` (default: auto-selected based on period)

**Request Headers:**
```http
Authorization: Bearer eyJhbGc...
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "period": "month",
  "granularity": "daily",
  "data_points": [
    {
      "date": "2026-02-01",
      "co2e_kg": 5.23,
      "activity_count": 2
    },
    {
      "date": "2026-02-02",
      "co2e_kg": 8.45,
      "activity_count": 3
    },
    {
      "date": "2026-02-03",
      "co2e_kg": 3.21,
      "activity_count": 1
    }
    // ... more data points
  ],
  "total_co2e_kg": 145.67,
  "average_co2e_kg": 5.20
}
```

## UI/UX Requirements

### Updated Dashboard Page

#### Layout Structure
```
┌─────────────────────────────────────────────────┐
│  Period Selector: [Day|Week|Month▼|Year|All]    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  SUMMARY CARD                           │   │
│  │  Total: 145.67 kg CO2e                  │   │
│  │  23 activities                          │   │
│  │  ↑ 9.98% vs last month                  │   │
│  │  Avg: 5.20 kg/day                       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────────────┐  ┌──────────────────┐   │
│  │  PIE CHART       │  │  TREND CHART     │   │
│  │  Category        │  │  Daily Emissions  │   │
│  │  Breakdown       │  │  Over Time       │   │
│  │                  │  │                  │   │
│  └──────────────────┘  └──────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  RECENT ACTIVITIES (from CT-001)        │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

#### Empty State
When no activities exist:
```
┌─────────────────────────────────────────────────┐
│                                                 │
│           🌱                                    │
│                                                 │
│    No activities for this period               │
│                                                 │
│    Start tracking your carbon footprint        │
│                                                 │
│    [+ Log Activity]                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Component Specifications

#### 1. Period Selector
- Horizontal tabs or dropdown on mobile
- Options: Day, Week, Month, Year, All Time
- Active state styling
- Default: Month

#### 2. Summary Card
- Large total CO2e number (kg CO2e)
- Activity count
- Comparison with previous period (percentage + arrow icon)
- Average daily emissions
- Green/red color coding for percentage change

#### 3. Category Breakdown Pie Chart
- Uses Recharts PieChart
- 3 segments: Transport, Energy, Food
- Color-coded: Blue (transport), Yellow (energy), Green (food)
- Shows percentage labels
- Legend with category names and totals
- Tooltip on hover with exact kg CO2e

#### 4. Trend Line Chart
- Uses Recharts LineChart
- X-axis: Dates (formatted based on granularity)
- Y-axis: CO2e (kg)
- Single line with gradient fill
- Dots on data points
- Tooltip with date and exact value
- Responsive grid lines

### Responsive Design
- **Desktop (>1024px):** Charts side-by-side in 2-column grid
- **Tablet (768-1024px):** Charts stacked vertically
- **Mobile (<768px):** Single column, period selector as dropdown

## Technical Design

### What's Already Done (CT-000/CT-001/CT-002)

#### Backend
- ✓ Activity entity and repository with query methods
- ✓ EmissionFactor entity and repository
- ✓ CalculationService for CO2e calculation
- ✓ Activities table with `category`, `co2e_kg`, `date`, `user_id`, `session_id` columns
- ✓ GET /api/v1/activities endpoint (lists all activities)
- ✓ Authentication dependencies (`get_optional_user`, `get_session_id`)

#### Frontend
- ✓ DashboardPage component (basic structure)
- ✓ ActivityList and ActivityCard components (CT-001)
- ✓ useActivities hook with React Query
- ✓ API client with request method
- ✓ Auth store with sessionId

### What Needs to Be Built

#### Backend (NEW)

**1. Aggregation Service** (`backend/src/domain/services/aggregation_service.py` - NEW)

```python
from datetime import date, datetime, timedelta
from typing import List
from domain.entities.activity import Activity

class AggregationService:
    """Service for aggregating activity data."""

    @staticmethod
    def calculate_total_co2e(activities: List[Activity]) -> float:
        """Calculate total CO2e from activities."""
        return round(sum(activity.co2e_kg for activity in activities), 2)

    @staticmethod
    def calculate_breakdown_by_category(
        activities: List[Activity]
    ) -> dict[str, float]:
        """Group activities by category and sum CO2e."""
        breakdown: dict[str, float] = {}
        for activity in activities:
            category = activity.category
            breakdown[category] = breakdown.get(category, 0) + activity.co2e_kg
        return {k: round(v, 2) for k, v in breakdown.items()}

    @staticmethod
    def calculate_daily_trend(
        activities: List[Activity],
        start_date: date,
        end_date: date
    ) -> dict[date, float]:
        """Aggregate activities by day."""
        # Create dict with all dates in range initialized to 0
        trend: dict[date, float] = {}
        current = start_date
        while current <= end_date:
            trend[current] = 0.0
            current += timedelta(days=1)

        # Sum CO2e by date
        for activity in activities:
            if start_date <= activity.date <= end_date:
                trend[activity.date] = trend.get(activity.date, 0) + activity.co2e_kg

        return {k: round(v, 2) for k, v in trend.items()}

    @staticmethod
    def get_period_dates(period: str, reference_date: date | None = None) -> tuple[date, date]:
        """Calculate start and end dates for a period."""
        if reference_date is None:
            reference_date = date.today()

        if period == "day":
            return reference_date, reference_date
        elif period == "week":
            start = reference_date - timedelta(days=reference_date.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif period == "month":
            start = reference_date.replace(day=1)
            # Last day of month
            if reference_date.month == 12:
                end = reference_date.replace(day=31)
            else:
                end = (reference_date.replace(month=reference_date.month + 1, day=1)
                       - timedelta(days=1))
            return start, end
        elif period == "year":
            start = reference_date.replace(month=1, day=1)
            end = reference_date.replace(month=12, day=31)
            return start, end
        else:  # "all"
            return date(2020, 1, 1), date(2030, 12, 31)
```

**2. Get Footprint Summary Use Case** (`backend/src/domain/use_cases/get_footprint_summary.py` - NEW)

```python
from datetime import date
from typing import Optional
from uuid import UUID
from domain.ports.activity_repository import ActivityRepository
from domain.services.aggregation_service import AggregationService

class GetFootprintSummaryInput:
    """Input for footprint summary use case."""
    def __init__(
        self,
        user_id: Optional[UUID],
        session_id: Optional[str],
        period: str = "month",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.period = period
        self.start_date = start_date
        self.end_date = end_date

class FootprintSummary:
    """Output for footprint summary."""
    def __init__(
        self,
        period: str,
        start_date: date,
        end_date: date,
        total_co2e_kg: float,
        activity_count: int,
        previous_period_co2e_kg: float,
        change_percentage: float,
        average_daily_co2e_kg: float
    ):
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.total_co2e_kg = total_co2e_kg
        self.activity_count = activity_count
        self.previous_period_co2e_kg = previous_period_co2e_kg
        self.change_percentage = change_percentage
        self.average_daily_co2e_kg = average_daily_co2e_kg

class GetFootprintSummaryUseCase:
    """Get carbon footprint summary for a period."""

    def __init__(
        self,
        activity_repo: ActivityRepository,
        aggregation_service: AggregationService
    ):
        self._activity_repo = activity_repo
        self._aggregation_service = aggregation_service

    async def execute(self, input_data: GetFootprintSummaryInput) -> FootprintSummary:
        """Execute the use case."""
        # Calculate dates
        if input_data.start_date and input_data.end_date:
            start_date = input_data.start_date
            end_date = input_data.end_date
        else:
            start_date, end_date = self._aggregation_service.get_period_dates(
                input_data.period
            )

        # Fetch current period activities
        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate metrics
        total_co2e = self._aggregation_service.calculate_total_co2e(activities)
        activity_count = len(activities)

        # Calculate previous period for comparison
        period_length = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)

        prev_activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=prev_start,
            end_date=prev_end
        )
        prev_total = self._aggregation_service.calculate_total_co2e(prev_activities)

        # Calculate change percentage
        if prev_total > 0:
            change_pct = ((total_co2e - prev_total) / prev_total) * 100
        else:
            change_pct = 0.0 if total_co2e == 0 else 100.0

        # Calculate average daily
        avg_daily = total_co2e / period_length if period_length > 0 else 0.0

        return FootprintSummary(
            period=input_data.period,
            start_date=start_date,
            end_date=end_date,
            total_co2e_kg=round(total_co2e, 2),
            activity_count=activity_count,
            previous_period_co2e_kg=round(prev_total, 2),
            change_percentage=round(change_pct, 2),
            average_daily_co2e_kg=round(avg_daily, 2)
        )
```

**3. Get Footprint Breakdown Use Case** (`backend/src/domain/use_cases/get_footprint_breakdown.py` - NEW)

Similar structure to GetFootprintSummaryUseCase, returns breakdown by category.

**4. Get Footprint Trend Use Case** (`backend/src/domain/use_cases/get_footprint_trend.py` - NEW)

Similar structure, returns time-series data using `calculate_daily_trend()`.

**5. Update Activity Repository Port** (`backend/src/domain/ports/activity_repository.py`)

```python
@abstractmethod
async def list_by_date_range(
    self,
    user_id: Optional[UUID],
    session_id: Optional[str],
    start_date: date,
    end_date: date
) -> List[Activity]:
    """List activities within date range for user/session."""
    pass
```

**6. Implement in Supabase Repository** (`backend/src/infrastructure/repositories/supabase_activity_repository.py`)

```python
async def list_by_date_range(
    self,
    user_id: Optional[UUID],
    session_id: Optional[str],
    start_date: date,
    end_date: date
) -> List[Activity]:
    """List activities within date range."""
    query = self._client.table("activities").select("*")

    if user_id:
        query = query.eq("user_id", str(user_id))
    elif session_id:
        query = query.eq("session_id", session_id)

    query = query.gte("date", start_date.isoformat()) \
                 .lte("date", end_date.isoformat()) \
                 .order("date", desc=False)

    response = query.execute()
    return [self._row_to_entity(row) for row in response.data]
```

**7. Footprint Schemas** (`backend/src/api/schemas/footprint.py` - NEW)

```python
from datetime import date
from pydantic import BaseModel, Field

class FootprintSummaryResponse(BaseModel):
    """Footprint summary response."""
    period: str
    start_date: date
    end_date: date
    total_co2e_kg: float = Field(ge=0)
    activity_count: int = Field(ge=0)
    previous_period_co2e_kg: float = Field(ge=0)
    change_percentage: float
    average_daily_co2e_kg: float = Field(ge=0)

class CategoryBreakdownItem(BaseModel):
    """Single category in breakdown."""
    category: str
    co2e_kg: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    activity_count: int = Field(ge=0)

class FootprintBreakdownResponse(BaseModel):
    """Footprint breakdown by category."""
    period: str
    breakdown: list[CategoryBreakdownItem]
    total_co2e_kg: float = Field(ge=0)

class TrendDataPoint(BaseModel):
    """Single point in trend chart."""
    date: date
    co2e_kg: float = Field(ge=0)
    activity_count: int = Field(ge=0)

class FootprintTrendResponse(BaseModel):
    """Footprint trend over time."""
    period: str
    granularity: str
    data_points: list[TrendDataPoint]
    total_co2e_kg: float = Field(ge=0)
    average_co2e_kg: float = Field(ge=0)
```

**8. Footprint Routes** (`backend/src/api/routes/footprint.py` - NEW)

```python
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from domain.entities.user import User
from domain.use_cases.get_footprint_summary import (
    GetFootprintSummaryUseCase,
    GetFootprintSummaryInput
)
from api.dependencies.auth import get_optional_user
from api.dependencies.session import get_session_id
from api.dependencies.use_cases import get_footprint_summary_use_case
from api.schemas.footprint import FootprintSummaryResponse

router = APIRouter(prefix="/footprint", tags=["footprint"])

@router.get("/summary", response_model=FootprintSummaryResponse)
async def get_footprint_summary(
    period: str = Query("month", regex="^(day|week|month|year|all)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: Optional[User] = Depends(get_optional_user),
    session_id: str = Depends(get_session_id),
    use_case: GetFootprintSummaryUseCase = Depends(get_footprint_summary_use_case)
) -> FootprintSummaryResponse:
    """Get carbon footprint summary for period."""
    input_data = GetFootprintSummaryInput(
        user_id=user.id if user else None,
        session_id=session_id if not user else None,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    summary = await use_case.execute(input_data)

    return FootprintSummaryResponse(
        period=summary.period,
        start_date=summary.start_date,
        end_date=summary.end_date,
        total_co2e_kg=summary.total_co2e_kg,
        activity_count=summary.activity_count,
        previous_period_co2e_kg=summary.previous_period_co2e_kg,
        change_percentage=summary.change_percentage,
        average_daily_co2e_kg=summary.average_daily_co2e_kg
    )

# Similar endpoints for /breakdown and /trend
```

**9. Update Use Case Dependencies** (`backend/src/api/dependencies/use_cases.py`)

```python
def get_footprint_summary_use_case(
    client: Client = Depends(get_supabase_client)
) -> GetFootprintSummaryUseCase:
    return GetFootprintSummaryUseCase(
        activity_repo=SupabaseActivityRepository(client),
        aggregation_service=AggregationService()
    )
```

**10. Register Footprint Router** (`backend/src/api/main.py`)

```python
from api.routes import footprint

app.include_router(footprint.router, prefix="/api/v1", tags=["footprint"])
```

#### Frontend (NEW)

**1. Install Recharts** (`frontend/package.json`)

```bash
npm install recharts
npm install --save-dev @types/recharts
```

**2. Footprint API Methods** (`frontend/src/services/api.ts`)

```typescript
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

export class ApiClient {
  // ... existing methods ...

  async getFootprintSummary(period: string = 'month'): Promise<FootprintSummary> {
    return this.request<FootprintSummary>(`/api/v1/footprint/summary?period=${period}`);
  }

  async getFootprintBreakdown(period: string = 'month'): Promise<CategoryBreakdown> {
    return this.request<CategoryBreakdown>(`/api/v1/footprint/breakdown?period=${period}`);
  }

  async getFootprintTrend(period: string = 'month'): Promise<FootprintTrend> {
    return this.request<FootprintTrend>(`/api/v1/footprint/trend?period=${period}`);
  }
}
```

**3. Footprint Hook** (`frontend/src/hooks/useFootprint.ts` - NEW)

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';

export function useFootprintSummary(period: string) {
  return useQuery({
    queryKey: ['footprint', 'summary', period],
    queryFn: () => apiClient.getFootprintSummary(period)
  });
}

export function useFootprintBreakdown(period: string) {
  return useQuery({
    queryKey: ['footprint', 'breakdown', period],
    queryFn: () => apiClient.getFootprintBreakdown(period)
  });
}

export function useFootprintTrend(period: string) {
  return useQuery({
    queryKey: ['footprint', 'trend', period],
    queryFn: () => apiClient.getFootprintTrend(period)
  });
}
```

**4. Period Selector Component** (`frontend/src/components/features/footprint/PeriodSelector.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';

interface PeriodSelectorProps {
  value: string;
  onChange: (period: string) => void;
}

const PERIODS = ['day', 'week', 'month', 'year', 'all'] as const;

export default function PeriodSelector({ value, onChange }: PeriodSelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="flex space-x-2 border-b border-gray-200">
      {PERIODS.map((period) => (
        <button
          key={period}
          onClick={() => onChange(period)}
          className={`px-4 py-2 font-medium ${
            value === period
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {t(`dashboard.period.${period}`)}
        </button>
      ))}
    </div>
  );
}
```

**5. Summary Card Component** (`frontend/src/components/features/footprint/SummaryCard.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';
import { FootprintSummary } from '@/services/api';

interface SummaryCardProps {
  data: FootprintSummary;
}

export default function SummaryCard({ data }: SummaryCardProps) {
  const { t } = useTranslation();

  const changeIcon = data.change_percentage > 0 ? '↑' : data.change_percentage < 0 ? '↓' : '→';
  const changeColor = data.change_percentage > 0 ? 'text-red-600' : 'text-green-600';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-sm font-medium text-gray-600 mb-2">
        {t('dashboard.title')}
      </h2>

      <div className="text-4xl font-bold text-gray-900 mb-4">
        {data.total_co2e_kg.toFixed(2)} <span className="text-xl text-gray-500">kg CO2e</span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">{t('dashboard.activities')}</span>
          <span className="font-medium">{data.activity_count}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-600">vs {t(`dashboard.period.${data.period}`)}</span>
          <span className={`font-medium ${changeColor}`}>
            {changeIcon} {Math.abs(data.change_percentage).toFixed(1)}%
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-600">{t('dashboard.avgDaily')}</span>
          <span className="font-medium">{data.average_daily_co2e_kg.toFixed(2)} kg</span>
        </div>
      </div>
    </div>
  );
}
```

**6. Category Breakdown Chart** (`frontend/src/components/features/footprint/CategoryBreakdownChart.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { CategoryBreakdown } from '@/services/api';

interface CategoryBreakdownChartProps {
  data: CategoryBreakdown;
}

const COLORS: Record<string, string> = {
  transport: '#3B82F6', // blue
  energy: '#F59E0B',    // yellow
  food: '#10B981'       // green
};

export default function CategoryBreakdownChart({ data }: CategoryBreakdownChartProps) {
  const { t } = useTranslation();

  const chartData = data.breakdown.map((item) => ({
    name: t(`activity.categories.${item.category}`),
    value: item.co2e_kg,
    percentage: item.percentage
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{t('dashboard.breakdown')}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ percentage }) => `${percentage.toFixed(1)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[data.breakdown[index].category]}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => `${value.toFixed(2)} kg CO2e`}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
```

**7. Trend Chart Component** (`frontend/src/components/features/footprint/TrendChart.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { FootprintTrend } from '@/services/api';

interface TrendChartProps {
  data: FootprintTrend;
}

export default function TrendChart({ data }: TrendChartProps) {
  const { t } = useTranslation();

  const chartData = data.data_points.map((point) => ({
    date: new Date(point.date).toLocaleDateString(),
    co2e: point.co2e_kg
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{t('dashboard.trend')}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis
            label={{ value: 'kg CO2e', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(2)} kg CO2e`}
          />
          <Line
            type="monotone"
            dataKey="co2e"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

**8. Update Dashboard Page** (`frontend/src/pages/DashboardPage.tsx`)

```typescript
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PeriodSelector from '@/components/features/footprint/PeriodSelector';
import SummaryCard from '@/components/features/footprint/SummaryCard';
import CategoryBreakdownChart from '@/components/features/footprint/CategoryBreakdownChart';
import TrendChart from '@/components/features/footprint/TrendChart';
import { useFootprintSummary, useFootprintBreakdown, useFootprintTrend } from '@/hooks/useFootprint';

export default function DashboardPage() {
  const { t } = useTranslation();
  const [period, setPeriod] = useState('month');

  const { data: summary, isLoading: summaryLoading } = useFootprintSummary(period);
  const { data: breakdown, isLoading: breakdownLoading } = useFootprintBreakdown(period);
  const { data: trend, isLoading: trendLoading } = useFootprintTrend(period);

  if (summaryLoading || breakdownLoading || trendLoading) {
    return <div className="text-center py-8">{t('common.loading')}</div>;
  }

  // Empty state
  if (summary && summary.activity_count === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🌱</div>
        <h2 className="text-2xl font-semibold mb-2">{t('dashboard.noData')}</h2>
        <p className="text-gray-600 mb-6">{t('dashboard.startTracking')}</p>
        <button className="btn btn-primary">+ {t('activity.log')}</button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('dashboard.title')}</h1>

      <PeriodSelector value={period} onChange={setPeriod} />

      <div className="mt-6 space-y-6">
        {summary && <SummaryCard data={summary} />}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {breakdown && <CategoryBreakdownChart data={breakdown} />}
          {trend && <TrendChart data={trend} />}
        </div>
      </div>
    </div>
  );
}
```

**9. Update i18n Files**

Add to `frontend/src/i18n/locales/en.json`:
```json
{
  "dashboard": {
    "activities": "Activities",
    "avgDaily": "Average Daily",
    "period": {
      "day": "Today",
      "week": "This Week",
      "month": "This Month",
      "year": "This Year",
      "all": "All Time"
    }
  }
}
```

## Implementation Steps

1. **Install Recharts**
   - Add recharts to frontend package.json
   - Run `npm install recharts @types/recharts`

2. **Create Aggregation Service**
   - Create `backend/src/domain/services/aggregation_service.py`
   - Implement `calculate_total_co2e()`, `calculate_breakdown_by_category()`, `calculate_daily_trend()`, `get_period_dates()`
   - Add unit tests

3. **Update Activity Repository**
   - Add `list_by_date_range()` to port
   - Implement in SupabaseActivityRepository
   - Add integration tests

4. **Create Footprint Summary Use Case**
   - Create `backend/src/domain/use_cases/get_footprint_summary.py`
   - Implement GetFootprintSummaryInput, FootprintSummary, GetFootprintSummaryUseCase
   - Add unit tests

5. **Create Footprint Breakdown Use Case**
   - Create `backend/src/domain/use_cases/get_footprint_breakdown.py`
   - Similar structure to summary use case
   - Add unit tests

6. **Create Footprint Trend Use Case**
   - Create `backend/src/domain/use_cases/get_footprint_trend.py`
   - Implement with daily aggregation
   - Add unit tests

7. **Create Footprint Schemas**
   - Create `backend/src/api/schemas/footprint.py`
   - Add FootprintSummaryResponse, CategoryBreakdownItem, FootprintBreakdownResponse, TrendDataPoint, FootprintTrendResponse

8. **Create Footprint Routes**
   - Create `backend/src/api/routes/footprint.py`
   - Add GET /summary, /breakdown, /trend endpoints
   - Register router in main app

9. **Create Use Case Dependencies**
   - Update `backend/src/api/dependencies/use_cases.py`
   - Add factory functions for footprint use cases

10. **Test Backend Endpoints**
    - Integration tests for all 3 endpoints
    - Test with user_id and session_id
    - Test all period values

11. **Add Footprint API Methods**
    - Update `frontend/src/services/api.ts`
    - Add getFootprintSummary(), getFootprintBreakdown(), getFootprintTrend()

12. **Create Footprint Hook**
    - Create `frontend/src/hooks/useFootprint.ts`
    - Add useFootprintSummary, useFootprintBreakdown, useFootprintTrend hooks

13. **Create Period Selector Component**
    - Create `frontend/src/components/features/footprint/PeriodSelector.tsx`
    - Implement tab navigation
    - Add responsive styling

14. **Create Summary Card Component**
    - Create `frontend/src/components/features/footprint/SummaryCard.tsx`
    - Display total, count, change percentage, average
    - Add color coding for change

15. **Create Category Breakdown Chart**
    - Create `frontend/src/components/features/footprint/CategoryBreakdownChart.tsx`
    - Implement Recharts PieChart
    - Add color coding, legend, tooltip

16. **Create Trend Chart Component**
    - Create `frontend/src/components/features/footprint/TrendChart.tsx`
    - Implement Recharts LineChart
    - Add responsive design

17. **Update Dashboard Page**
    - Modify `frontend/src/pages/DashboardPage.tsx`
    - Integrate all new components
    - Add empty state
    - Add loading states

18. **Update i18n Files**
    - Add dashboard-specific translations
    - Update EN and ES locales

19. **Add Component Tests**
    - Test PeriodSelector selection
    - Test SummaryCard rendering
    - Test charts with mock data
    - Test empty state

20. **Add E2E Tests**
    - Test full dashboard flow
    - Test period switching
    - Test responsive design

21. **Manual Testing**
    - Create activities spanning multiple weeks
    - Test all period selectors
    - Verify calculations match
    - Test on mobile viewport

22. **Performance Optimization**
    - Add React.memo to chart components
    - Optimize query caching with React Query
    - Test with large datasets (100+ activities)

23. **Update Documentation**
    - Add dashboard section to README
    - Document aggregation logic
    - Add screenshots

## Test Requirements

### Backend Tests

**Unit Tests:**
- `test_aggregation_service_calculate_total()` - Sums CO2e correctly
- `test_aggregation_service_breakdown()` - Groups by category
- `test_aggregation_service_daily_trend()` - Fills missing dates with 0
- `test_get_period_dates_month()` - Returns first and last day of month
- `test_footprint_summary_use_case()` - Returns correct summary
- `test_footprint_breakdown_use_case()` - Returns category breakdown
- `test_footprint_trend_use_case()` - Returns time series data

**Integration Tests:**
- `test_get_summary_endpoint()` - Returns 200 with summary
- `test_get_breakdown_endpoint()` - Returns 200 with breakdown
- `test_get_trend_endpoint()` - Returns 200 with trend data
- `test_summary_with_no_activities()` - Returns zeros
- `test_summary_filters_by_user_id()` - Only returns user's activities
- `test_summary_filters_by_session_id()` - Only returns session's activities

### Frontend Tests

**Component Tests:**
- `PeriodSelector.test.tsx` - Renders all periods, calls onChange
- `SummaryCard.test.tsx` - Displays all metrics, formats numbers
- `CategoryBreakdownChart.test.tsx` - Renders pie chart with correct data
- `TrendChart.test.tsx` - Renders line chart with correct data
- `DashboardPage.test.tsx` - Shows empty state when no activities

**E2E Tests:**
- `dashboard.spec.ts` - Full dashboard flow with period switching
- `dashboard-calculations.spec.ts` - Verify calculations match backend

## Definition of Done

- [ ] All 3 backend endpoints return correct data
- [ ] Period selector switches between all views
- [ ] Summary card shows total, count, change, average
- [ ] Pie chart displays category breakdown
- [ ] Line chart shows trend over time
- [ ] Empty state displayed when no activities
- [ ] All charts are responsive (mobile/tablet/desktop)
- [ ] Data updates automatically when activity logged
- [ ] Loading states displayed during fetch
- [ ] User-specific data shown if authenticated
- [ ] All backend tests pass (13 new tests)
- [ ] All frontend tests pass (5 component + 2 E2E tests)
- [ ] No TypeScript or Python errors
- [ ] Documentation updated

## Out of Scope

- Custom date range picker (use predefined periods only)
- Export charts as images (future: CT-003.1)
- Compare multiple time periods side-by-side (future: CT-003.2)
- Weekly/monthly aggregation for year view (use daily only)
- Activity type breakdown (show category only)
- Filter by specific categories (future: CT-003.3)

## Related

- **Dependencies:** CT-000, CT-001, CT-002 (optional)
- **Enables:** CT-005 (Regional Comparison uses same aggregation service)
- **Architecture:** Uses AggregationService in domain layer
