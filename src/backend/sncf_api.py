"""SNCF API client for querying train schedules via Navitia API."""

from typing import Any

import requests

from config import get_logger

# Set up logging
logger = get_logger(__name__)


class SNCFAPIClient:
    """Client for interacting with the Navitia SNCF API."""

    def __init__(self, api_key: str):
        """
        Initialize the SNCF API client.

        Args:
            api_key: Navitia API key for authentication
        """
        self.api_key = api_key
        self.base_url = "https://api.navitia.io/v1/"
        self.headers = {"Authorization": api_key}

    def get_station_id(self, station_name: str) -> str | None:
        """
        Get the station ID from the station name.

        Args:
            station_name: Name of the station to search for

        Returns:
            Station ID if found, None otherwise
        """
        try:
            logger.debug(f"Searching for station: {station_name}")
            response = requests.get(
                f"{self.base_url}coverage/sncf/places?q={station_name}&type[]=stop_area",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            places = response.json().get("places")
            if places:
                station_id = places[0]["id"]
                logger.debug(f"Found station ID: {station_id} for {station_name}")
                return station_id
            logger.warning(f"No station found for: {station_name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API error while searching for station {station_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while searching for station {station_name}: {e}")
            raise

    def get_journeys(
        self,
        departure_station_id: str,
        arrival_station_id: str,
        count: int = 20,
        datetime: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get journey information between two stations.

        Args:
            departure_station_id: ID of the departure station
            arrival_station_id: ID of the arrival station
            count: Number of journeys to retrieve (default: 20)
            datetime: Optional datetime string in format YYYYMMDDTHHmmss

        Returns:
            List of journey dictionaries with schedule information
        """
        try:
            logger.debug(f"Fetching journeys from {departure_station_id} to {arrival_station_id}")
            logger.debug(f"Parameters: count={count}, datetime={datetime}")

            params = {
                "from": departure_station_id,
                "to": arrival_station_id,
                "count": count,
                "data_freshness": "realtime",  # Request real-time data when available
            }
            if datetime:
                params["datetime"] = datetime

            response = requests.get(
                f"{self.base_url}coverage/sncf/journeys",
                headers=self.headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()

            journeys = response.json().get("journeys", [])
            logger.debug(f"Successfully retrieved {len(journeys)} journeys")
            return journeys

        except requests.exceptions.Timeout:
            logger.error("Request timed out while fetching journeys")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API error while fetching journeys: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching journeys: {e}")
            raise

    def search_train_by_number(
        self,
        train_number: str,
        stations: list[str],
        datetime: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for trains by train number across all station pairs.

        Args:
            train_number: Train number to search for (e.g., "6611")
            stations: List of station IDs to search through
            datetime: Optional datetime string in format YYYYMMDDTHHmmss

        Returns:
            List of matching journey dictionaries
        """
        try:
            logger.info(f"Searching for train number: {train_number}")
            matching_journeys = []

            # Search through all possible station pairs
            for dep_idx, departure_id in enumerate(stations):
                for arrival_id in stations[dep_idx + 1:]:
                    try:
                        journeys = self.get_journeys(
                            departure_id,
                            arrival_id,
                            count=50,
                            datetime=datetime
                        )

                        # Filter for matching train number
                        for journey in journeys:
                            for section in journey.get("sections", []):
                                if section.get("type") == "public_transport":
                                    display_info = section.get("display_informations", {})
                                    headsign = display_info.get("headsign", "")
                                    if train_number.upper() in headsign.upper():
                                        matching_journeys.append(journey)
                                        break

                    except Exception as e:
                        logger.debug(f"No journeys found for {departure_id} to {arrival_id}: {e}")
                        continue

            msg = f"Found {len(matching_journeys)} journeys matching train number"
            logger.info(f"{msg} {train_number}")
            return matching_journeys

        except Exception as e:
            logger.error(f"Error searching for train number {train_number}: {e}")
            raise
