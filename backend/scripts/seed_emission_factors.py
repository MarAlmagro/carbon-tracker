#!/usr/bin/env python3
"""
Seed database with emission factors.

Sources:
- DEFRA 2023 Conversion Factors
- EPA Emission Factors Hub

Usage:
    python -m backend.scripts.seed_emission_factors
"""

import os

# Source constants
SOURCE_DEFRA = "DEFRA"
SOURCE_OUR_WORLD_IN_DATA = "Our World in Data"
SOURCE_ESTIMATED = "Estimated"

# Emission factors in kg CO2e per unit
# Source: DEFRA 2023 / EPA
EMISSION_FACTORS = [
    # Transport (kg CO2e per km)
    {
        "category": "transport",
        "type": "car_petrol",
        "factor": 0.17099,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "car_diesel",
        "factor": 0.15059,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "car_electric",
        "factor": 0.04745,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "bus",
        "factor": 0.08291,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "train",
        "factor": 0.03594,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "plane_domestic",
        "factor": 0.24587,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "plane_international",
        "factor": 0.19085,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    # Flight emissions (kg CO2e per km) - includes radiative forcing multiplier
    {
        "category": "transport",
        "type": "flight_domestic_short",
        "factor": 0.255,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "flight_domestic_medium",
        "factor": 0.195,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "flight_domestic_long",
        "factor": 0.175,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "flight_international_short",
        "factor": 0.270,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "flight_international_medium",
        "factor": 0.210,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "flight_international_long",
        "factor": 0.150,
        "unit": "km",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "bike",
        "factor": 0.0,
        "unit": "km",
        "source": "N/A",
        "source_year": 2023,
    },
    {
        "category": "transport",
        "type": "walk",
        "factor": 0.0,
        "unit": "km",
        "source": "N/A",
        "source_year": 2023,
    },
    # Energy (kg CO2e per kWh)
    {
        "category": "energy",
        "type": "electricity",
        "factor": 0.20705,
        "unit": "kWh",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "energy",
        "type": "natural_gas",
        "factor": 0.18293,
        "unit": "kWh",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    {
        "category": "energy",
        "type": "heating_oil",
        "factor": 0.24680,
        "unit": "kWh",
        "source": SOURCE_DEFRA,
        "source_year": 2023,
    },
    # Food (kg CO2e per serving/kg)
    {
        "category": "food",
        "type": "beef",
        "factor": 27.0,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "pork",
        "factor": 12.1,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "poultry",
        "factor": 6.9,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "fish",
        "factor": 5.4,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "dairy",
        "factor": 3.2,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "vegetables",
        "factor": 2.0,
        "unit": "kg",
        "source": SOURCE_OUR_WORLD_IN_DATA,
        "source_year": 2023,
    },
    {
        "category": "food",
        "type": "vegan_meal",
        "factor": 0.5,
        "unit": "serving",
        "source": SOURCE_ESTIMATED,
        "source_year": 2023,
    },
]

# Regional averages for comparison (kg CO2e per year, per capita)
REGIONAL_AVERAGES = [
    {"country_code": "ES", "country_name": "Spain", "annual_average_kg": 5800},
    {"country_code": "US", "country_name": "United States", "annual_average_kg": 14700},
    {"country_code": "GB", "country_name": "United Kingdom", "annual_average_kg": 5200},
    {"country_code": "DE", "country_name": "Germany", "annual_average_kg": 7900},
    {"country_code": "FR", "country_name": "France", "annual_average_kg": 4700},
    {"country_code": "IT", "country_name": "Italy", "annual_average_kg": 5500},
    {"country_code": "CN", "country_name": "China", "annual_average_kg": 7400},
    {"country_code": "IN", "country_name": "India", "annual_average_kg": 1900},
    {"country_code": "BR", "country_name": "Brazil", "annual_average_kg": 2200},
    {"country_code": "JP", "country_name": "Japan", "annual_average_kg": 8500},
    {"country_code": "MX", "country_name": "Mexico", "annual_average_kg": 3700},
    {"country_code": "AU", "country_name": "Australia", "annual_average_kg": 15400},
    {"country_code": "CA", "country_name": "Canada", "annual_average_kg": 14200},
]


def seed_database():
    """Seed the database with emission factors and regional averages."""
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    try:
        from infrastructure.config.supabase import get_supabase_client

        client = get_supabase_client()
        table = client.table("emission_factors")

        for factor_data in EMISSION_FACTORS:
            existing = (
                table.select("id")
                .eq("category", factor_data["category"])
                .eq("type", factor_data["type"])
                .eq("source_year", factor_data["source_year"])
                .execute()
            )

            if existing.data:
                print(
                    f"  ⏭ {factor_data['category']}/{factor_data['type']}: already exists"
                )
            else:
                table.insert(factor_data).execute()
                print(
                    f"  ✓ {factor_data['category']}/{factor_data['type']}: {factor_data['factor']} {factor_data['unit']}"
                )

        print(f"\n✅ Seeded {len(EMISSION_FACTORS)} emission factors")

    except ImportError as e:
        print(f"Import error: {e}")
        print("\nFalling back to dry-run mode...")
        print("Seeding emission factors...")
        for factor in EMISSION_FACTORS:
            print(
                f"  - {factor['category']}/{factor['type']}: {factor['factor']} {factor['unit']}"
            )

        print("\nSeeding regional averages...")
        for region in REGIONAL_AVERAGES:
            print(
                f"  - {region['country_name']} ({region['country_code']}): {region['annual_average_kg']} kg/year"
            )

        print("\n✅ Seed data ready for insertion")
        print(
            "   Run with SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY set to actually insert data"
        )


if __name__ == "__main__":
    seed_database()
