"""Utility functions for the TGV Times dashboard."""

from datetime import datetime

import pandas as pd


def calculate_delay_minutes(scheduled_time: str, actual_time: str) -> int:
    """Calculate delay in minutes between scheduled and actual times."""
    scheduled = datetime.strptime(scheduled_time, "%Y%m%dT%H%M%S")
    actual = datetime.strptime(actual_time, "%Y%m%dT%H%M%S")
    delay_seconds = (actual - scheduled).total_seconds()
    return int(delay_seconds / 60)


def format_journey_data(journeys: list) -> tuple[pd.DataFrame, list]:
    """Convert journey data to a pandas DataFrame and keep full journey data.

    Returns:
        Tuple of (DataFrame for display, list of full journey objects)
    """
    data = []
    for idx, journey in enumerate(journeys):
        departure_time = datetime.strptime(
            journey["departure_date_time"], "%Y%m%dT%H%M%S"
        )
        arrival_time = datetime.strptime(
            journey["arrival_date_time"], "%Y%m%dT%H%M%S"
        )

        # Extract station names and provider from sections
        sections = journey.get("sections", [])
        departure_station = "N/A"
        arrival_station = "N/A"
        train_number = "N/A"
        provider = "N/A"

        for section in sections:
            if section.get("type") == "public_transport":
                departure_station = section.get("from", {}).get("stop_point", {}).get("name", "N/A")
                arrival_station = section.get("to", {}).get("stop_point", {}).get("name", "N/A")
                train_number = section.get("display_informations", {}).get("headsign", "N/A")
                provider = section.get("display_informations", {}).get("commercial_mode", "N/A")
                break

        # Get base (scheduled) times if available
        base_departure = journey.get("sections", [{}])[1].get("base_departure_date_time") if len(journey.get("sections", [])) > 1 else None
        base_arrival = journey.get("sections", [{}])[1].get("base_arrival_date_time") if len(journey.get("sections", [])) > 1 else None

        # Calculate delays
        departure_delay = 0
        arrival_delay = 0
        if base_departure:
            departure_delay = calculate_delay_minutes(base_departure, journey["departure_date_time"])
        if base_arrival:
            arrival_delay = calculate_delay_minutes(base_arrival, journey["arrival_date_time"])

        duration_seconds = journey["duration"]
        duration_minutes = duration_seconds // 60
        duration_hours = duration_minutes // 60
        duration_mins = duration_minutes % 60

        data.append({
            "ID": idx,
            "Provider": provider,
            "Train": train_number,
            "From": departure_station,
            "To": arrival_station,
            "Departure": departure_time.strftime("%H:%M"),
            "Arrival": arrival_time.strftime("%H:%M"),
            "Duration": f"{duration_hours}h{duration_mins:02d}",
            "Dep. Delay": departure_delay,
            "Arr. Delay": arrival_delay,
            "Status": "Delayed" if (departure_delay > 5 or arrival_delay > 5) else "On Time",
        })

    return pd.DataFrame(data), journeys


def apply_row_styling(row):
    """Apply conditional styling to DataFrame rows based on delay."""
    if row["Status"] == "Delayed":
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)


def filter_tgv_journeys(journeys: list, provider_filter: str | None = None) -> list:
    """Filter for direct high-speed trains with optional provider filtering.

    Accepts all high-speed trains including:
    - TGV INOUI (standard SNCF)
    - OUIGO (low-cost SNCF)
    - DB SNCF (Germany-France)
    - Trenitalia (Italian high-speed)
    - Renfe (Spanish high-speed)
    - Any other "Train grande vitesse" (high-speed train)

    Args:
        journeys: List of journey dictionaries from Navitia API
        provider_filter: Optional provider name to filter by (e.g., "TGV INOUI", "OUIGO")
                        If None or "All", returns all high-speed trains

    Returns:
        Filtered list of journey dictionaries
    """
    filtered = []
    for j in journeys:
        # Skip journeys with transfers
        if j.get("nb_transfers", 0) != 0:
            continue

        # Check for high-speed train in sections
        for section in j.get("sections", []):
            if section.get("type") == "public_transport":
                display_info = section.get("display_informations", {})
                physical_mode = display_info.get("physical_mode", "").lower()

                # Accept any high-speed train based on physical mode
                # This automatically includes TGV, Trenitalia, Renfe, DB ICE, etc.
                is_high_speed = "grande vitesse" in physical_mode or "high speed" in physical_mode

                if is_high_speed:
                    # Apply provider filter if specified
                    if provider_filter and provider_filter != "All":
                        if display_info.get("commercial_mode") == provider_filter:
                            filtered.append(j)
                    else:
                        filtered.append(j)
                break

    return filtered


def get_available_providers(journeys: list) -> list[str]:
    """Extract unique providers from a list of journeys.

    Args:
        journeys: List of journey dictionaries

    Returns:
        Sorted list of unique provider names
    """
    providers = set()
    for j in journeys:
        for section in j.get("sections", []):
            if section.get("type") == "public_transport":
                provider = section.get("display_informations", {}).get("commercial_mode")
                if provider:
                    providers.add(provider)
                break
    return sorted(providers)
