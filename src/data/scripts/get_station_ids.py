"""Quick script to get station IDs."""

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

client = SNCFAPIClient(API_KEY)

stations_to_find = [
    "Paris Gare de l'Est",
    "Paris Est",
    "Metz",
    "Metz Ville",
    "Paris Gare du Nord",
    "Paris Nord",
    "London St Pancras",
    "London",
    "St Pancras"
]

print("Finding station IDs:")
for station_name in stations_to_find:
    station_id = client.get_station_id(station_name)
    if station_id:
        print(f"  ✓ {station_name}: {station_id}")
    else:
        print(f"  ✗ {station_name}: Not found")
