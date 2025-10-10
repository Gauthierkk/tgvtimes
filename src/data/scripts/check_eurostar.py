"""Check for Eurostar trains between Paris and London."""

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

client = SNCFAPIClient(API_KEY)

# Paris Gare du Nord to London St Pancras
paris_nord = "stop_area:SNCF:87271007"
london_stpancras = "stop_area:SNCF:70154005"

today = datetime.now()
departure_time = datetime.combine(today.date(), time(6, 0))
departure_filter = departure_time.strftime("%Y%m%dT%H%M%S")

print("=" * 80)
print("SEARCHING FOR EUROSTAR TRAINS")
print("=" * 80)
print(f"\nParis Gare du Nord → London St Pancras")
print(f"Station IDs: {paris_nord} → {london_stpancras}\n")

try:
    journeys = client.get_journeys(
        paris_nord,
        london_stpancras,
        count=50,
        datetime=departure_filter
    )

    print(f"Retrieved {len(journeys)} journeys\n")

    eurostar_found = False
    providers = set()

    for journey in journeys:
        for section in journey.get("sections", []):
            if section.get("type") == "public_transport":
                display_info = section.get("display_informations", {})
                commercial_mode = display_info.get("commercial_mode", "N/A")
                physical_mode = display_info.get("physical_mode", "N/A")
                network = display_info.get("network", "N/A")
                headsign = display_info.get("headsign", "N/A")

                providers.add(commercial_mode)

                if "eurostar" in commercial_mode.lower() or "eurostar" in network.lower():
                    if not eurostar_found:
                        print("🎯 FOUND EUROSTAR!")
                        print(f"   Commercial mode: {commercial_mode}")
                        print(f"   Physical mode: {physical_mode}")
                        print(f"   Network: {network}")
                        print(f"   Headsign: {headsign}\n")
                        eurostar_found = True

    print("=" * 80)
    print("SEARCH SUMMARY")
    print("=" * 80)
    print(f"Eurostar found: {'✅ YES' if eurostar_found else '❌ NO'}")
    print(f"\nAll providers on this route:")
    for provider in sorted(providers):
        print(f"  • {provider}")

except Exception as e:
    print(f"Error: {e}")
