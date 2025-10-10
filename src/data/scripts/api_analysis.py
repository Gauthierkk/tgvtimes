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
    """Fetch and analyze all departures from a station."""
    print("=" * 80)
    print("OPERATOR & TRAIN TYPE ANALYSIS")
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
        "count": 100,  # Get many departures for better analysis
        "duration": 14400,  # Next 4 hours
    }

    try:
        print("Fetching departures from API...")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        departures = data.get("departures", [])

        print(f"✓ Retrieved {len(departures)} departures\n")

        if not departures:
            print("❌ No departures found")
            return

        # Analyze departures to find all operators and types
        operators = Counter()
        physical_modes = Counter()
        networks = Counter()
        operator_examples = defaultdict(list)

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

                operator_examples[commercial_mode].append({
                    "time": departure_time,
                    "train": train_number,
                    "direction": direction,
                    "physical_mode": physical_mode,
                    "network": network
                })

        # Print analysis results
        print("=" * 80)
        print("OPERATORS (COMMERCIAL MODES)")
        print("=" * 80)
        print(f"\nFound {len(operators)} unique operators:\n")

        for operator, count in operators.most_common():
            print(f"• {operator}: {count} departures")
            for example in operator_examples[operator]:
                print(f"    {example['time']} - Train {example['train']} → {example['direction']}")
            print()

        print("=" * 80)
        print("TRAIN TYPES (PHYSICAL MODES)")
        print("=" * 80)
        print(f"\nFound {len(physical_modes)} unique train types:\n")

        for mode, count in physical_modes.most_common():
            print(f"• {mode}: {count} departures")

        print("\n" + "=" * 80)
        print("NETWORKS")
        print("=" * 80)
        print(f"\nFound {len(networks)} unique networks:\n")

        for network, count in networks.most_common():
            print(f"• {network}: {count} departures")

        # Save detailed analysis to JSON
        print("\n" + "=" * 80)
        print("SAVING ANALYSIS TO FILE")
        print("=" * 80)

        analysis = {
            "station": {
                "name": STATION_NAME,
                "id": STATION_ID
            },
            "analysis_date": datetime.now().isoformat(),
            "total_departures": len(departures),
            "operators": [
                {
                    "name": op,
                    "count": count,
                    "examples": operator_examples[op]
                }
                for op, count in operators.most_common()
            ],
            "physical_modes": [
                {"name": mode, "count": count}
                for mode, count in physical_modes.most_common()
            ],
            "networks": [
                {"name": net, "count": count}
                for net, count in networks.most_common()
            ]
        }

        output_file = project_root / "operator_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved analysis to: {output_file}")
        print(f"  Contains operator counts, examples, and train types\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
