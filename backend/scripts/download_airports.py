"""Download and convert OpenFlights airport data to JSON."""

import csv
import json
import urllib.request
from pathlib import Path

# URL for OpenFlights airport database
AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

# Output file path
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "infrastructure" / "data" / "airports.json"

def download_and_convert():
    """Download airport data and convert to JSON."""
    print(f"Downloading airport data from {AIRPORTS_URL}...")

    with urllib.request.urlopen(AIRPORTS_URL) as response:
        csv_data = response.read().decode('utf-8')

    # Parse CSV (no header in OpenFlights data)
    # Format: ID,Name,City,Country,IATA,ICAO,Lat,Lon,Alt,TZ,DST,TzName,Type,Source
    airports = []
    reader = csv.reader(csv_data.strip().split('\n'))

    for row in reader:
        if len(row) < 14:
            continue

        # Skip airports without IATA code
        iata_code = row[4].strip()
        if not iata_code or iata_code == '\\N':
            continue

        # Skip military and closed airports (keep only "airport")
        airport_type = row[12].strip().lower()
        if airport_type != 'airport':
            continue

        try:
            airport = {
                "iata_code": iata_code,
                "icao_code": row[5].strip() if row[5] != '\\N' else '',
                "name": row[1].strip(),
                "city": row[2].strip(),
                "country": row[3].strip(),
                "country_code": get_country_code(row[3].strip()),
                "latitude": float(row[6]),
                "longitude": float(row[7])
            }
            airports.append(airport)
        except (ValueError, IndexError) as e:
            print(f"Skipping row due to error: {e}")
            continue

    print(f"Processed {len(airports)} airports")

    # Write to JSON file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(airports, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_FILE}")
    print(f"Total airports: {len(airports)}")


def get_country_code(country_name: str) -> str:
    """Map country name to ISO 2-letter code."""
    # Common country mappings (expand as needed)
    country_codes = {
        "United States": "US",
        "United Kingdom": "GB",
        "Canada": "CA",
        "Australia": "AU",
        "Germany": "DE",
        "France": "FR",
        "Spain": "ES",
        "Italy": "IT",
        "Japan": "JP",
        "China": "CN",
        "India": "IN",
        "Brazil": "BR",
        "Mexico": "MX",
        "Netherlands": "NL",
        "Switzerland": "CH",
        "Sweden": "SE",
        "Norway": "NO",
        "Denmark": "DK",
        "Finland": "FI",
        "Poland": "PL",
        "Russia": "RU",
        "South Korea": "KR",
        "Singapore": "SG",
        "Thailand": "TH",
        "Indonesia": "ID",
        "Malaysia": "MY",
        "Philippines": "PH",
        "Vietnam": "VN",
        "Turkey": "TR",
        "Greece": "GR",
        "Portugal": "PT",
        "Austria": "AT",
        "Belgium": "BE",
        "Ireland": "IE",
        "New Zealand": "NZ",
        "South Africa": "ZA",
        "Egypt": "EG",
        "United Arab Emirates": "AE",
        "Saudi Arabia": "SA",
        "Israel": "IL",
        "Argentina": "AR",
        "Chile": "CL",
        "Colombia": "CO",
        "Peru": "PE",
    }

    return country_codes.get(country_name, country_name[:2].upper())


if __name__ == "__main__":
    download_and_convert()
