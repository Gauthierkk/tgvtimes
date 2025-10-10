"""Script to fetch station IDs from Navitia API and generate station config."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from backend import SNCFAPIClient

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")

# List of stations to fetch IDs for
STATIONS = [
    "Bordeaux",
    "Paris Montparnasse",
    "Aix-en-Provence TGV",
    "Paris Gare de Lyon",
    "Lyon Part-Dieu",
]


def fetch_station_ids_and_connections():
    """Fetch station IDs and determine connections between stations."""
    client = SNCFAPIClient(API_KEY)
    station_ids = {}

    # Step 1: Fetch all station IDs
    print("Step 1: Fetching station IDs...")
    for station_name in STATIONS:
        print(f"  Fetching ID for: {station_name}")
        station_id = client.get_station_id(station_name)
        if station_id:
            station_ids[station_name] = station_id
            print(f"    ✓ Found: {station_id}")
        else:
            print("    ✗ Not found")

    # Step 2: Check connections between all station pairs
    print("\nStep 2: Checking connections between stations...")
    station_config = {}

    for station_name, station_id in station_ids.items():
        connections = []
        print(f"\n  Checking connections from {station_name}:")

        for other_station_name, other_station_id in station_ids.items():
            if station_name == other_station_name:
                continue

            print(f"    Testing {station_name} -> {other_station_name}...", end=" ")
            try:
                journeys = client.get_journeys(station_id, other_station_id)
                # Filter for TGV trains only (no transfers, and high-speed train)
                # Physical mode is "Train grande vitesse" (high-speed train) for TGVs
                tgv_journeys = [
                    j for j in journeys
                    if j.get("nb_transfers", 0) == 0
                    and any(
                        section.get("type") == "public_transport"
                        and (
                            "grande vitesse" in section.get("display_informations", {}).get("physical_mode", "").lower()
                            or "TGV" in section.get("display_informations", {}).get("commercial_mode", "").upper()
                        )
                        for section in j.get("sections", [])
                    )
                ]
                if tgv_journeys:
                    connections.append(other_station_name)
                    print("✓ Connected (TGV)")
                else:
                    print("✗ No TGV connection")
            except Exception as e:
                print(f"✗ Error: {e}")

        station_config[station_name] = {
            "id": station_id,
            "connections": connections
        }

    # Save to data directory (parent of scripts folder)
    data_dir = Path(__file__).parent.parent

    # Save to JSON file
    config_file = data_dir / "stations.json"
    with open(config_file, "w") as f:
        json.dump(station_config, f, indent=2)

    print(f"\n✓ Station config saved to: {config_file}")
    print(f"  Total stations: {len(station_config)}")

    # Print summary
    print("\nConnection Summary:")
    for station_name, data in station_config.items():
        print(f"  {station_name}: {len(data['connections'])} connections")
        for connection in data['connections']:
            print(f"    → {connection}")


if __name__ == "__main__":
    fetch_station_ids_and_connections()
