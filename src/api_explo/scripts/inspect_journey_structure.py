"""Functions to inspect the structure of journey data from Navitia API."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.sncf_api import SNCFAPIClient

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")


def inspect_journey_structure(
    departure_id: str = "stop_area:SNCF:87686006",
    arrival_id: str = "stop_area:SNCF:87723197",
    api_key: str | None = None,
) -> dict | None:
    """Fetch a sample journey and return its structure.

    Args:
        departure_id: Navitia station ID for departure (default: Paris Gare de Lyon)
        arrival_id: Navitia station ID for arrival (default: Lyon Part-Dieu)
        api_key: SNCF API key (uses environment variable if not provided)

    Returns:
        First journey data structure as dict, or None if no journeys found
    """
    if api_key is None:
        api_key = API_KEY

    client = SNCFAPIClient(api_key)

    print(f"Fetching journeys from {departure_id} to {arrival_id}...")
    journeys = client.get_journeys(departure_id, arrival_id)

    if journeys:
        print(f"\nFound {len(journeys)} journeys")
        return journeys[0]
    else:
        print("No journeys found")
        return None


def print_journey_structure(journey: dict) -> None:
    """Print formatted journey structure.

    Args:
        journey: Journey data structure from Navitia API
    """
    print("\nInspecting journey structure:")
    print("=" * 80)
    print(json.dumps(journey, indent=2))


if __name__ == "__main__":
    journey = inspect_journey_structure()
    if journey:
        print_journey_structure(journey)
