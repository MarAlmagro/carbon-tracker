"""Service for calculating flight distances and determining flight types."""

import math

from domain.entities.airport import Airport


class FlightDistanceService:
    """Service for flight distance calculations and type determination."""

    @staticmethod
    def calculate_distance_km(origin: Airport, destination: Airport) -> float:
        """
        Calculate great-circle distance between two airports using Haversine formula.

        Args:
            origin: Origin airport
            destination: Destination airport

        Returns:
            Distance in kilometers (rounded to nearest integer)
        """
        # Convert to radians
        lat1 = math.radians(origin.latitude)
        lon1 = math.radians(origin.longitude)
        lat2 = math.radians(destination.latitude)
        lon2 = math.radians(destination.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in kilometers
        earth_radius_km = 6371.0

        return round(c * earth_radius_km, 0)

    @staticmethod
    def determine_flight_type(
        origin: Airport, destination: Airport, distance_km: float
    ) -> str:
        """
        Determine flight type based on distance and countries.

        Flight types:
        - Short haul: < 1,500 km
        - Medium haul: 1,500-4,000 km
        - Long haul: > 4,000 km

        Domestic vs international determined by country codes.

        Args:
            origin: Origin airport
            destination: Destination airport
            distance_km: Distance in kilometers

        Returns:
            Flight type (e.g., "flight_domestic_short", "flight_international_long")
        """
        is_domestic = origin.country_code == destination.country_code

        # Determine haul type based on distance
        if distance_km < 1500:
            haul = "short"
        elif distance_km <= 4000:
            haul = "medium"
        else:
            haul = "long"

        # Construct flight type
        domestic_or_intl = "domestic" if is_domestic else "international"
        return f"flight_{domestic_or_intl}_{haul}"

    @staticmethod
    def extract_haul_type(flight_type: str) -> str:
        """
        Extract haul type from flight type string.

        Args:
            flight_type: Flight type (e.g., "flight_domestic_short")

        Returns:
            Haul type ("short", "medium", or "long")
        """
        return flight_type.split("_")[-1]

    @staticmethod
    def is_domestic(flight_type: str) -> bool:
        """
        Check if flight type is domestic.

        Args:
            flight_type: Flight type (e.g., "flight_domestic_short")

        Returns:
            True if domestic, False if international
        """
        return "domestic" in flight_type
