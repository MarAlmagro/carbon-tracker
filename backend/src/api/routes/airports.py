"""Airport search endpoints."""

from fastapi import APIRouter, Depends, Query

from api.dependencies.use_cases import get_airport_repository
from api.schemas.airport import AirportResponse, AirportSearchResponse
from domain.ports.airport_repository import AirportRepository

router = APIRouter(prefix="/airports", tags=["airports"])


@router.get("/search", response_model=AirportSearchResponse)
async def search_airports(
    q: str = Query(
        ..., min_length=2, description="Search query (IATA code or city name)"
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    airport_repo: AirportRepository = Depends(get_airport_repository),
) -> AirportSearchResponse:
    """
    Search airports by IATA code or city name.

    - **q**: Search query (minimum 2 characters)
    - **limit**: Maximum number of results (1-50)

    Returns list of matching airports with their details.
    """
    airports = await airport_repo.search(q, limit)

    return AirportSearchResponse(
        results=[
            AirportResponse(
                iata_code=airport.iata_code,
                name=airport.name,
                city=airport.city,
                country=airport.country,
                country_code=airport.country_code,
                latitude=airport.latitude,
                longitude=airport.longitude,
            )
            for airport in airports
        ]
    )
