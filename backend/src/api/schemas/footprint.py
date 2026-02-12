"""Footprint API response schemas."""

from datetime import date

from pydantic import BaseModel, Field


class FootprintSummaryResponse(BaseModel):
    """Footprint summary response.

    Attributes:
        period: Time period used
        start_date: Start of period
        end_date: End of period
        total_co2e_kg: Total emissions in kg CO2e
        activity_count: Number of activities
        previous_period_co2e_kg: Previous period total
        change_percentage: Percentage change vs previous period
        average_daily_co2e_kg: Average daily emissions
    """

    period: str
    start_date: date
    end_date: date
    total_co2e_kg: float = Field(ge=0)
    activity_count: int = Field(ge=0)
    previous_period_co2e_kg: float = Field(ge=0)
    change_percentage: float
    average_daily_co2e_kg: float = Field(ge=0)


class CategoryBreakdownItem(BaseModel):
    """Single category in breakdown.

    Attributes:
        category: Category name
        co2e_kg: Total emissions for category
        percentage: Percentage of total
        activity_count: Number of activities
    """

    category: str
    co2e_kg: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    activity_count: int = Field(ge=0)


class FootprintBreakdownResponse(BaseModel):
    """Footprint breakdown by category.

    Attributes:
        period: Time period used
        breakdown: List of category breakdowns
        total_co2e_kg: Total emissions
    """

    period: str
    breakdown: list[CategoryBreakdownItem]
    total_co2e_kg: float = Field(ge=0)


class TrendDataPoint(BaseModel):
    """Single point in trend chart.

    Attributes:
        date: Date of data point
        co2e_kg: Emissions for this date
        activity_count: Number of activities
    """

    date: date
    co2e_kg: float = Field(ge=0)
    activity_count: int = Field(ge=0)


class FootprintTrendResponse(BaseModel):
    """Footprint trend over time.

    Attributes:
        period: Time period used
        granularity: Data point granularity
        data_points: List of trend data points
        total_co2e_kg: Total emissions
        average_co2e_kg: Average per data point
    """

    period: str
    granularity: str
    data_points: list[TrendDataPoint]
    total_co2e_kg: float = Field(ge=0)
    average_co2e_kg: float = Field(ge=0)
