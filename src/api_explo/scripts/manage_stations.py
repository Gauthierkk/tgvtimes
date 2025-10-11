"""Functions for station management in TGV Times.

This module provides utilities to:
1. Look up station IDs by name
2. Check connections between stations
"""

import os
import sys
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


def lookup_station_ids(station_names: list[str], api_key: str | None = None) -> dict[str, str]:
    """Look up station IDs for given station names.

    Args:
        station_names: List of station names to look up
        api_key: SNCF API key (uses environment variable if not provided)

    Returns:
        Dictionary mapping station names to their Navitia IDs
    """
    if api_key is None:
        api_key = API_KEY

    client = SNCFAPIClient(api_key)

    results = {}
    for station_name in station_names:
        station_id = client.get_station_id(station_name)
        if station_id:
            results[station_name] = station_id

    return results


def check_connection(
    client: SNCFAPIClient, from_id: str, to_id: str, from_name: str, to_name: str
) -> bool:
    """Check if there's a high-speed connection between two stations.

    Args:
        client: SNCF API client instance
        from_id: Navitia ID for departure station
        to_id: Navitia ID for arrival station
        from_name: Name of departure station (for logging)
        to_name: Name of arrival station (for logging)

    Returns:
        True if high-speed connection exists, False otherwise
    """
    try:
        journeys = client.get_journeys(from_id, to_id, count=10)
        # Filter for high-speed trains (no transfers)
        hs_journeys = [
            j
            for j in journeys
            if j.get("nb_transfers", 0) == 0
            and any(
                section.get("type") == "public_transport"
                and (
                    "grande vitesse"
                    in section.get("display_informations", {}).get("physical_mode", "").lower()
                    or "high speed"
                    in section.get("display_informations", {}).get("physical_mode", "").lower()
                )
                for section in j.get("sections", [])
            )
        ]
        return len(hs_journeys) > 0
    except Exception as e:
        logger.debug(f"Error checking {from_name} -> {to_name}: {e}")
        return False


def print_station_lookup(station_names: list[str]) -> None:
    """Print formatted station ID lookup results.

    Args:
        station_names: List of station names to look up
    """
    print("=" * 80)
    print("STATION ID LOOKUP")
    print("=" * 80)
    print()

    results = lookup_station_ids(station_names)

    for station_name in station_names:
        print(f"Looking up: {station_name}")
        if station_name in results:
            print(f"  ✓ Found: {results[station_name]}")
        else:
            print("  ✗ Not found")
        print()

    return results


if __name__ == "__main__":
    # Example usage
    test_stations = ["Paris Gare de Lyon", "Lyon Part-Dieu", "Marseille Saint-Charles"]
    print_station_lookup(test_stations)
