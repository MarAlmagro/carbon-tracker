"""Airport and flight API schemas."""

from pydantic import BaseModel, Field


class AirportResponse(BaseModel):
    """Airport response schema."""

    iata_code: str = Field(..., min_length=3, max_length=3, description="3-letter IATA code")
    name: str = Field(..., description="Airport name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class AirportSearchResponse(BaseModel):
    """Airport search results schema."""

    results: list[AirportResponse] = Field(..., description="List of matching airports")


class FlightCalculationRequest(BaseModel):
    """Request schema for flight calculation."""

    origin_iata: str = Field(..., min_length=3, max_length=3, description="Origin airport IATA code")
    destination_iata: str = Field(..., min_length=3, max_length=3, description="Destination airport IATA code")


class FlightCalculationResponse(BaseModel):
    """Response schema for flight calculation."""

    origin_iata: str = Field(..., description="Origin airport IATA code")
    destination_iata: str = Field(..., description="Destination airport IATA code")
    distance_km: float = Field(..., description="Great-circle distance in kilometers")
    flight_type: str = Field(..., description="Flight type (e.g., flight_domestic_short)")
    is_domestic: bool = Field(..., description="Whether flight is domestic")
    haul_type: str = Field(..., description="Haul type (short, medium, or long)")
