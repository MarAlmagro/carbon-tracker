# Feature: Regional Comparison

## Metadata
- **ID**: CT-005
- **Priority**: MEDIUM
- **Estimated Effort**: 6-8 hours
- **Dependencies**: CT-000 (Project Foundation), CT-001 (Transport Logging), CT-003 (Dashboard)

## Summary
Enable users to compare their carbon footprint against regional averages, showing percentiles, insights, and recommendations based on geographic location.

## User Story
As a **Carbon Tracker user**, I want to **compare my footprint to regional and global averages** so that **I can understand where I stand and identify opportunities for improvement**.

## Acceptance Criteria
- [ ] AC1: Users can select their region from a predefined list
- [ ] AC2: Comparison page shows user's footprint vs regional average
- [ ] AC3: Percentile ranking displayed (e.g., "Top 25%" or "Below average")
- [ ] AC4: Visual chart compares user vs regional vs global averages
- [ ] AC5: Insights section explains what the comparison means
- [ ] AC6: Region preference saved for authenticated users
- [ ] AC7: Auto-detect region from browser locale (optional fallback)
- [ ] AC8: Regional data for at least 20 regions (continents + major countries)
- [ ] AC9: Comparison calculations use same time period as dashboard
- [ ] AC10: All strings in i18n files (EN/ES)

## API Contract

### 1. Get Regional Averages
**Endpoint:** `GET /api/v1/comparison/regions`

**Response (200 OK):**
```json
{
  "regions": [
    {
      "code": "na",
      "name": "North America",
      "average_annual_co2e_kg": 16000,
      "population": 580000000
    },
    {
      "code": "eu",
      "name": "Europe",
      "average_annual_co2e_kg": 7000,
      "population": 750000000
    },
    {
      "code": "world",
      "name": "Global Average",
      "average_annual_co2e_kg": 4800,
      "population": 8000000000
    }
  ]
}
```

### 2. Compare User to Region
**Endpoint:** `GET /api/v1/comparison/compare`

**Query Parameters:**
- `region_code` (required): Region to compare against (e.g., "na", "eu", "world")
- `period` (optional): Time period (`month` | `year`, default: `year`)

**Request Headers:**
```http
Authorization: Bearer eyJhbGc... (optional)
X-Session-ID: abc-123
```

**Response (200 OK):**
```json
{
  "user_footprint": {
    "period": "year",
    "total_co2e_kg": 8500,
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "activity_count": 145
  },
  "regional_average": {
    "region_code": "na",
    "region_name": "North America",
    "average_annual_co2e_kg": 16000
  },
  "comparison": {
    "difference_kg": -7500,
    "difference_percentage": -46.88,
    "percentile": 25,
    "rating": "excellent",
    "message": "Your footprint is 47% below the North American average. Great job!"
  },
  "breakdown": {
    "user_by_category": {
      "transport": 5100,
      "energy": 2400,
      "food": 1000
    },
    "regional_avg_by_category": {
      "transport": 9600,
      "energy": 4800,
      "food": 1600
    }
  }
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid region code: xyz"
}
```

## Regional Data Structure

### Regional Averages (Static JSON)

```json
[
  {
    "code": "world",
    "name": "Global Average",
    "average_annual_co2e_kg": 4800,
    "breakdown": {
      "transport": 1440,
      "energy": 2400,
      "food": 960
    },
    "source": "Global Carbon Project 2023"
  },
  {
    "code": "na",
    "name": "North America",
    "average_annual_co2e_kg": 16000,
    "breakdown": {
      "transport": 9600,
      "energy": 4800,
      "food": 1600
    },
    "source": "EPA 2023"
  },
  {
    "code": "eu",
    "name": "Europe",
    "average_annual_co2e_kg": 7000,
    "breakdown": {
      "transport": 2800,
      "energy": 3150,
      "food": 1050
    },
    "source": "European Environment Agency 2023"
  },
  {
    "code": "asia",
    "name": "Asia",
    "average_annual_co2e_kg": 3500,
    "breakdown": {
      "transport": 1050,
      "energy": 1750,
      "food": 700
    },
    "source": "UNEP 2023"
  },
  {
    "code": "sa",
    "name": "South America",
    "average_annual_co2e_kg": 2500,
    "breakdown": {
      "transport": 750,
      "energy": 1250,
      "food": 500
    },
    "source": "IPCC 2023"
  },
  {
    "code": "af",
    "name": "Africa",
    "average_annual_co2e_kg": 1000,
    "breakdown": {
      "transport": 300,
      "energy": 500,
      "food": 200
    },
    "source": "UNEP 2023"
  },
  {
    "code": "oc",
    "name": "Oceania",
    "average_annual_co2e_kg": 12000,
    "breakdown": {
      "transport": 6000,
      "energy": 4800,
      "food": 1200
    },
    "source": "Australian Government 2023"
  },
  {
    "code": "us",
    "name": "United States",
    "average_annual_co2e_kg": 17000,
    "breakdown": {
      "transport": 10200,
      "energy": 5100,
      "food": 1700
    },
    "source": "EPA 2023"
  },
  {
    "code": "uk",
    "name": "United Kingdom",
    "average_annual_co2e_kg": 5500,
    "breakdown": {
      "transport": 2200,
      "energy": 2475,
      "food": 825
    },
    "source": "UK BEIS 2023"
  },
  {
    "code": "cn",
    "name": "China",
    "average_annual_co2e_kg": 7500,
    "breakdown": {
      "transport": 2250,
      "energy": 3750,
      "food": 1500
    },
    "source": "China MEE 2023"
  }
  // ... more regions
]
```

## Rating System

Percentile ranges and ratings:
- **0-25%**: "Excellent" - Well below average
- **25-50%**: "Good" - Below average
- **50-75%**: "Average" - Around average
- **75-90%**: "Above Average" - Higher than most
- **90-100%**: "High" - Significantly above average

## UI/UX Requirements

### Comparison Page Layout

```
┌─────────────────────────────────────────────────┐
│  📊 Regional Comparison                         │
├─────────────────────────────────────────────────┤
│  Region: [North America ▼]   Period: [Year ▼]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  YOUR FOOTPRINT                         │   │
│  │  8,500 kg CO2e                         │   │
│  │                                         │   │
│  │  REGIONAL AVERAGE                       │   │
│  │  16,000 kg CO2e                        │   │
│  │                                         │   │
│  │  YOU'RE 47% BELOW AVERAGE! ⭐          │   │
│  │  Percentile: Top 25%                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  BAR CHART                              │   │
│  │  Your: ████████░░░░░░░░░░  8,500 kg    │   │
│  │  Avg:  ████████████████████ 16,000 kg  │   │
│  │  World: ████████  4,800 kg              │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  BREAKDOWN COMPARISON                   │   │
│  │  Category    You    Regional  Diff      │   │
│  │  Transport   5,100  9,600     -47%     │   │
│  │  Energy      2,400  4,800     -50%     │   │
│  │  Food        1,000  1,600     -38%     │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  INSIGHTS & RECOMMENDATIONS             │   │
│  │  • Your transport emissions are...      │   │
│  │  • Consider reducing energy usage...    │   │
│  │  • Your food choices are excellent...   │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Components

#### 1. Region Selector Dropdown
- Searchable dropdown
- Shows region name (e.g., "North America")
- Default: Auto-detected or user's saved preference

#### 2. Period Selector
- Month or Year options
- Default: Year

#### 3. Comparison Summary Card
- User's total footprint (large number)
- Regional average (smaller, below)
- Difference percentage (color-coded: green if below, red if above)
- Percentile ranking with icon
- Rating badge (Excellent, Good, Average, etc.)

#### 4. Comparison Bar Chart
- Horizontal bars comparing:
  - User's footprint
  - Regional average
  - Global average
- Bars color-coded
- Values labeled at end of bars

#### 5. Category Breakdown Table
- 3 rows: Transport, Energy, Food
- 4 columns: Category, User, Regional Avg, Difference %
- Difference color-coded

#### 6. Insights Section
- 3-5 bullet points with actionable insights
- Based on comparison results
- Positive reinforcement for categories below average
- Suggestions for categories above average

### Empty State
If user has no activities:
```
┌─────────────────────────────────────────────────┐
│                                                 │
│           📊                                    │
│                                                 │
│    Start tracking to see your comparison       │
│                                                 │
│    [+ Log Activity]                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Technical Design

### What's Already Done (CT-000/CT-001/CT-003)

#### Backend
- ✓ AggregationService with calculate_total_co2e() and calculate_breakdown_by_category()
- ✓ GetFootprintSummaryUseCase (can reuse for comparison period)
- ✓ Activity repository with list_by_date_range()
- ✓ JSON-based configuration support

#### Frontend
- ✓ Dashboard with period selector
- ✓ useFootprintSummary hook
- ✓ SummaryCard component structure
- ✓ i18n support

### What Needs to Be Built

#### Backend (NEW)

**1. Regional Data File** (`backend/src/infrastructure/data/regional_averages.json` - NEW)

See "Regional Data Structure" section above for full JSON structure.

**2. Region Entity** (`backend/src/domain/entities/region.py` - NEW)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RegionalAverage:
    """Regional carbon footprint average."""
    code: str
    name: str
    average_annual_co2e_kg: float
    breakdown: dict[str, float]  # category -> kg CO2e
    source: str
```

**3. Region Data Provider Port** (`backend/src/domain/ports/region_data_provider.py` - NEW)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.region import RegionalAverage

class RegionDataProvider(ABC):
    """Port for regional data access."""

    @abstractmethod
    async def list_all(self) -> List[RegionalAverage]:
        """List all available regions."""
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[RegionalAverage]:
        """Get regional average by code."""
        pass
```

**4. JSON Region Data Provider** (`backend/src/infrastructure/adapters/json_region_data_provider.py` - NEW)

```python
import json
from pathlib import Path
from typing import List, Optional
from domain.entities.region import RegionalAverage
from domain.ports.region_data_provider import RegionDataProvider

class JSONRegionDataProvider(RegionDataProvider):
    """Region data provider backed by JSON file."""

    def __init__(self, data_file: Path):
        self._data_file = data_file
        self._regions: List[RegionalAverage] = []
        self._load_data()

    def _load_data(self):
        """Load regional data from JSON."""
        with open(self._data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._regions = [
                RegionalAverage(
                    code=row['code'],
                    name=row['name'],
                    average_annual_co2e_kg=row['average_annual_co2e_kg'],
                    breakdown=row['breakdown'],
                    source=row['source']
                )
                for row in data
            ]

    async def list_all(self) -> List[RegionalAverage]:
        """List all regions."""
        return self._regions

    async def get_by_code(self, code: str) -> Optional[RegionalAverage]:
        """Get region by code."""
        for region in self._regions:
            if region.code == code.lower():
                return region
        return None
```

**5. Comparison Service** (`backend/src/domain/services/comparison_service.py` - NEW)

```python
from typing import Tuple

class ComparisonService:
    """Service for calculating comparison metrics."""

    @staticmethod
    def calculate_difference(
        user_value: float,
        regional_avg: float
    ) -> Tuple[float, float]:
        """
        Calculate absolute and percentage difference.
        Returns: (difference_kg, difference_percentage)
        Negative means user is below average.
        """
        diff_kg = user_value - regional_avg
        diff_pct = (diff_kg / regional_avg * 100) if regional_avg > 0 else 0.0
        return round(diff_kg, 2), round(diff_pct, 2)

    @staticmethod
    def calculate_percentile(
        user_value: float,
        regional_avg: float
    ) -> int:
        """
        Estimate percentile based on user value vs regional average.
        Simplified calculation assuming normal distribution.
        """
        ratio = user_value / regional_avg if regional_avg > 0 else 1.0

        # Simplified percentile mapping
        if ratio <= 0.5:
            return 10
        elif ratio <= 0.75:
            return 25
        elif ratio <= 0.9:
            return 40
        elif ratio <= 1.1:
            return 50
        elif ratio <= 1.25:
            return 60
        elif ratio <= 1.5:
            return 75
        elif ratio <= 2.0:
            return 90
        else:
            return 95

    @staticmethod
    def get_rating(percentile: int) -> str:
        """Get rating based on percentile."""
        if percentile <= 25:
            return "excellent"
        elif percentile <= 50:
            return "good"
        elif percentile <= 75:
            return "average"
        elif percentile <= 90:
            return "above_average"
        else:
            return "high"

    @staticmethod
    def generate_insights(
        user_breakdown: dict[str, float],
        regional_breakdown: dict[str, float]
    ) -> list[str]:
        """Generate insights comparing user to regional breakdown."""
        insights = []

        for category in ["transport", "energy", "food"]:
            user_val = user_breakdown.get(category, 0)
            regional_val = regional_breakdown.get(category, 0)

            if regional_val > 0:
                diff_pct = ((user_val - regional_val) / regional_val) * 100

                if diff_pct < -30:
                    insights.append(
                        f"Your {category} emissions are excellent - "
                        f"{abs(diff_pct):.0f}% below average!"
                    )
                elif diff_pct < -10:
                    insights.append(
                        f"Your {category} emissions are below average. Great work!"
                    )
                elif diff_pct > 30:
                    insights.append(
                        f"Your {category} emissions are {diff_pct:.0f}% above average. "
                        f"Consider ways to reduce them."
                    )

        return insights[:5]  # Max 5 insights
```

**6. Compare to Region Use Case** (`backend/src/domain/use_cases/compare_to_region.py` - NEW)

```python
from typing import Optional
from uuid import UUID
from datetime import date
from domain.ports.activity_repository import ActivityRepository
from domain.ports.region_data_provider import RegionDataProvider
from domain.services.aggregation_service import AggregationService
from domain.services.comparison_service import ComparisonService

class CompareToRegionInput:
    """Input for regional comparison."""
    def __init__(
        self,
        user_id: Optional[UUID],
        session_id: Optional[str],
        region_code: str,
        period: str = "year"
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.region_code = region_code
        self.period = period

class ComparisonResult:
    """Comparison output."""
    def __init__(
        self,
        user_footprint: dict,
        regional_average: dict,
        comparison: dict,
        breakdown: dict
    ):
        self.user_footprint = user_footprint
        self.regional_average = regional_average
        self.comparison = comparison
        self.breakdown = breakdown

class CompareToRegionUseCase:
    """Compare user's footprint to regional average."""

    def __init__(
        self,
        activity_repo: ActivityRepository,
        region_provider: RegionDataProvider,
        aggregation_service: AggregationService,
        comparison_service: ComparisonService
    ):
        self._activity_repo = activity_repo
        self._region_provider = region_provider
        self._aggregation_service = aggregation_service
        self._comparison_service = comparison_service

    async def execute(self, input_data: CompareToRegionInput) -> ComparisonResult:
        """Execute comparison."""
        # Get regional data
        region = await self._region_provider.get_by_code(input_data.region_code)
        if not region:
            raise ValueError(f"Invalid region code: {input_data.region_code}")

        # Calculate user's footprint for period
        start_date, end_date = self._aggregation_service.get_period_dates(
            input_data.period
        )

        activities = await self._activity_repo.list_by_date_range(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            start_date=start_date,
            end_date=end_date
        )

        user_total = self._aggregation_service.calculate_total_co2e(activities)
        user_breakdown = self._aggregation_service.calculate_breakdown_by_category(
            activities
        )

        # Calculate comparison metrics
        diff_kg, diff_pct = self._comparison_service.calculate_difference(
            user_total,
            region.average_annual_co2e_kg
        )

        percentile = self._comparison_service.calculate_percentile(
            user_total,
            region.average_annual_co2e_kg
        )

        rating = self._comparison_service.get_rating(percentile)

        # Generate insights
        insights = self._comparison_service.generate_insights(
            user_breakdown,
            region.breakdown
        )

        return ComparisonResult(
            user_footprint={
                "period": input_data.period,
                "total_co2e_kg": user_total,
                "start_date": start_date,
                "end_date": end_date,
                "activity_count": len(activities)
            },
            regional_average={
                "region_code": region.code,
                "region_name": region.name,
                "average_annual_co2e_kg": region.average_annual_co2e_kg
            },
            comparison={
                "difference_kg": diff_kg,
                "difference_percentage": diff_pct,
                "percentile": percentile,
                "rating": rating,
                "insights": insights
            },
            breakdown={
                "user_by_category": user_breakdown,
                "regional_avg_by_category": region.breakdown
            }
        )
```

**7. Comparison Schemas** (`backend/src/api/schemas/comparison.py` - NEW)

```python
from pydantic import BaseModel, Field
from datetime import date

class RegionInfo(BaseModel):
    """Region information."""
    code: str
    name: str
    average_annual_co2e_kg: float

class RegionListResponse(BaseModel):
    """List of available regions."""
    regions: list[RegionInfo]

class UserFootprintInfo(BaseModel):
    """User footprint information."""
    period: str
    total_co2e_kg: float
    start_date: date
    end_date: date
    activity_count: int

class RegionalAverageInfo(BaseModel):
    """Regional average information."""
    region_code: str
    region_name: str
    average_annual_co2e_kg: float

class ComparisonMetrics(BaseModel):
    """Comparison metrics."""
    difference_kg: float
    difference_percentage: float
    percentile: int = Field(ge=0, le=100)
    rating: str
    insights: list[str]

class BreakdownComparison(BaseModel):
    """Category breakdown comparison."""
    user_by_category: dict[str, float]
    regional_avg_by_category: dict[str, float]

class ComparisonResponse(BaseModel):
    """Regional comparison response."""
    user_footprint: UserFootprintInfo
    regional_average: RegionalAverageInfo
    comparison: ComparisonMetrics
    breakdown: BreakdownComparison
```

**8. Comparison Routes** (`backend/src/api/routes/comparison.py` - NEW)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from domain.entities.user import User
from domain.use_cases.compare_to_region import CompareToRegionUseCase, CompareToRegionInput
from domain.ports.region_data_provider import RegionDataProvider
from api.dependencies.auth import get_optional_user
from api.dependencies.session import get_session_id
from api.dependencies.use_cases import get_compare_to_region_use_case
from api.dependencies.repositories import get_region_data_provider
from api.schemas.comparison import ComparisonResponse, RegionListResponse, RegionInfo

router = APIRouter(prefix="/comparison", tags=["comparison"])

@router.get("/regions", response_model=RegionListResponse)
async def list_regions(
    region_provider: RegionDataProvider = Depends(get_region_data_provider)
) -> RegionListResponse:
    """List all available regions."""
    regions = await region_provider.list_all()

    return RegionListResponse(
        regions=[
            RegionInfo(
                code=region.code,
                name=region.name,
                average_annual_co2e_kg=region.average_annual_co2e_kg
            )
            for region in regions
        ]
    )

@router.get("/compare", response_model=ComparisonResponse)
async def compare_to_region(
    region_code: str = Query(..., description="Region code (e.g., 'na', 'eu')"),
    period: str = Query("year", regex="^(month|year)$"),
    user: Optional[User] = Depends(get_optional_user),
    session_id: str = Depends(get_session_id),
    use_case: CompareToRegionUseCase = Depends(get_compare_to_region_use_case)
) -> ComparisonResponse:
    """Compare user's footprint to regional average."""
    try:
        input_data = CompareToRegionInput(
            user_id=user.id if user else None,
            session_id=session_id if not user else None,
            region_code=region_code,
            period=period
        )

        result = await use_case.execute(input_data)

        return ComparisonResponse(
            user_footprint=UserFootprintInfo(**result.user_footprint),
            regional_average=RegionalAverageInfo(**result.regional_average),
            comparison=ComparisonMetrics(**result.comparison),
            breakdown=BreakdownComparison(**result.breakdown)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**9. Update Dependencies** (`backend/src/api/dependencies/repositories.py`)

```python
from pathlib import Path
from infrastructure.adapters.json_region_data_provider import JSONRegionDataProvider

def get_region_data_provider() -> RegionDataProvider:
    data_file = Path(__file__).parents[3] / "infrastructure" / "data" / "regional_averages.json"
    return JSONRegionDataProvider(data_file)
```

**10. Register Router** (`backend/src/api/main.py`)

```python
from api.routes import comparison

app.include_router(comparison.router, prefix="/api/v1")
```

#### Frontend (NEW)

**1. Comparison API Methods** (`frontend/src/services/api.ts`)

```typescript
export interface Region {
  code: string;
  name: string;
  average_annual_co2e_kg: number;
}

export interface ComparisonResult {
  user_footprint: {
    period: string;
    total_co2e_kg: number;
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
  // ... existing methods ...

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
```

**2. Comparison Hook** (`frontend/src/hooks/useComparison.ts` - NEW)

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';

export function useRegions() {
  return useQuery({
    queryKey: ['regions'],
    queryFn: () => apiClient.getRegions(),
    staleTime: 60 * 60 * 1000 // 1 hour
  });
}

export function useComparison(regionCode: string, period: string) {
  return useQuery({
    queryKey: ['comparison', regionCode, period],
    queryFn: () => apiClient.compareToRegion(regionCode, period),
    enabled: !!regionCode
  });
}
```

**3. Comparison Page** (`frontend/src/pages/ComparisonPage.tsx` - NEW)

```typescript
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRegions, useComparison } from '@/hooks/useComparison';
import ComparisonSummary from '@/components/features/comparison/ComparisonSummary';
import ComparisonChart from '@/components/features/comparison/ComparisonChart';
import BreakdownTable from '@/components/features/comparison/BreakdownTable';
import InsightsSection from '@/components/features/comparison/InsightsSection';

export default function ComparisonPage() {
  const { t } = useTranslation();
  const [selectedRegion, setSelectedRegion] = useState('world');
  const [selectedPeriod, setSelectedPeriod] = useState('year');

  const { data: regions, isLoading: regionsLoading } = useRegions();
  const { data: comparison, isLoading: comparisonLoading } = useComparison(
    selectedRegion,
    selectedPeriod
  );

  if (regionsLoading) {
    return <div className="text-center py-8">{t('common.loading')}</div>;
  }

  // Empty state
  if (comparison && comparison.user_footprint.activity_count === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📊</div>
        <h2 className="text-2xl font-semibold mb-2">
          {t('comparison.noData')}
        </h2>
        <p className="text-gray-600 mb-6">{t('comparison.startTracking')}</p>
        <button className="btn btn-primary">+ {t('activity.log')}</button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('comparison.title')}</h1>

      <div className="flex gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">
            {t('comparison.region')}
          </label>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            {regions?.map((region) => (
              <option key={region.code} value={region.code}>
                {region.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {t('comparison.period')}
          </label>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="month">{t('dashboard.period.month')}</option>
            <option value="year">{t('dashboard.period.year')}</option>
          </select>
        </div>
      </div>

      {comparisonLoading ? (
        <div className="text-center py-8">{t('common.loading')}</div>
      ) : comparison ? (
        <div className="space-y-6">
          <ComparisonSummary data={comparison} />
          <ComparisonChart data={comparison} />
          <BreakdownTable data={comparison.breakdown} />
          <InsightsSection insights={comparison.comparison.insights} />
        </div>
      ) : null}
    </div>
  );
}
```

**4. Comparison Summary Component** (`frontend/src/components/features/comparison/ComparisonSummary.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';
import { ComparisonResult } from '@/services/api';

interface ComparisonSummaryProps {
  data: ComparisonResult;
}

export default function ComparisonSummary({ data }: ComparisonSummaryProps) {
  const { t } = useTranslation();

  const ratingColors: Record<string, string> = {
    excellent: 'bg-green-100 text-green-800',
    good: 'bg-blue-100 text-blue-800',
    average: 'bg-yellow-100 text-yellow-800',
    above_average: 'bg-orange-100 text-orange-800',
    high: 'bg-red-100 text-red-800'
  };

  const ratingColor = ratingColors[data.comparison.rating] || 'bg-gray-100';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-2">
            {t('comparison.yourFootprint')}
          </h3>
          <div className="text-4xl font-bold text-gray-900">
            {data.user_footprint.total_co2e_kg.toFixed(0)}
            <span className="text-xl text-gray-500 ml-2">kg CO2e</span>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-2">
            {t('comparison.regionalAverage')}
          </h3>
          <div className="text-4xl font-bold text-gray-400">
            {data.regional_average.average_annual_co2e_kg.toFixed(0)}
            <span className="text-xl text-gray-400 ml-2">kg CO2e</span>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${ratingColor}`}
            >
              {t(`comparison.rating.${data.comparison.rating}`)}
            </span>
            <div className="mt-2 text-2xl font-bold">
              {data.comparison.difference_percentage > 0 ? '+' : ''}
              {data.comparison.difference_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">
              {t('comparison.percentile', {
                percentile: data.comparison.percentile
              })}
            </div>
          </div>

          <div className="text-6xl">
            {data.comparison.rating === 'excellent' ? '⭐' : '📊'}
          </div>
        </div>
      </div>
    </div>
  );
}
```

**5. Other Components** (ComparisonChart, BreakdownTable, InsightsSection)

Similar implementations with Recharts and table components.

**6. Add i18n Translations**

Update `frontend/src/i18n/locales/en.json`:
```json
{
  "comparison": {
    "title": "Regional Comparison",
    "region": "Region",
    "period": "Period",
    "yourFootprint": "Your Footprint",
    "regionalAverage": "Regional Average",
    "percentile": "Percentile: {percentile}%",
    "rating": {
      "excellent": "Excellent",
      "good": "Good",
      "average": "Average",
      "above_average": "Above Average",
      "high": "High"
    },
    "noData": "No data to compare",
    "startTracking": "Start tracking to compare your footprint"
  }
}
```

## Implementation Steps

1-23. [Similar detailed steps as other plans, covering backend creation of regional data, services, use cases, routes, and frontend components]

## Test Requirements

Similar comprehensive testing structure as other features.

## Definition of Done

- [ ] Regional averages loaded for 20+ regions
- [ ] Comparison endpoint returns correct calculations
- [ ] Frontend displays comparison with charts
- [ ] Percentile and rating calculated correctly
- [ ] Insights generated based on breakdown
- [ ] All tests pass
- [ ] Documentation updated

## Out of Scope

- User-submitted regional data (future: CT-005.1)
- Time-series comparison (track improvement over time) (future: CT-005.2)
- Social comparison (compare to friends) (future: CT-005.3)
- Goal setting based on regional targets (future: CT-005.4)

## Related

- **Dependencies:** CT-000, CT-001, CT-003
- **Uses:** AggregationService from CT-003
- **Enables:** Personalized recommendations (future)
