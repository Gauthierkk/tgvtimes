"""Inspect raw API response for a station to see all departures.

This script fetches all departures from a station using the Navitia departures
endpoint and prints the raw JSON response to help understand available data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")

# Configuration
STATION_NAME = "Paris Gare de Lyon"
STATION_ID = "stop_area:SNCF:87686006"

# Get project root for saving output
project_root = Path(__file__).parent.parent.parent.parent


def main():
    """Fetch and display all departures from a station."""
    print("=" * 80)
    print("RAW API DEPARTURES INSPECTOR")
    print("=" * 80)
    print(f"\nStation: {STATION_NAME}")
    print(f"Station ID: {STATION_ID}")
    print(f"Date: {datetime.now().date()}\n")

    # API endpoint for departures
    base_url = "https://api.navitia.io/v1/"
    headers = {"Authorization": API_KEY}

    # Get current time for from_datetime parameter
    now = datetime.now()
    from_datetime = now.strftime("%Y%m%dT%H%M%S")

    # Build departures endpoint URL
    url = f"{base_url}coverage/sncf/stop_areas/{STATION_ID}/departures"

    params = {
        "from_datetime": from_datetime,
        "count": 50,  # Get more departures
        "duration": 7200,  # Next 2 hours
    }

    try:
        print("Fetching departures from API...")
        print(f"URL: {url}")
        print(f"Parameters: {params}\n")

        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        departures = data.get("departures", [])

        print(f"✓ Retrieved {len(departures)} departures\n")

        if not departures:
            print("❌ No departures found")
            return

        print("=" * 80)
        print("FULL RAW JSON RESPONSE")
        print("=" * 80)
        print("\nShowing first departure in detail:\n")

        # Pretty print the first departure
        first_departure = departures[0]
        print(json.dumps(first_departure, indent=2, ensure_ascii=False))

        print("\n" + "=" * 80)
        print("DEPARTURE STRUCTURE OVERVIEW")
        print("=" * 80)
        print(f"\nTop-level keys in departure object:")
        for key in first_departure.keys():
            print(f"  • {key}")

        print("\n" + "=" * 80)
        print("ALL DEPARTURES SUMMARY")
        print("=" * 80)
        print()

        for idx, dep in enumerate(departures[:20], 1):  # Show first 20
            stop_date_time = dep.get("stop_date_time", {})
            departure_time = stop_date_time.get("departure_date_time", "N/A")

            # Get display information
            display_info = dep.get("display_informations", {})
            commercial_mode = display_info.get("commercial_mode", "N/A")
            physical_mode = display_info.get("physical_mode", "N/A")
            train_number = display_info.get("headsign", "N/A")
            direction = display_info.get("direction", "N/A")
            network = display_info.get("network", "N/A")

            # Get route information
            route = dep.get("route", {})
            route_name = route.get("name", "N/A")

            # Format departure time
            if departure_time != "N/A":
                dt = datetime.strptime(departure_time, "%Y%m%dT%H%M%S")
                departure_time = dt.strftime("%H:%M")

            print(f"Departure {idx}:")
            print(f"  Time: {departure_time}")
            print(f"  Train: {train_number}")
            print(f"  Operator: {commercial_mode}")
            print(f"  Type: {physical_mode}")
            print(f"  Network: {network}")
            print(f"  Direction: {direction}")
            print(f"  Route: {route_name}")
            print()

        if len(departures) > 20:
            print(f"... and {len(departures) - 20} more departures")
            print()

        print("=" * 80)
        print("SAVING FULL RESPONSE TO FILE")
        print("=" * 80)

        # Save all departures to a file for detailed inspection
        output_file = project_root / "raw_api_response.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved full API response to: {output_file}")
        print(f"  Contains {len(departures)} departures with all available data")
        print(f"  Plus metadata: links, pagination, context, etc.\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
