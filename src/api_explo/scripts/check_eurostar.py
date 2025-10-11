"""Functions to check for Eurostar trains between Paris and London."""

import os
import sys
from datetime import datetime, time
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.sncf_api import SNCFAPIClient

load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")


def check_eurostar_trains(
    paris_nord: str = "stop_area:SNCF:87271007",
    london_stpancras: str = "stop_area:SNCF:70154005",
    api_key: str | None = None,
    departure_hour: int = 6,
    count: int = 50,
) -> dict:
    """Check for Eurostar trains between Paris and London.

    Args:
        paris_nord: Navitia station ID for Paris Gare du Nord
        london_stpancras: Navitia station ID for London St Pancras
        api_key: SNCF API key (uses environment variable if not provided)
        departure_hour: Hour to start search from (default: 6)
        count: Number of journeys to fetch (default: 50)

    Returns:
        Dictionary with:
            - eurostar_found: bool
            - providers: set of commercial modes found
            - journey_count: number of journeys found
            - sample_eurostar: dict with details if found
    """
    if api_key is None:
        api_key = API_KEY

    client = SNCFAPIClient(api_key)

    today = datetime.now()
    departure_time = datetime.combine(today.date(), time(departure_hour, 0))
    departure_filter = departure_time.strftime("%Y%m%dT%H%M%S")

    journeys = client.get_journeys(
        paris_nord, london_stpancras, count=count, datetime=departure_filter
    )

    eurostar_found = False
    providers = set()
    sample_eurostar = None

    for journey in journeys:
        for section in journey.get("sections", []):
            if section.get("type") == "public_transport":
                display_info = section.get("display_informations", {})
                commercial_mode = display_info.get("commercial_mode", "N/A")

                providers.add(commercial_mode)

                if "eurostar" in commercial_mode.lower():
                    if not eurostar_found:
                        sample_eurostar = {
                            "commercial_mode": commercial_mode,
                            "physical_mode": display_info.get("physical_mode", "N/A"),
                            "network": display_info.get("network", "N/A"),
                            "headsign": display_info.get("headsign", "N/A"),
                        }
                        eurostar_found = True

    return {
        "eurostar_found": eurostar_found,
        "providers": providers,
        "journey_count": len(journeys),
        "sample_eurostar": sample_eurostar,
    }


def print_eurostar_check(
    paris_nord: str = "stop_area:SNCF:87271007", london_stpancras: str = "stop_area:SNCF:70154005"
) -> None:
    """Print formatted check for Eurostar trains.

    Args:
        paris_nord: Navitia station ID for Paris Gare du Nord
        london_stpancras: Navitia station ID for London St Pancras
    """
    print("=" * 80)
    print("SEARCHING FOR EUROSTAR TRAINS")
    print("=" * 80)
    print("\nParis Gare du Nord → London St Pancras")
    print(f"Station IDs: {paris_nord} → {london_stpancras}\n")

    result = check_eurostar_trains(paris_nord, london_stpancras)

    print(f"Retrieved {result['journey_count']} journeys\n")

    if result["eurostar_found"] and result["sample_eurostar"]:
        print("🎯 FOUND EUROSTAR!")
        sample = result["sample_eurostar"]
        print(f"   Commercial mode: {sample['commercial_mode']}")
        print(f"   Physical mode: {sample['physical_mode']}")
        print(f"   Network: {sample['network']}")
        print(f"   Headsign: {sample['headsign']}\n")

    print("=" * 80)
    print("SEARCH SUMMARY")
    print("=" * 80)
    print(f"Eurostar found: {'✅ YES' if result['eurostar_found'] else '❌ NO'}")
    print("\nAll providers on this route:")
    for provider in sorted(result["providers"]):
        print(f"  • {provider}")


if __name__ == "__main__":
    print_eurostar_check()
