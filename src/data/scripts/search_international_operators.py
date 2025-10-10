"""Search for TGV Lyria and Frecciarossa trains in the SNCF network."""

import os
import sys
from datetime import datetime, time
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.sncf_api import SNCFAPIClient
from src.config.logger import get_logger

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")

logger = get_logger(__name__)

def search_operators():
    """Search for TGV Lyria and Frecciarossa trains."""
    client = SNCFAPIClient(API_KEY)

    # First, let's search for Swiss and Italian cities in the Navitia API
    # We need to find the station IDs that Navitia uses
    logger.info("Step 1: Finding station IDs for international cities in Navitia")

    international_cities = [
        "Genève", "Geneva", "Lausanne", "Zurich", "Zürich", "Basel", "Bâle",
        "Milano", "Milan", "Torino", "Turin", "Chambéry", "Annecy", "Bellegarde"
    ]

    found_stations = {}
    for city in international_cities:
        station_id = client.get_station_id(city)
        if station_id:
            found_stations[city] = station_id
            logger.info(f"  ✅ Found {city}: {station_id}")
        else:
            logger.info(f"  ❌ Not found: {city}")

    # Build search routes from what we found
    search_routes = []
    paris_gdl = "stop_area:SNCF:87686006"
    lyon_pd = "stop_area:SNCF:87723197"

    for city, station_id in found_stations.items():
        search_routes.append(("Paris Gare de Lyon", city, paris_gdl, station_id))
        search_routes.append(("Lyon Part-Dieu", city, lyon_pd, station_id))

    logger.info(f"\nBuilt {len(search_routes)} search routes")

    all_providers = Counter()
    lyria_found = False
    frecciarossa_found = False

    # Use today's date
    today = datetime.now()
    departure_time = datetime.combine(today.date(), time(6, 0))
    departure_filter = departure_time.strftime("%Y%m%dT%H%M%S")

    logger.info("=" * 80)
    logger.info("SEARCHING FOR TGV LYRIA AND FRECCIAROSSA")
    logger.info("=" * 80)

    for route_name_from, route_name_to, from_id, to_id in search_routes:
        logger.info(f"\nSearching: {route_name_from} → {route_name_to}")
        logger.info(f"Station IDs: {from_id} → {to_id}")

        try:
            journeys = client.get_journeys(
                from_id,
                to_id,
                count=50,
                datetime=departure_filter
            )

            logger.info(f"Retrieved {len(journeys)} journeys")

            # Analyze providers in these journeys
            for journey in journeys:
                for section in journey.get("sections", []):
                    if section.get("type") == "public_transport":
                        display_info = section.get("display_informations", {})
                        commercial_mode = display_info.get("commercial_mode", "N/A")
                        physical_mode = display_info.get("physical_mode", "N/A")
                        network = display_info.get("network", "N/A")
                        headsign = display_info.get("headsign", "N/A")

                        all_providers[commercial_mode] += 1

                        # Check for TGV Lyria or Frecciarossa
                        if "lyria" in commercial_mode.lower() or "lyria" in network.lower():
                            if not lyria_found:
                                logger.info(f"\n🎯 FOUND TGV LYRIA!")
                                logger.info(f"   Commercial mode: {commercial_mode}")
                                logger.info(f"   Physical mode: {physical_mode}")
                                logger.info(f"   Network: {network}")
                                logger.info(f"   Headsign: {headsign}")
                                lyria_found = True

                        if "frecciarossa" in commercial_mode.lower() or "frecciarossa" in network.lower():
                            if not frecciarossa_found:
                                logger.info(f"\n🎯 FOUND FRECCIAROSSA!")
                                logger.info(f"   Commercial mode: {commercial_mode}")
                                logger.info(f"   Physical mode: {physical_mode}")
                                logger.info(f"   Network: {network}")
                                logger.info(f"   Headsign: {headsign}")
                                frecciarossa_found = True

        except Exception as e:
            logger.warning(f"Error fetching journeys for this route: {e}")
            continue

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SEARCH SUMMARY")
    logger.info("=" * 80)
    logger.info(f"TGV Lyria found: {'✅ YES' if lyria_found else '❌ NO'}")
    logger.info(f"Frecciarossa found: {'✅ YES' if frecciarossa_found else '❌ NO'}")

    logger.info(f"\nAll providers discovered across international routes:")
    for provider, count in all_providers.most_common():
        logger.info(f"  • {provider}: {count} trains")

if __name__ == "__main__":
    search_operators()
