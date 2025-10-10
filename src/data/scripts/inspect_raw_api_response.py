"""Inspect raw API response for a station to see all available train data.

This script fetches journeys from a station and prints the raw JSON response
to help understand the API structure and available data fields.
"""

import json
import os
import sys
from datetime import datetime, time
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.sncf_api import SNCFAPIClient
from src.config.logger import get_logger

load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")

logger = get_logger(__name__)

# Configuration
STATION_NAME = "Paris Gare de Lyon"
STATION_ID = "stop_area:SNCF:87686006"
DESTINATION_NAME = "Lyon Part-Dieu"
DESTINATION_ID = "stop_area:SNCF:87723197"


def main():
    """Fetch and display raw API response for a station."""
    print("=" * 80)
    print(f"RAW API RESPONSE INSPECTOR")
    print("=" * 80)
    print(f"\nStation: {STATION_NAME} ({STATION_ID})")
    print(f"Destination: {DESTINATION_NAME} ({DESTINATION_ID})")
    print(f"Date: {datetime.now().date()}\n")

    client = SNCFAPIClient(API_KEY)

    # Get journeys for today
    today = datetime.now()
    departure_time = datetime.combine(today.date(), time(8, 0))
    datetime_filter = departure_time.strftime("%Y%m%dT%H%M%S")

    try:
        print("Fetching journeys from API...")
        journeys = client.get_journeys(
            STATION_ID,
            DESTINATION_ID,
            count=5,  # Just get 5 journeys for inspection
            datetime=datetime_filter
        )

        print(f"✓ Retrieved {len(journeys)} journeys\n")

        if not journeys:
            print("❌ No journeys found")
            return

        print("=" * 80)
        print("FULL RAW JSON RESPONSE")
        print("=" * 80)
        print("\nShowing first journey in detail:\n")

        # Pretty print the first journey
        first_journey = journeys[0]
        print(json.dumps(first_journey, indent=2, ensure_ascii=False))

        print("\n" + "=" * 80)
        print("JOURNEY STRUCTURE OVERVIEW")
        print("=" * 80)
        print(f"\nTop-level keys in journey object:")
        for key in first_journey.keys():
            print(f"  • {key}")

        print("\n" + "=" * 80)
        print("SECTIONS BREAKDOWN")
        print("=" * 80)

        sections = first_journey.get("sections", [])
        print(f"\nNumber of sections: {len(sections)}\n")

        for idx, section in enumerate(sections):
            section_type = section.get("type", "N/A")
            print(f"Section {idx + 1}: {section_type}")

            if section_type == "public_transport":
                display_info = section.get("display_informations", {})
                print(f"  Commercial mode: {display_info.get('commercial_mode', 'N/A')}")
                print(f"  Physical mode: {display_info.get('physical_mode', 'N/A')}")
                print(f"  Network: {display_info.get('network', 'N/A')}")
                print(f"  Train number: {display_info.get('headsign', 'N/A')}")
                print(f"  Direction: {display_info.get('direction', 'N/A')}")

                # From/To information
                from_info = section.get("from", {})
                to_info = section.get("to", {})
                print(f"  From: {from_info.get('stop_point', {}).get('name', 'N/A')}")
                print(f"  To: {to_info.get('stop_point', {}).get('name', 'N/A')}")

                # Times
                print(f"  Departure: {section.get('departure_date_time', 'N/A')}")
                print(f"  Arrival: {section.get('arrival_date_time', 'N/A')}")

                # Base times (scheduled)
                base_dep = section.get('base_departure_date_time')
                base_arr = section.get('base_arrival_date_time')
                if base_dep:
                    print(f"  Base departure: {base_dep}")
                if base_arr:
                    print(f"  Base arrival: {base_arr}")

            print()

        print("=" * 80)
        print("SAVING FULL RESPONSE TO FILE")
        print("=" * 80)

        # Save all journeys to a file for detailed inspection
        output_file = project_root / "raw_api_response.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(journeys, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved full response to: {output_file}")
        print(f"  Contains {len(journeys)} journeys with all available data\n")

    except Exception as e:
        logger.error(f"Error fetching data: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
