"""Analyze departures from a station to discover all operators and train types.

This script fetches all departures from a station and analyzes them to find:
- All unique operators (commercial modes)
- All unique train types (physical modes)
- Networks and their frequencies
- Sample trains for each operator
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")

# Configuration
STATION_NAME = "Paris Gare de Lyon"
STATION_ID = "stop_area:SNCF:87686006"

# Get project root for saving output
project_root = Path(__file__).parent.parent.parent.parent


def analyze_departures(
    station_id: str, station_name: str, api_key: str, count: int = 100, duration: int = 14400
) -> dict[str, Any]:
    """Analyze departures from a station to find all operators and train types.

    Args:
        station_id: Navitia station ID (e.g., "stop_area:SNCF:87686006")
        station_name: Human-readable station name
        api_key: Navitia API key
        count: Number of departures to fetch (default: 100)
        duration: Time window in seconds (default: 14400 = 4 hours)

    Returns:
        Dictionary containing analysis results with:
        - station: dict with name and id
        - analysis_date: ISO timestamp
        - total_departures: int
        - operators: list of dicts with name, count, examples
        - physical_modes: list of dicts with name, count
        - networks: list of dicts with name, count
    """
    # API endpoint for departures
    base_url = "https://api.navitia.io/v1/"
    headers = {"Authorization": api_key}

    # Get current time for from_datetime parameter
    now = datetime.now()
    from_datetime = now.strftime("%Y%m%dT%H%M%S")

    # Build departures endpoint URL
    url = f"{base_url}coverage/sncf/stop_areas/{station_id}/departures"

    params = {
        "from_datetime": from_datetime,
        "count": count,
        "duration": duration,
    }

    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    departures = data.get("departures", [])

    if not departures:
        return {
            "station": {"name": station_name, "id": station_id},
            "analysis_date": datetime.now().isoformat(),
            "total_departures": 0,
            "operators": [],
            "physical_modes": [],
            "networks": [],
        }

    # Analyze departures to find all operators and types
    operators: Counter[str] = Counter()
    physical_modes: Counter[str] = Counter()
    networks: Counter[str] = Counter()
    operator_examples: dict[str, list[dict[str, str]]] = defaultdict(list)

    for dep in departures:
        display_info = dep.get("display_informations", {})
        commercial_mode = display_info.get("commercial_mode", "Unknown")
        physical_mode = display_info.get("physical_mode", "Unknown")
        network = display_info.get("network", "Unknown")
        train_number = display_info.get("headsign", "N/A")
        direction = display_info.get("direction", "N/A")

        operators[commercial_mode] += 1
        physical_modes[physical_mode] += 1
        networks[network] += 1

        # Store example for each operator (max 3)
        if len(operator_examples[commercial_mode]) < 3:
            stop_date_time = dep.get("stop_date_time", {})
            departure_time = stop_date_time.get("departure_date_time", "N/A")
            if departure_time != "N/A":
                dt = datetime.strptime(departure_time, "%Y%m%dT%H%M%S")
                departure_time = dt.strftime("%H:%M")

            operator_examples[commercial_mode].append(
                {
                    "time": departure_time,
                    "train": train_number,
                    "direction": direction,
                    "physical_mode": physical_mode,
                    "network": network,
                }
            )

    # Build analysis result
    return {
        "station": {"name": station_name, "id": station_id},
        "analysis_date": datetime.now().isoformat(),
        "total_departures": len(departures),
        "operators": [
            {"name": op, "count": count, "examples": operator_examples[op]}
            for op, count in operators.most_common()
        ],
        "physical_modes": [
            {"name": mode, "count": count} for mode, count in physical_modes.most_common()
        ],
        "networks": [{"name": net, "count": count} for net, count in networks.most_common()],
    }


def print_analysis(analysis: dict[str, Any]) -> None:
    """Print formatted analysis results to console.

    Args:
        analysis: Analysis dictionary from analyze_departures()
    """
    station = analysis["station"]

    print("=" * 80)
    print("OPERATOR & TRAIN TYPE ANALYSIS")
    print("=" * 80)
    print(f"\nStation: {station['name']}")
    print(f"Station ID: {station['id']}")
    print(f"Total departures: {analysis['total_departures']}\n")

    # Print operators
    print("=" * 80)
    print("OPERATORS (COMMERCIAL MODES)")
    print("=" * 80)
    print(f"\nFound {len(analysis['operators'])} unique operators:\n")

    for operator in analysis["operators"]:
        print(f"• {operator['name']}: {operator['count']} departures")
        for example in operator["examples"]:
            print(f"    {example['time']} - Train {example['train']} → {example['direction']}")
        print()

    # Print physical modes
    print("=" * 80)
    print("TRAIN TYPES (PHYSICAL MODES)")
    print("=" * 80)
    print(f"\nFound {len(analysis['physical_modes'])} unique train types:\n")

    for mode in analysis["physical_modes"]:
        print(f"• {mode['name']}: {mode['count']} departures")

    # Print networks
    print("\n" + "=" * 80)
    print("NETWORKS")
    print("=" * 80)
    print(f"\nFound {len(analysis['networks'])} unique networks:\n")

    for network in analysis["networks"]:
        print(f"• {network['name']}: {network['count']} departures")


def run_operator_analysis(
    station_id: str | None = None,
    station_name: str | None = None,
    api_key: str | None = None,
    count: int = 100,
    duration: int = 14400,
    save_to_file: bool = True,
) -> dict[str, Any] | None:
    """Run complete operator analysis for a station.

    Args:
        station_id: Navitia station ID (uses default if not provided)
        station_name: Human-readable station name (uses default if not provided)
        api_key: SNCF API key (uses environment variable if not provided)
        count: Number of departures to fetch (default: 100)
        duration: Time window in seconds (default: 14400 = 4 hours)
        save_to_file: Whether to save results to JSON file (default: True)

    Returns:
        Analysis dictionary, or None if error occurs
    """
    if api_key is None:
        api_key = API_KEY
    if station_id is None:
        station_id = STATION_ID
    if station_name is None:
        station_name = STATION_NAME

    if not api_key:
        print("ERROR: SNCF_API_KEY not found in environment")
        print("Please set it in your .env file")
        return None

    try:
        print("Fetching departures from API...")
        analysis = analyze_departures(
            station_id=station_id,
            station_name=station_name,
            api_key=api_key,
            count=count,
            duration=duration,
        )

        if analysis["total_departures"] == 0:
            print("No departures found")
            return None

        # Print formatted analysis
        print_analysis(analysis)

        # Save detailed analysis to JSON
        if save_to_file:
            print("\n" + "=" * 80)
            print("SAVING ANALYSIS TO FILE")
            print("=" * 80)

            output_file = project_root / "operator_analysis.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            print(f"\n✓ Saved analysis to: {output_file}")
            print("  Contains operator counts, examples, and train types\n")

        return analysis

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        return None


def main() -> None:
    """Main entry point for standalone execution."""
    run_operator_analysis()


if __name__ == "__main__":
    main()
