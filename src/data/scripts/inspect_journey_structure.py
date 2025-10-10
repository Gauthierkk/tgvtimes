"""Script to inspect the structure of journey data from Navitia API."""

import json
import os

from dotenv import load_dotenv

from backend import SNCFAPIClient

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")


def inspect_journey_structure():
    """Fetch a sample journey and print its structure."""
    client = SNCFAPIClient(API_KEY)

    # Test with Paris Gare de Lyon to Lyon Part-Dieu
    departure_id = "stop_area:SNCF:87686006"  # Paris Gare de Lyon
    arrival_id = "stop_area:SNCF:87723197"  # Lyon Part-Dieu

    print("Fetching journeys from Paris Gare de Lyon to Lyon Part-Dieu...")
    journeys = client.get_journeys(departure_id, arrival_id)

    if journeys:
        print(f"\nFound {len(journeys)} journeys")
        print("\nInspecting first journey structure:")
        print("=" * 80)
        print(json.dumps(journeys[0], indent=2))
    else:
        print("No journeys found")


if __name__ == "__main__":
    inspect_journey_structure()
