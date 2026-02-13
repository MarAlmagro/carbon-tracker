"""API schemas for comparison endpoints."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class RegionInfo(BaseModel):
    """Basic region information.

    Used in region listing responses.
    """

    code: str = Field(..., description="Region code (e.g., 'us', 'eu', 'world')")
    name: str = Field(..., description="Human-readable region name")
    average_annual_co2e_kg: float = Field(
        ..., description="Average annual CO2e in kg", gt=0
    )


class RegionListResponse(BaseModel):
    """Response for listing available regions."""

    regions: list[RegionInfo] = Field(..., description="List of available regions")


class UserFootprintInfo(BaseModel):
    """User's footprint information for the comparison period."""

    period: str = Field(..., description="Time period (month/year)")
    total_co2e_kg: float = Field(..., description="Total CO2e in kg", ge=0)
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    activity_count: int = Field(..., description="Number of activities", ge=0)


class RegionalAverageInfo(BaseModel):
    """Regional average information."""

    region_code: str = Field(..., description="Region code")
    region_name: str = Field(..., description="Region name")
    average_annual_co2e_kg: float = Field(
        ..., description="Regional average annual CO2e in kg"
    )


class ComparisonMetrics(BaseModel):
    """Comparison metrics and insights."""

    difference_kg: float = Field(..., description="Absolute difference in kg CO2e")
    difference_percentage: float = Field(
        ..., description="Percentage difference (negative is better)"
    )
    percentile: int = Field(..., description="User's percentile (0-100)", ge=0, le=100)
    rating: str = Field(
        ..., description="Rating (excellent/good/average/above_average/high)"
    )
    insights: list[str] = Field(..., description="Generated insights and tips")


class BreakdownComparison(BaseModel):
    """Category-level breakdown comparison."""

    user_by_category: dict[str, float] = Field(
        ..., description="User's CO2e by category"
    )
    regional_avg_by_category: dict[str, float] = Field(
        ..., description="Regional average by category"
    )


class ComparisonResponse(BaseModel):
    """Complete regional comparison response."""

    user_footprint: UserFootprintInfo
    regional_average: RegionalAverageInfo
    comparison: ComparisonMetrics
    breakdown: BreakdownComparison

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_footprint": {
                    "period": "year",
                    "total_co2e_kg": 8500.0,
                    "start_date": "2026-01-01",
                    "end_date": "2026-12-31",
                    "activity_count": 145,
                },
                "regional_average": {
                    "region_code": "na",
                    "region_name": "North America",
                    "average_annual_co2e_kg": 16000.0,
                },
                "comparison": {
                    "difference_kg": -7500.0,
                    "difference_percentage": -46.88,
                    "percentile": 25,
                    "rating": "excellent",
                    "insights": [
                        "Your transport emissions are excellent - 47% below average!",
                        "Your energy emissions are below average. Great work!",
                    ],
                },
                "breakdown": {
                    "user_by_category": {
                        "transport": 5100.0,
                        "energy": 2400.0,
                        "food": 1000.0,
                    },
                    "regional_avg_by_category": {
                        "transport": 9600.0,
                        "energy": 4800.0,
                        "food": 1600.0,
                    },
                },
            }
        }
    )
