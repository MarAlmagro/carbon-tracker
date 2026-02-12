# Feature: Flight Emissions Tracking

## Metadata
- **ID**: CT-004
- **Priority**: MEDIUM
- **Estimated Effort**: 4-6 hours
- **Dependencies**: CT-000 (Project Foundation), CT-001 (Transport Logging), CT-003 (Dashboard - optional)

## Summary
Add specialized flight tracking with origin/destination airport selection, automatic distance calculation, and differentiated emission factors for domestic vs international and short/medium/long haul flights.

## User Story
As a **frequent traveler**, I want to **log flight emissions with origin and destination airports** so that **I can accurately track the carbon impact of my air travel with realistic distance calculations**.

## Acceptance Criteria
- [ ] AC1: Flight form has origin and destination airport fields with autocomplete
- [ ] AC2: Distance is calculated automatically between selected airports
- [ ] AC3: Emission factors differ by flight type (domestic vs international, short/medium/long haul)
- [ ] AC4: Short haul: < 1,500 km, Medium: 1,500-4,000 km, Long: > 4,000 km
- [ ] AC5: Domestic vs international determined by country codes
- [ ] AC6: Flight activities stored with origin, destination, distance in database
- [ ] AC7: Dashboard shows flights separately from ground transport
- [ ] AC8: Airport autocomplete searches by IATA code and city name
- [ ] AC9: All flight types available in i18n files (EN/ES)
- [ ] AC10: Emission factors seeded in database for all flight types

## API Contract

### 1. Search Airports
**Endpoint:** `GET /api/v1/airports/search`

**Query Parameters:**
- `q` (required): Search query (IATA code or city name, min 2 characters)
- `limit` (optional): Max results (default: 10, max: 50)

**Request:**
```http
GET /api/v1/airports/search?q=LON&limit=10
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "iata_code": "LHR",
      "name": "London Heathrow Airport",
      "city": "London",
      "country": "United Kingdom",
      "country_code": "GB",
      "latitude": 51.4700,
      "longitude": -0.4543
    },
    {
      "iata_code": "LGW",
      "name": "London Gatwick Airport",
      "city": "London",
      "country": "United Kingdom",
      "country_code": "GB",
      "latitude": 51.1481,
      "longitude": -0.1903
    }
  ]
}
```

### 2. Calculate Flight Distance
**Endpoint:** `POST /api/v1/flights/calculate`

**Request Body:**
```json
{
  "origin_iata": "JFK",
  "destination_iata": "LHR"
}
```

**Response (200 OK):**
```json
{
  "origin_iata": "JFK",
  "destination_iata": "LHR",
  "distance_km": 5541,
  "flight_type": "international_long",
  "is_domestic": false,
  "haul_type": "long"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Airport not found: XXX"
}
```

### 3. Log Flight Activity
**Endpoint:** `POST /api/v1/activities`

**Request Body:**
```json
{
  "category": "transport",
  "type": "flight_international_long",
  "value": 5541,
  "date": "2026-02-10",
  "notes": "Business trip to London",
  "metadata": {
    "origin_iata": "JFK",
    "destination_iata": "LHR",
    "origin_city": "New York",
    "destination_city": "London"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "transport",
  "type": "flight_international_long",
  "value": 5541,
  "co2e_kg": 831.15,
  "date": "2026-02-10",
  "notes": "Business trip to London",
  "metadata": {
    "origin_iata": "JFK",
    "destination_iata": "LHR",
    "origin_city": "New York",
    "destination_city": "London"
  },
  "user_id": null,
  "session_id": "abc-123",
  "created_at": "2026-02-10T14:30:00Z"
}
```

## Emission Factors

### Flight Emission Factors (kg CO2e per km per passenger)

| Flight Type | Factor | Notes |
|-------------|--------|-------|
| `flight_domestic_short` | 0.255 | Domestic, < 1,500 km |
| `flight_domestic_medium` | 0.195 | Domestic, 1,500-4,000 km |
| `flight_domestic_long` | 0.175 | Domestic, > 4,000 km |
| `flight_international_short` | 0.270 | International, < 1,500 km |
| `flight_international_medium` | 0.210 | International, 1,500-4,000 km |
| `flight_international_long` | 0.150 | International, > 4,000 km |

Source: UK DEFRA 2023, includes radiative forcing multiplier (1.9x)

## Airport Data Structure

### Airport Record
```json
{
  "iata_code": "JFK",
  "icao_code": "KJFK",
  "name": "John F. Kennedy International Airport",
  "city": "New York",
  "country": "United States",
  "country_code": "US",
  "latitude": 40.6413,
  "longitude": -73.7781,
  "timezone": "America/New_York"
}
```

**Data Source:** OpenFlights Airport Database (~7,000 commercial airports)

## UI/UX Requirements

### New Components

#### 1. Flight Form
Replace transport type dropdown with two airport selectors when "Flight" is selected.

**Layout:**
```
┌─────────────────────────────────────────┐
│  Transport Category: [Ground] [Flight]  │
├─────────────────────────────────────────┤
│  Origin Airport                         │
│  [Search by city or code...]     [×]    │
│  → JFK - New York (John F. Kennedy...)  │
│                                         │
│  Destination Airport                    │
│  [Search by city or code...]     [×]    │
│  → LHR - London (Heathrow)              │
│                                         │
│  Distance: 5,541 km (calculated)        │
│  Estimated CO2e: 831.15 kg             │
│                                         │
│  Date: [2026-02-10]                     │
│  Notes: [Optional notes...]             │
│                                         │
│  [Log Flight Activity]                  │
└─────────────────────────────────────────┘
```

**Airport Autocomplete Behavior:**
- Minimum 2 characters to trigger search
- Shows up to 10 results
- Display format: `IATA - City (Airport Name)`
- Debounce input (300ms)
- Loading spinner during search
- Clear button (×) to reset selection

#### 2. Flight Activity Card
Display origin → destination with flight icon.

```
┌─────────────────────────────────────────┐
│  ✈️  JFK → LHR                          │
│  5,541 km • 831.15 kg CO2e             │
│  Feb 10, 2026                           │
│  Business trip to London                │
└─────────────────────────────────────────┘
```

#### 3. Dashboard Flight Section
Separate section or filter for flights in activity list.

### Updated Components

#### Transport Form
- Add "Flight" tab/button alongside ground transport
- Show FlightForm component when flight selected
- Show existing TransportForm for ground transport

## Technical Design

### What's Already Done (CT-000/CT-001)

#### Backend
- ✓ Activity entity with metadata field (JSONField for origin/destination)
- ✓ EmissionFactor repository for factor lookups
- ✓ LogActivityUseCase for creating activities
- ✓ POST /api/v1/activities endpoint
- ✓ Activity metadata stored as JSON in database

#### Frontend
- ✓ TransportForm component
- ✓ ActivityCard component
- ✓ useCreateActivity mutation hook
- ✓ Form validation with react-hook-form

### What Needs to Be Built

#### Backend (NEW)

**1. Airport Data File** (`backend/src/infrastructure/data/airports.json` - NEW)

```json
[
  {
    "iata_code": "JFK",
    "icao_code": "KJFK",
    "name": "John F. Kennedy International Airport",
    "city": "New York",
    "country": "United States",
    "country_code": "US",
    "latitude": 40.6413,
    "longitude": -73.7781
  },
  {
    "iata_code": "LHR",
    "icao_code": "EGLL",
    "name": "London Heathrow Airport",
    "city": "London",
    "country": "United Kingdom",
    "country_code": "GB",
    "latitude": 51.4700,
    "longitude": -0.4543
  }
  // ... ~7,000 more airports
]
```

**2. Airport Entity** (`backend/src/domain/entities/airport.py` - NEW)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Airport:
    """Airport entity."""
    iata_code: str
    icao_code: str
    name: str
    city: str
    country: str
    country_code: str
    latitude: float
    longitude: float
```

**3. Airport Repository Port** (`backend/src/domain/ports/airport_repository.py` - NEW)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.airport import Airport

class AirportRepository(ABC):
    """Port for airport data access."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Airport]:
        """Search airports by IATA code or city name."""
        pass

    @abstractmethod
    async def get_by_iata(self, iata_code: str) -> Optional[Airport]:
        """Get airport by IATA code."""
        pass
```

**4. JSON Airport Repository** (`backend/src/infrastructure/repositories/json_airport_repository.py` - NEW)

```python
import json
from pathlib import Path
from typing import List, Optional
from domain.entities.airport import Airport
from domain.ports.airport_repository import AirportRepository

class JSONAirportRepository(AirportRepository):
    """Airport repository backed by JSON file."""

    def __init__(self, data_file: Path):
        self._data_file = data_file
        self._airports: List[Airport] = []
        self._load_data()

    def _load_data(self):
        """Load airports from JSON file."""
        with open(self._data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._airports = [
                Airport(
                    iata_code=row['iata_code'],
                    icao_code=row['icao_code'],
                    name=row['name'],
                    city=row['city'],
                    country=row['country'],
                    country_code=row['country_code'],
                    latitude=row['latitude'],
                    longitude=row['longitude']
                )
                for row in data
            ]

    async def search(self, query: str, limit: int = 10) -> List[Airport]:
        """Search airports by IATA or city (case-insensitive)."""
        query = query.upper()
        results = [
            airport for airport in self._airports
            if query in airport.iata_code or query.upper() in airport.city.upper()
        ]
        return results[:limit]

    async def get_by_iata(self, iata_code: str) -> Optional[Airport]:
        """Get airport by IATA code."""
        for airport in self._airports:
            if airport.iata_code == iata_code.upper():
                return airport
        return None
```

**5. Flight Distance Service** (`backend/src/domain/services/flight_distance_service.py` - NEW)

```python
import math
from domain.entities.airport import Airport

class FlightDistanceService:
    """Service for calculating flight distances."""

    @staticmethod
    def calculate_distance_km(origin: Airport, destination: Airport) -> float:
        """
        Calculate great-circle distance using Haversine formula.
        Returns distance in kilometers.
        """
        lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
        lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in kilometers
        earth_radius_km = 6371.0

        return round(c * earth_radius_km, 0)

    @staticmethod
    def determine_flight_type(
        origin: Airport,
        destination: Airport,
        distance_km: float
    ) -> str:
        """
        Determine flight type based on distance and countries.
        Returns: flight_domestic_short, flight_international_long, etc.
        """
        is_domestic = origin.country_code == destination.country_code

        # Determine haul type
        if distance_km < 1500:
            haul = "short"
        elif distance_km <= 4000:
            haul = "medium"
        else:
            haul = "long"

        # Construct type
        domestic_or_intl = "domestic" if is_domestic else "international"
        return f"flight_{domestic_or_intl}_{haul}"
```

**6. Calculate Flight Use Case** (`backend/src/domain/use_cases/calculate_flight.py` - NEW)

```python
from domain.ports.airport_repository import AirportRepository
from domain.services.flight_distance_service import FlightDistanceService

class CalculateFlightInput:
    """Input for flight calculation."""
    def __init__(self, origin_iata: str, destination_iata: str):
        self.origin_iata = origin_iata
        self.destination_iata = destination_iata

class FlightCalculation:
    """Output for flight calculation."""
    def __init__(
        self,
        origin_iata: str,
        destination_iata: str,
        distance_km: float,
        flight_type: str,
        is_domestic: bool,
        haul_type: str
    ):
        self.origin_iata = origin_iata
        self.destination_iata = destination_iata
        self.distance_km = distance_km
        self.flight_type = flight_type
        self.is_domestic = is_domestic
        self.haul_type = haul_type

class CalculateFlightUseCase:
    """Calculate flight distance and type."""

    def __init__(
        self,
        airport_repo: AirportRepository,
        distance_service: FlightDistanceService
    ):
        self._airport_repo = airport_repo
        self._distance_service = distance_service

    async def execute(self, input_data: CalculateFlightInput) -> FlightCalculation:
        """Execute flight calculation."""
        # Fetch airports
        origin = await self._airport_repo.get_by_iata(input_data.origin_iata)
        if not origin:
            raise ValueError(f"Airport not found: {input_data.origin_iata}")

        destination = await self._airport_repo.get_by_iata(input_data.destination_iata)
        if not destination:
            raise ValueError(f"Airport not found: {input_data.destination_iata}")

        # Calculate distance
        distance_km = self._distance_service.calculate_distance_km(origin, destination)

        # Determine flight type
        flight_type = self._distance_service.determine_flight_type(
            origin, destination, distance_km
        )

        # Extract haul type
        haul_type = flight_type.split('_')[-1]  # "short", "medium", "long"
        is_domestic = "domestic" in flight_type

        return FlightCalculation(
            origin_iata=input_data.origin_iata,
            destination_iata=input_data.destination_iata,
            distance_km=distance_km,
            flight_type=flight_type,
            is_domestic=is_domestic,
            haul_type=haul_type
        )
```

**7. Airport Schemas** (`backend/src/api/schemas/airport.py` - NEW)

```python
from pydantic import BaseModel, Field

class AirportResponse(BaseModel):
    """Airport response."""
    iata_code: str = Field(min_length=3, max_length=3)
    name: str
    city: str
    country: str
    country_code: str = Field(min_length=2, max_length=2)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class AirportSearchResponse(BaseModel):
    """Airport search results."""
    results: list[AirportResponse]

class FlightCalculationRequest(BaseModel):
    """Request to calculate flight."""
    origin_iata: str = Field(min_length=3, max_length=3)
    destination_iata: str = Field(min_length=3, max_length=3)

class FlightCalculationResponse(BaseModel):
    """Flight calculation result."""
    origin_iata: str
    destination_iata: str
    distance_km: float
    flight_type: str
    is_domestic: bool
    haul_type: str
```

**8. Airport Routes** (`backend/src/api/routes/airports.py` - NEW)

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from domain.ports.airport_repository import AirportRepository
from api.dependencies.repositories import get_airport_repository
from api.schemas.airport import AirportSearchResponse, AirportResponse

router = APIRouter(prefix="/airports", tags=["airports"])

@router.get("/search", response_model=AirportSearchResponse)
async def search_airports(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    airport_repo: AirportRepository = Depends(get_airport_repository)
) -> AirportSearchResponse:
    """Search airports by IATA code or city name."""
    results = await airport_repo.search(q, limit)

    return AirportSearchResponse(
        results=[
            AirportResponse(
                iata_code=airport.iata_code,
                name=airport.name,
                city=airport.city,
                country=airport.country,
                country_code=airport.country_code,
                latitude=airport.latitude,
                longitude=airport.longitude
            )
            for airport in results
        ]
    )
```

**9. Flight Routes** (`backend/src/api/routes/flights.py` - NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from domain.use_cases.calculate_flight import CalculateFlightUseCase, CalculateFlightInput
from api.dependencies.use_cases import get_calculate_flight_use_case
from api.schemas.airport import FlightCalculationRequest, FlightCalculationResponse

router = APIRouter(prefix="/flights", tags=["flights"])

@router.post("/calculate", response_model=FlightCalculationResponse)
async def calculate_flight(
    request: FlightCalculationRequest,
    use_case: CalculateFlightUseCase = Depends(get_calculate_flight_use_case)
) -> FlightCalculationResponse:
    """Calculate flight distance and determine type."""
    try:
        input_data = CalculateFlightInput(
            origin_iata=request.origin_iata,
            destination_iata=request.destination_iata
        )

        result = await use_case.execute(input_data)

        return FlightCalculationResponse(
            origin_iata=result.origin_iata,
            destination_iata=result.destination_iata,
            distance_km=result.distance_km,
            flight_type=result.flight_type,
            is_domestic=result.is_domestic,
            haul_type=result.haul_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**10. Update Activity Schema** (`backend/src/api/schemas/activity.py`)

Add optional metadata field:
```python
class ActivityCreate(BaseModel):
    """Activity creation request."""
    # ... existing fields ...
    metadata: Optional[dict] = None  # For flight origin/destination
```

**11. Seed Flight Emission Factors** (`backend/scripts/seed_emission_factors.py`)

Add flight factors to seeding script:
```python
flight_factors = [
    ("transport", "flight_domestic_short", 0.255, "kg CO2e/km", "UK DEFRA 2023"),
    ("transport", "flight_domestic_medium", 0.195, "kg CO2e/km", "UK DEFRA 2023"),
    ("transport", "flight_domestic_long", 0.175, "kg CO2e/km", "UK DEFRA 2023"),
    ("transport", "flight_international_short", 0.270, "kg CO2e/km", "UK DEFRA 2023"),
    ("transport", "flight_international_medium", 0.210, "kg CO2e/km", "UK DEFRA 2023"),
    ("transport", "flight_international_long", 0.150, "kg CO2e/km", "UK DEFRA 2023"),
]
```

**12. Register Routes** (`backend/src/api/main.py`)

```python
from api.routes import airports, flights

app.include_router(airports.router, prefix="/api/v1")
app.include_router(flights.router, prefix="/api/v1")
```

#### Frontend (NEW)

**1. Airport API Methods** (`frontend/src/services/api.ts`)

```typescript
export interface Airport {
  iata_code: string;
  name: string;
  city: string;
  country: string;
  country_code: string;
  latitude: number;
  longitude: number;
}

export interface FlightCalculation {
  origin_iata: string;
  destination_iata: string;
  distance_km: number;
  flight_type: string;
  is_domestic: boolean;
  haul_type: string;
}

export class ApiClient {
  // ... existing methods ...

  async searchAirports(query: string, limit: number = 10): Promise<Airport[]> {
    const response = await this.request<{ results: Airport[] }>(
      `/api/v1/airports/search?q=${encodeURIComponent(query)}&limit=${limit}`
    );
    return response.results;
  }

  async calculateFlight(
    originIata: string,
    destinationIata: string
  ): Promise<FlightCalculation> {
    return this.request<FlightCalculation>('/api/v1/flights/calculate', {
      method: 'POST',
      body: JSON.stringify({
        origin_iata: originIata,
        destination_iata: destinationIata
      })
    });
  }
}
```

**2. Airport Search Hook** (`frontend/src/hooks/useAirportSearch.ts` - NEW)

```typescript
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';

export function useAirportSearch(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['airports', query],
    queryFn: () => apiClient.searchAirports(query),
    enabled: enabled && query.length >= 2,
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
}
```

**3. Airport Autocomplete Component** (`frontend/src/components/features/flight/AirportAutocomplete.tsx` - NEW)

```typescript
import { useState, useEffect, useRef } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { useAirportSearch } from '@/hooks/useAirportSearch';
import { Airport } from '@/services/api';

interface AirportAutocompleteProps {
  value: Airport | null;
  onChange: (airport: Airport | null) => void;
  placeholder?: string;
  label: string;
}

export default function AirportAutocomplete({
  value,
  onChange,
  placeholder,
  label
}: AirportAutocompleteProps) {
  const [inputValue, setInputValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const debouncedQuery = useDebounce(inputValue, 300);

  const { data: airports, isLoading } = useAirportSearch(
    debouncedQuery,
    isOpen && debouncedQuery.length >= 2
  );

  const handleSelect = (airport: Airport) => {
    onChange(airport);
    setInputValue(`${airport.iata_code} - ${airport.city}`);
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setInputValue('');
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <label className="block text-sm font-medium mb-1">{label}</label>

      <div className="relative">
        <input
          type="text"
          value={value ? `${value.iata_code} - ${value.city}` : inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsOpen(true);
            if (!e.target.value) onChange(null);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full px-3 py-2 border rounded-md"
        />

        {value && (
          <button
            onClick={handleClear}
            className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>

      {isOpen && airports && airports.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
          {airports.map((airport) => (
            <button
              key={airport.iata_code}
              onClick={() => handleSelect(airport)}
              className="w-full px-3 py-2 text-left hover:bg-gray-100"
            >
              <div className="font-medium">
                {airport.iata_code} - {airport.city}
              </div>
              <div className="text-sm text-gray-600">{airport.name}</div>
            </button>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="absolute right-10 top-10 text-gray-400">
          Loading...
        </div>
      )}
    </div>
  );
}
```

**4. Flight Form Component** (`frontend/src/components/features/activity/FlightForm.tsx` - NEW)

```typescript
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import AirportAutocomplete from '@/components/features/flight/AirportAutocomplete';
import { apiClient, Airport } from '@/services/api';

interface FlightFormData {
  date: string;
  notes: string;
}

export default function FlightForm() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [origin, setOrigin] = useState<Airport | null>(null);
  const [destination, setDestination] = useState<Airport | null>(null);
  const [distance, setDistance] = useState<number | null>(null);
  const [estimatedCo2e, setEstimatedCo2e] = useState<number | null>(null);

  const { register, handleSubmit, reset } = useForm<FlightFormData>({
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
      notes: ''
    }
  });

  // Calculate distance and CO2e when both airports selected
  useEffect(() => {
    if (origin && destination) {
      apiClient
        .calculateFlight(origin.iata_code, destination.iata_code)
        .then((result) => {
          setDistance(result.distance_km);
          // Estimate CO2e (actual calculation happens on backend)
          setEstimatedCo2e(result.distance_km * 0.15); // Rough estimate
        });
    } else {
      setDistance(null);
      setEstimatedCo2e(null);
    }
  }, [origin, destination]);

  const createActivityMutation = useMutation({
    mutationFn: async (data: FlightFormData) => {
      if (!origin || !destination || !distance) {
        throw new Error('Origin and destination required');
      }

      const flightCalc = await apiClient.calculateFlight(
        origin.iata_code,
        destination.iata_code
      );

      return apiClient.createActivity({
        category: 'transport',
        type: flightCalc.flight_type,
        value: flightCalc.distance_km,
        date: data.date,
        notes: data.notes,
        metadata: {
          origin_iata: origin.iata_code,
          destination_iata: destination.iata_code,
          origin_city: origin.city,
          destination_city: destination.city
        }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities'] });
      reset();
      setOrigin(null);
      setDestination(null);
    }
  });

  const onSubmit = (data: FlightFormData) => {
    createActivityMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <AirportAutocomplete
        value={origin}
        onChange={setOrigin}
        label={t('activity.flight.origin')}
        placeholder={t('activity.flight.searchAirport')}
      />

      <AirportAutocomplete
        value={destination}
        onChange={setDestination}
        label={t('activity.flight.destination')}
        placeholder={t('activity.flight.searchAirport')}
      />

      {distance && (
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-sm text-gray-700">
            {t('activity.flight.distance')}: {distance.toFixed(0)} km
          </div>
          {estimatedCo2e && (
            <div className="text-sm text-gray-700">
              {t('activity.flight.estimatedCo2e')}: {estimatedCo2e.toFixed(2)} kg CO2e
            </div>
          )}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.date')}
        </label>
        <input
          type="date"
          {...register('date', { required: true })}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.notes')}
        </label>
        <textarea
          {...register('notes')}
          placeholder={t('activity.notesPlaceholder')}
          className="w-full px-3 py-2 border rounded-md"
          rows={3}
        />
      </div>

      <button
        type="submit"
        disabled={!origin || !destination || createActivityMutation.isPending}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {createActivityMutation.isPending
          ? t('common.loading')
          : t('activity.flight.logFlight')}
      </button>
    </form>
  );
}
```

**5. Update Transport Form** (`frontend/src/components/features/activity/TransportForm.tsx`)

Add tab/button to switch between ground and flight:
```typescript
const [transportMode, setTransportMode] = useState<'ground' | 'flight'>('ground');

return (
  <div>
    <div className="flex space-x-2 mb-4">
      <button
        onClick={() => setTransportMode('ground')}
        className={transportMode === 'ground' ? 'active' : ''}
      >
        Ground Transport
      </button>
      <button
        onClick={() => setTransportMode('flight')}
        className={transportMode === 'flight' ? 'active' : ''}
      >
        Flight
      </button>
    </div>

    {transportMode === 'ground' ? (
      <GroundTransportForm />
    ) : (
      <FlightForm />
    )}
  </div>
);
```

**6. Update Activity Card** (`frontend/src/components/features/activity/ActivityCard.tsx`)

Add flight display logic:
```typescript
const isFlight = activity.type.startsWith('flight_');

if (isFlight && activity.metadata) {
  return (
    <div className="activity-card">
      <div className="text-lg">
        ✈️ {activity.metadata.origin_iata} → {activity.metadata.destination_iata}
      </div>
      <div className="text-sm text-gray-600">
        {activity.value.toFixed(0)} km • {activity.co2e_kg.toFixed(2)} kg CO2e
      </div>
      <div className="text-xs text-gray-500">{formatDate(activity.date)}</div>
      {activity.notes && <div className="text-sm">{activity.notes}</div>}
    </div>
  );
}
```

**7. Add i18n Translations**

Update `frontend/src/i18n/locales/en.json`:
```json
{
  "activity": {
    "flight": {
      "origin": "Origin Airport",
      "destination": "Destination Airport",
      "searchAirport": "Search by city or code...",
      "distance": "Distance",
      "estimatedCo2e": "Estimated CO2e",
      "logFlight": "Log Flight Activity"
    }
  }
}
```

**8. Download Airports JSON**

Download OpenFlights airport database and place in `frontend/public/airports.json` OR use backend endpoint.

## Implementation Steps

1. **Download Airport Data**
   - Download OpenFlights airports.json (~7,000 airports)
   - Place in `backend/src/infrastructure/data/airports.json`
   - Verify JSON structure matches Airport entity

2. **Create Airport Entity and Port**
   - Create `backend/src/domain/entities/airport.py`
   - Create `backend/src/domain/ports/airport_repository.py`

3. **Create JSON Airport Repository**
   - Create `backend/src/infrastructure/repositories/json_airport_repository.py`
   - Implement search() and get_by_iata()
   - Add unit tests

4. **Create Flight Distance Service**
   - Create `backend/src/domain/services/flight_distance_service.py`
   - Implement Haversine formula
   - Implement determine_flight_type()
   - Add unit tests

5. **Create Calculate Flight Use Case**
   - Create `backend/src/domain/use_cases/calculate_flight.py`
   - Implement CalculateFlightUseCase
   - Add unit tests

6. **Create Airport and Flight Schemas**
   - Create `backend/src/api/schemas/airport.py`
   - Add all request/response models

7. **Create Airport Routes**
   - Create `backend/src/api/routes/airports.py`
   - Add GET /airports/search endpoint
   - Add integration tests

8. **Create Flight Routes**
   - Create `backend/src/api/routes/flights.py`
   - Add POST /flights/calculate endpoint
   - Add integration tests

9. **Update Activity Schema**
   - Add optional metadata field to ActivityCreate
   - Document metadata structure for flights

10. **Seed Flight Emission Factors**
    - Update `backend/scripts/seed_emission_factors.py`
    - Add 6 flight emission factors
    - Run seeding script

11. **Register Routes in Main App**
    - Update `backend/src/api/main.py`
    - Register airports and flights routers

12. **Add Frontend Airport API Methods**
    - Update `frontend/src/services/api.ts`
    - Add searchAirports() and calculateFlight()

13. **Create Airport Search Hook**
    - Create `frontend/src/hooks/useAirportSearch.ts`
    - Implement with React Query and debounce

14. **Create Airport Autocomplete Component**
    - Create `frontend/src/components/features/flight/AirportAutocomplete.tsx`
    - Add dropdown, loading states, clear button

15. **Create Flight Form Component**
    - Create `frontend/src/components/features/activity/FlightForm.tsx`
    - Integrate AirportAutocomplete
    - Add distance/CO2e calculation preview

16. **Update Transport Form**
    - Add Ground/Flight tab switcher
    - Conditionally render GroundTransportForm or FlightForm

17. **Update Activity Card**
    - Add flight display logic with airplane icon
    - Show origin → destination format

18. **Add i18n Translations**
    - Update EN and ES locale files
    - Add flight-specific strings

19. **Test Backend Flight Endpoints**
    - Test airport search with various queries
    - Test flight calculation with known distances
    - Verify flight type determination

20. **Test Frontend Flight Form**
    - Test airport autocomplete
    - Test flight logging end-to-end
    - Verify activity appears in list

21. **Manual Testing**
    - Log multiple flights (domestic/international, short/long)
    - Verify distance calculations
    - Verify CO2e calculations match flight types
    - Test mobile responsiveness

## Test Requirements

### Backend Tests

**Unit Tests:**
- `test_haversine_distance()` - JFK to LHR = 5,541 km
- `test_determine_flight_type_domestic_short()` - LAX to SFO
- `test_determine_flight_type_international_long()` - JFK to LHR
- `test_airport_search_by_iata()` - "LON" returns LHR, LGW, etc.
- `test_airport_search_by_city()` - "London" returns all London airports
- `test_calculate_flight_use_case()` - Returns correct distance and type

**Integration Tests:**
- `test_search_airports_endpoint()` - Returns 200 with results
- `test_calculate_flight_endpoint()` - Returns 200 with calculation
- `test_calculate_flight_invalid_iata()` - Returns 400 error

### Frontend Tests

**Component Tests:**
- `AirportAutocomplete.test.tsx` - Renders, searches, selects airport
- `FlightForm.test.tsx` - Calculates distance, submits flight activity
- `ActivityCard.test.tsx` - Displays flight format correctly

**E2E Tests:**
- `flight-logging.spec.ts` - Complete flow: search airports → log flight → verify in list

## Definition of Done

- [ ] Airport data loaded with ~7,000 airports
- [ ] Airport search endpoint returns results
- [ ] Flight calculation endpoint returns distance and type
- [ ] 6 flight emission factors seeded in database
- [ ] Frontend flight form autocompletes airports
- [ ] Distance calculated automatically between airports
- [ ] Flight activities stored with origin/destination metadata
- [ ] Activity card displays flights with airplane icon
- [ ] All backend tests pass (9 new tests)
- [ ] All frontend tests pass (3 component + 1 E2E tests)
- [ ] No TypeScript or Python errors
- [ ] Documentation updated with flight feature

## Out of Scope

- Multi-leg flights (connections) - log separately for now
- Flight class (economy/business/first) - use average for now
- Historical flight data import (future: CT-004.1)
- Carbon offset options (future: CT-004.2)
- Airline-specific emission factors (future: CT-004.3)
- Flight search/booking integration (future: CT-004.4)

## Related

- **Dependencies:** CT-000, CT-001
- **Enhances:** CT-003 (Dashboard shows flights separately)
- **Architecture:** Uses AggregationService for flight-specific charts
