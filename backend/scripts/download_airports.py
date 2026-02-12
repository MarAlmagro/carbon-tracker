"""Download and convert OpenFlights airport data to JSON."""

import csv
import json
import urllib.request
from pathlib import Path

# URL for OpenFlights airport database
AIRPORTS_URL = (
    "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
)

# Output file path
OUTPUT_FILE = (
    Path(__file__).parent.parent / "src" / "infrastructure" / "data" / "airports.json"
)


def download_and_convert():
    """Download airport data and convert to JSON."""
    print(f"Downloading airport data from {AIRPORTS_URL}...")

    with urllib.request.urlopen(AIRPORTS_URL) as response:
        csv_data = response.read().decode("utf-8")

    # Parse CSV (no header in OpenFlights data)
    # Format: ID,Name,City,Country,IATA,ICAO,Lat,Lon,Alt,TZ,DST,TzName,Type,Source
    airports = []
    reader = csv.reader(csv_data.strip().split("\n"))

    for row in reader:
        if len(row) < 14:
            continue

        # Skip airports without IATA code
        iata_code = row[4].strip()
        if not iata_code or iata_code == "\\N":
            continue

        # Skip military and closed airports (keep only "airport")
        airport_type = row[12].strip().lower()
        if airport_type != "airport":
            continue

        try:
            airport = {
                "iata_code": iata_code,
                "icao_code": row[5].strip() if row[5] != "\\N" else "",
                "name": row[1].strip(),
                "city": row[2].strip(),
                "country": row[3].strip(),
                "country_code": get_country_code(row[3].strip()),
                "latitude": float(row[6]),
                "longitude": float(row[7]),
            }
            airports.append(airport)
        except (ValueError, IndexError) as e:
            print(f"Skipping row due to error: {e}")
            continue

    print(f"Processed {len(airports)} airports")

    # Write to JSON file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
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
        "South Sudan": "SS",
        "Czech Republic": "CZ",
        "Hong Kong": "HK",
        "Taiwan": "TW",
        "Iceland": "IS",
        "Romania": "RO",
        "Hungary": "HU",
        "Bulgaria": "BG",
        "Croatia": "HR",
        "Serbia": "RS",
        "Ukraine": "UA",
        "Morocco": "MA",
        "Tunisia": "TN",
        "Kenya": "KE",
        "Nigeria": "NG",
        "Ethiopia": "ET",
        "Tanzania": "TZ",
        "Ghana": "GH",
        "Senegal": "SN",
        "Mozambique": "MZ",
        "Madagascar": "MG",
        "Cameroon": "CM",
        "Ivory Coast": "CI",
        "Cote d'Ivoire": "CI",
        "Pakistan": "PK",
        "Bangladesh": "BD",
        "Sri Lanka": "LK",
        "Nepal": "NP",
        "Myanmar": "MM",
        "Burma": "MM",
        "Cambodia": "KH",
        "Laos": "LA",
        "Mongolia": "MN",
        "Kazakhstan": "KZ",
        "Uzbekistan": "UZ",
        "Qatar": "QA",
        "Kuwait": "KW",
        "Oman": "OM",
        "Bahrain": "BH",
        "Jordan": "JO",
        "Lebanon": "LB",
        "Iraq": "IQ",
        "Iran": "IR",
        "Afghanistan": "AF",
        "Ecuador": "EC",
        "Venezuela": "VE",
        "Bolivia": "BO",
        "Paraguay": "PY",
        "Uruguay": "UY",
        "Costa Rica": "CR",
        "Panama": "PA",
        "Cuba": "CU",
        "Jamaica": "JM",
        "Dominican Republic": "DO",
        "Puerto Rico": "PR",
        "Trinidad and Tobago": "TT",
        "Guatemala": "GT",
        "Honduras": "HN",
        "El Salvador": "SV",
        "Nicaragua": "NI",
        "Papua New Guinea": "PG",
        "Fiji": "FJ",
        "Greenland": "GL",
        "Faroe Islands": "FO",
        "Malta": "MT",
        "Cyprus": "CY",
        "Luxembourg": "LU",
        "Estonia": "EE",
        "Latvia": "LV",
        "Lithuania": "LT",
        "Slovenia": "SI",
        "Slovakia": "SK",
        "Bosnia and Herzegovina": "BA",
        "North Macedonia": "MK",
        "Macedonia": "MK",
        "Montenegro": "ME",
        "Albania": "AL",
        "Kosovo": "XK",
        "Georgia": "GE",
        "Armenia": "AM",
        "Azerbaijan": "AZ",
        "Bahamas": "BS",
        "Bermuda": "BM",
        "Barbados": "BB",
        "Guam": "GU",
        "Samoa": "WS",
        "American Samoa": "AS",
        "French Polynesia": "PF",
        "New Caledonia": "NC",
        "Reunion": "RE",
        "Martinique": "MQ",
        "Guadeloupe": "GP",
        "French Guiana": "GF",
        "Macau": "MO",
        "Brunei": "BN",
        "Maldives": "MV",
        "Mauritius": "MU",
        "Namibia": "NA",
        "Botswana": "BW",
        "Zimbabwe": "ZW",
        "Zambia": "ZM",
        "Uganda": "UG",
        "Rwanda": "RW",
        "Angola": "AO",
        "Libya": "LY",
        "Sudan": "SD",
        "Algeria": "DZ",
        "Syria": "SY",
        "Yemen": "YE",
        "Turkmenistan": "TM",
        "Kyrgyzstan": "KG",
        "Tajikistan": "TJ",
    }

    code = country_codes.get(country_name)
    if code is None:
        print(f"Warning: unknown country '{country_name}', using 'XX'")
        return "XX"
    return code


if __name__ == "__main__":
    download_and_convert()
