"""Flight calculation endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.use_cases import get_calculate_flight_use_case
from api.schemas.airport import FlightCalculationRequest, FlightCalculationResponse
from domain.use_cases.calculate_flight import (
    CalculateFlightInput,
    CalculateFlightUseCase,
)

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/calculate", response_model=FlightCalculationResponse)
async def calculate_flight(
    request: FlightCalculationRequest,
    use_case: CalculateFlightUseCase = Depends(get_calculate_flight_use_case),
) -> FlightCalculationResponse:
    """
    Calculate flight distance and determine flight type.

    - **origin_iata**: Origin airport IATA code (3 letters)
    - **destination_iata**: Destination airport IATA code (3 letters)

    Returns:
    - Distance in kilometers (great-circle distance)
    - Flight type (e.g., "flight_domestic_short", "flight_international_long")
    - Whether flight is domestic
    - Haul type (short, medium, or long)

    Raises:
    - **400**: If airport not found
    """
    try:
        input_data = CalculateFlightInput(
            origin_iata=request.origin_iata.upper(),
            destination_iata=request.destination_iata.upper(),
        )

        result = await use_case.execute(input_data)

        return FlightCalculationResponse(
            origin_iata=result.origin_iata,
            destination_iata=result.destination_iata,
            distance_km=result.distance_km,
            flight_type=result.flight_type,
            is_domestic=result.is_domestic,
            haul_type=result.haul_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
