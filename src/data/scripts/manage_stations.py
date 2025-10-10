"""Station management script for TGV Times.

This script provides utilities to:
1. Look up station IDs by name
2. Generate station configuration with connections
3. Update stations.json with new stations

Usage:
  # Look up station IDs
  uv run python src/data/scripts/manage_stations.py lookup "Paris Gare du Nord" "Lyon"

  # Generate full station config from list
  uv run python src/data/scripts/manage_stations.py generate

  # Add single station with manual connections
  uv run python src/data/scripts/manage_stations.py add "Station Name" --connections "Station1,Station2"
"""

import argparse
import json
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

# Default stations list for full generation
DEFAULT_STATIONS = [
    "Bordeaux",
    "Paris Montparnasse",
    "Aix-en-Provence TGV",
    "Paris Gare de Lyon",
    "Lyon Part-Dieu",
    "Paris Gare de l'Est",
    "Metz",
    "Paris Gare du Nord",
    "London St Pancras",
]


def lookup_station_ids(station_names: list[str]):
    """Look up station IDs for given station names."""
    client = SNCFAPIClient(API_KEY)

    print("=" * 80)
    print("STATION ID LOOKUP")
    print("=" * 80)
    print()

    results = {}
    for station_name in station_names:
        print(f"Looking up: {station_name}")
        station_id = client.get_station_id(station_name)
        if station_id:
            results[station_name] = station_id
            print(f"  ✓ Found: {station_id}")
        else:
            print(f"  ✗ Not found")
        print()

    return results


def check_connection(client, from_id, to_id, from_name, to_name):
    """Check if there's a high-speed connection between two stations."""
    try:
        journeys = client.get_journeys(from_id, to_id, count=10)
        # Filter for high-speed trains (no transfers)
        hs_journeys = [
            j for j in journeys
            if j.get("nb_transfers", 0) == 0
            and any(
                section.get("type") == "public_transport"
                and (
                    "grande vitesse" in section.get(
                        "display_informations", {}
                    ).get("physical_mode", "").lower()
                    or "high speed" in section.get(
                        "display_informations", {}
                    ).get("physical_mode", "").lower()
                )
                for section in j.get("sections", [])
            )
        ]
        return len(hs_journeys) > 0
    except Exception as e:
        logger.debug(f"Error checking {from_name} -> {to_name}: {e}")
        return False


def generate_station_config(stations: list[str] = None):
    """Generate complete station configuration with connections."""
    if stations is None:
        stations = DEFAULT_STATIONS

    client = SNCFAPIClient(API_KEY)

    print("=" * 80)
    print("GENERATING STATION CONFIGURATION")
    print("=" * 80)
    print()

    # Step 1: Fetch all station IDs
    print("Step 1: Fetching station IDs...")
    station_ids = {}

    for station_name in stations:
        print(f"  Fetching ID for: {station_name}")
        station_id = client.get_station_id(station_name)
        if station_id:
            station_ids[station_name] = station_id
            print(f"    ✓ Found: {station_id}")
        else:
            print(f"    ✗ Not found")

    # Step 2: Check connections between all station pairs
    print("\nStep 2: Checking high-speed connections...")
    station_config = {}

    for station_name, station_id in station_ids.items():
        connections = []
        print(f"\n  Checking connections from {station_name}:")

        for other_station_name, other_station_id in station_ids.items():
            if station_name == other_station_name:
                continue

            print(f"    Testing {station_name} -> {other_station_name}...", end=" ")
            if check_connection(
                client, station_id, other_station_id, station_name, other_station_name
            ):
                connections.append(other_station_name)
                print("✓ Connected")
            else:
                print("✗ No connection")

        # Determine country code from station ID
        country = "FR"  # Default to France
        if "70154005" in station_id:  # London St Pancras
            country = "GB"

        station_config[station_name] = {
            "id": station_id,
            "country": country,
            "connections": connections
        }

    # Save to stations.json
    data_dir = Path(__file__).parent.parent
    config_file = data_dir / "stations.json"

    with open(config_file, "w") as f:
        json.dump(station_config, f, indent=2)

    print(f"\n✓ Station config saved to: {config_file}")
    print(f"  Total stations: {len(station_config)}")

    # Print summary
    print("\nConnection Summary:")
    for station_name, data in station_config.items():
        country_flag = "🇬🇧" if data["country"] == "GB" else "🇫🇷"
        print(f"  {country_flag} {station_name}: {len(data['connections'])} connections")
        for connection in data['connections']:
            print(f"    → {connection}")


def add_station(station_name: str, connections: list[str] = None):
    """Add a single station to the configuration."""
    client = SNCFAPIClient(API_KEY)

    print("=" * 80)
    print(f"ADDING STATION: {station_name}")
    print("=" * 80)
    print()

    # Get station ID
    print("Fetching station ID...")
    station_id = client.get_station_id(station_name)

    if not station_id:
        print(f"✗ Station '{station_name}' not found in Navitia API")
        return

    print(f"✓ Found ID: {station_id}")

    # Load existing config
    data_dir = Path(__file__).parent.parent
    config_file = data_dir / "stations.json"

    try:
        with open(config_file, "r") as f:
            station_config = json.load(f)
    except FileNotFoundError:
        station_config = {}

    # Determine country
    country = "FR"
    if "70154005" in station_id:
        country = "GB"

    # Add station
    station_config[station_name] = {
        "id": station_id,
        "country": country,
        "connections": connections or []
    }

    # Save
    with open(config_file, "w") as f:
        json.dump(station_config, f, indent=2)

    print(f"\n✓ Added '{station_name}' to {config_file}")
    print(f"  Connections: {connections or 'None'}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Station management for TGV Times",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up station IDs")
    lookup_parser.add_argument(
        "stations",
        nargs="+",
        help="Station names to look up"
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate full station configuration"
    )
    generate_parser.add_argument(
        "--stations",
        nargs="+",
        help="Custom list of stations (uses defaults if not provided)"
    )

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a single station")
    add_parser.add_argument("name", help="Station name")
    add_parser.add_argument(
        "--connections",
        help="Comma-separated list of connected stations"
    )

    args = parser.parse_args()

    if not API_KEY:
        print("❌ Error: SNCF_API_KEY not found in environment")
        print("Please set it in your .env file")
        sys.exit(1)

    if args.command == "lookup":
        lookup_station_ids(args.stations)
    elif args.command == "generate":
        generate_station_config(args.stations)
    elif args.command == "add":
        connections = args.connections.split(",") if args.connections else None
        add_station(args.name, connections)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
