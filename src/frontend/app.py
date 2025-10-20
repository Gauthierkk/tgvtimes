"""Streamlit UI for TGV Times train schedule application."""

import json
import os
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
from dotenv import load_dotenv

from backend import SNCFAPIClient
from config import get_logger
from frontend.utils import (
    apply_row_styling,
    filter_tgv_journeys,
    format_journey_data,
)

# Load environment variables from .env (local) or Streamlit secrets (cloud)
load_dotenv()
try:
    # Try Streamlit secrets first (for cloud deployment)
    API_KEY = st.secrets.get("SNCF_API_KEY")
except (AttributeError, FileNotFoundError):
    # Fall back to environment variable (for local development)
    API_KEY = os.getenv("SNCF_API_KEY")

# Set up logging
logger = get_logger(__name__)

# Use Paris timezone for all train schedules (regardless of server location)
PARIS_TZ = ZoneInfo("Europe/Paris")


def load_station_config():
    """Load station configuration from JSON file."""
    try:
        config_path = Path(__file__).parent.parent / "config" / "appdata" / "stations.json"
        logger.debug(f"Loading station config from: {config_path}")
        with open(config_path) as f:
            config = json.load(f)
        logger.info(f"Successfully loaded {len(config)} stations")
        return config
    except FileNotFoundError:
        logger.error(f"Station configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in station configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading station configuration: {e}")
        raise


try:
    STATION_CONFIG = load_station_config()
except Exception as e:
    logger.critical(f"Failed to load station configuration: {e}")
    STATION_CONFIG = {}


def main():
    """Main Streamlit application entry point."""
    logger.info("Starting TGV Times Dashboard")

    st.set_page_config(page_title="High-Speed Rail Station Board", layout="wide")
    st.title("High-Speed Rail Station Board")

    # Check if API key is configured
    if not API_KEY:
        logger.error("API key not configured")
        st.error("API key not configured. Please set SNCF_API_KEY in your .env file.")
        return

    # Check if station config is loaded
    if not STATION_CONFIG:
        logger.error("Station configuration not loaded")
        st.error("Station configuration not loaded. Please check the logs.")
        return

    # Initialize API client
    try:
        client = SNCFAPIClient(API_KEY)
        logger.debug("API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        st.error(f"Failed to initialize API client: {e}")
        return

    # Get list of stations from config
    all_stations = list(STATION_CONFIG.keys())
    logger.debug(f"Loaded {len(all_stations)} total stations")

    # Sidebar filters
    st.sidebar.header("Search Mode")
    search_mode = st.sidebar.radio("Search by:", ["Station Board", "Train Number"], index=0)

    st.sidebar.header("Filters")

    if search_mode == "Station Board":
        # Single station selection
        selected_station = st.sidebar.selectbox("Select Station:", all_stations, index=3)

        # Departure or Arrival toggle
        board_type = st.sidebar.radio("Show:", ["Departures", "Arrivals"], index=0)

        # Get list of connected stations for filtering
        connections = STATION_CONFIG[selected_station].get("connections", [])

        # Add "All" option to the connections list
        filter_options = ["All", *connections]

        # Filter by origin/destination station
        if board_type == "Departures":
            station_filter = st.sidebar.selectbox("Filter by destination:", filter_options, index=0)
        else:  # Arrivals
            station_filter = st.sidebar.selectbox("Filter by origin:", filter_options, index=0)

        train_number = None
    else:
        # Train Number search mode
        train_number = st.sidebar.text_input("Train Number:", placeholder="e.g., 6611")
        selected_station = None
        board_type = None
        station_filter = None

    # Date filter
    st.sidebar.subheader("Date & Time Filter")

    # Day selection (use Paris timezone)
    today = datetime.now(PARIS_TZ).date()
    selected_date = st.sidebar.date_input(
        "Travel Date:", value=today, min_value=today, max_value=today + timedelta(days=60)
    )

    # Time filter (only for station board mode)
    selected_time = None
    use_time_filter = False
    if search_mode == "Station Board":
        use_time_filter = st.sidebar.checkbox("Filter by time", value=True)
        datetime_filter = None

        if use_time_filter:
            time_label = "Departures after:" if board_type == "Departures" else "Arrivals after:"
            # Default to current time for real-time upcoming trains (Paris timezone)
            current_time = datetime.now(PARIS_TZ).time()
            # Round down to nearest 5 minutes for cleaner display
            current_minute = (current_time.minute // 5) * 5
            default_time = time(current_time.hour, current_minute)
            selected_time = st.sidebar.time_input(time_label, value=default_time)
            filter_datetime = datetime.combine(selected_date, selected_time)
            datetime_filter = filter_datetime.strftime("%Y%m%dT%H%M%S")
        else:
            # If no time filter, use start of selected day
            filter_datetime = datetime.combine(selected_date, time(0, 0))
            datetime_filter = filter_datetime.strftime("%Y%m%dT%H%M%S")
    else:
        # For train number search, use start of day
        filter_datetime = datetime.combine(selected_date, time(0, 0))
        datetime_filter = filter_datetime.strftime("%Y%m%dT%H%M%S")

    # Provider filter
    st.sidebar.subheader("Provider Filter")
    provider_options = [
        "All",
        "TGV INOUI",
        "OUIGO",
        "TGV Lyria",
        "Eurostar",
        "DB SNCF",
        "Trenitalia",
        "Renfe",
    ]
    provider_filter = st.sidebar.selectbox(
        "High-Speed Provider:",
        provider_options,
        index=0,
        help="Filter trains by operator:\n"
        "• TGV INOUI: Standard SNCF service\n"
        "• OUIGO: Low-cost SNCF option\n"
        "• TGV Lyria: France-Switzerland service\n"
        "• Eurostar: France-UK service\n"
        "• DB SNCF: Germany-France service\n"
        "• Trenitalia: Italian high-speed trains\n"
        "• Renfe: Spanish high-speed trains",
    )

    # Result limit filter
    st.sidebar.subheader("Display Options")
    limit_options = ["1", "5", "10", "25", "All"]
    limit_selection = st.sidebar.selectbox(
        "Trains per route:",
        limit_options,
        index=3,  # Default to 25
        help="Maximum number of trains to fetch per route",
    )
    # Convert selection to API count parameter
    result_limit = 1000 if limit_selection == "All" else int(limit_selection)

    # Initialize session state for auto-load and tracking settings changes
    if "initial_load" not in st.session_state:
        st.session_state.initial_load = True
    if "last_settings" not in st.session_state:
        st.session_state.last_settings = {}

    # Build current settings dictionary
    if search_mode == "Station Board":
        current_settings = {
            "mode": search_mode,
            "station": selected_station,
            "board_type": board_type,
            "station_filter": station_filter,
            "date": selected_date,
            "use_time_filter": use_time_filter,
            "time": selected_time if use_time_filter else None,
            "provider": provider_filter,
            "limit": limit_selection,
        }
    else:
        current_settings = {
            "mode": search_mode,
            "train_number": train_number,
            "date": selected_date,
            "provider": provider_filter,
            "limit": limit_selection,
        }

    # Check if settings have changed
    settings_changed = st.session_state.last_settings != current_settings

    # Auto-load on page load, when search button is clicked, or when settings change
    search_clicked = st.sidebar.button("Search Trains", type="primary")
    should_load = (
        search_clicked
        or (st.session_state.initial_load and search_mode == "Station Board")
        or (settings_changed and not st.session_state.initial_load)
    )

    # Update last settings
    if should_load:
        st.session_state.last_settings = current_settings

    if should_load:
        # Mark initial load as complete
        if st.session_state.initial_load:
            st.session_state.initial_load = False
            logger.info("Performing initial data load")
        elif settings_changed:
            logger.info("Settings changed - auto-reloading data")
        elif search_clicked:
            logger.info("Manual search triggered by user")

        try:
            with st.spinner("Loading train schedules..."):
                if search_mode == "Station Board":
                    logger.info(
                        f"Station Board: {selected_station} - "
                        f"{board_type} (filter: {station_filter})"
                    )
                    logger.debug(f"Date: {selected_date}, Time filter: {use_time_filter}")

                    # Get station ID from config
                    station_id = STATION_CONFIG[selected_station]["id"]

                    # Get all journeys from/to this station
                    # We need to query all connected stations
                    all_journeys = []

                    if board_type == "Departures":
                        # For departures, query from this station to all connected stations
                        destinations = connections if station_filter == "All" else [station_filter]

                        for dest in destinations:
                            dest_id = STATION_CONFIG[dest]["id"]
                            journeys = client.get_journeys(
                                station_id, dest_id, count=result_limit, datetime=datetime_filter
                            )
                            all_journeys.extend(journeys)
                    else:  # Arrivals
                        # For arrivals, query from all connected stations to this station
                        origins = connections if station_filter == "All" else [station_filter]

                        for origin in origins:
                            origin_id = STATION_CONFIG[origin]["id"]
                            journeys = client.get_journeys(
                                origin_id, station_id, count=result_limit, datetime=datetime_filter
                            )
                            all_journeys.extend(journeys)

                    logger.info(f"Retrieved {len(all_journeys)} total journeys")

                    # Filter for direct high-speed trains with optional provider filter
                    provider_param = None if provider_filter == "All" else provider_filter
                    tgv_journeys = filter_tgv_journeys(all_journeys, provider_param)
                    provider_msg = f" ({provider_filter})" if provider_filter != "All" else ""
                    msg = f"Filtered to {len(tgv_journeys)} direct high-speed trains"
                    logger.info(msg + provider_msg)

                else:  # Train Number search mode
                    if not train_number:
                        st.warning("Please enter a train number to search.")
                        return

                    logger.info(f"Searching for train number: {train_number}")

                    # Get all station IDs
                    station_ids = [STATION_CONFIG[station]["id"] for station in all_stations]

                    # Search for train by number
                    all_journeys = client.search_train_by_number(
                        train_number, station_ids, datetime=datetime_filter
                    )

                    logger.info(f"Retrieved {len(all_journeys)} journeys for train {train_number}")

                    # Filter for direct high-speed trains with optional provider filter
                    provider_param = None if provider_filter == "All" else provider_filter
                    tgv_journeys = filter_tgv_journeys(all_journeys, provider_param)
                    provider_msg = f" ({provider_filter})" if provider_filter != "All" else ""
                    msg = f"Filtered to {len(tgv_journeys)} direct high-speed trains"
                    logger.info(msg + provider_msg)

        except Exception as e:
            logger.error(f"Error fetching train data: {e}", exc_info=True)
            st.error(f"Error fetching train schedules: {e!s}")
            st.info("Please try again or check your network connection.")
            return

        if tgv_journeys:
            # Store journeys in session state
            st.session_state.tgv_journeys = tgv_journeys

            # Display route info
            date_str = selected_date.strftime("%A, %B %d, %Y")
            if search_mode == "Station Board":
                filter_text = ""
                if station_filter != "All":
                    if board_type == "Departures":
                        filter_text = f" to {station_filter}"
                    else:
                        filter_text = f" from {station_filter}"
                st.subheader(f"{selected_station} - {board_type}{filter_text}")
                st.caption(f"Showing {len(tgv_journeys)} direct high-speed trains on {date_str}")
            else:
                st.subheader(f"Train Number: {train_number}")
                st.caption(f"Found {len(tgv_journeys)} journey(s) on {date_str}")

            # Convert to DataFrame and get full journey data
            # Determine sort criterion based on mode
            if search_mode == "Station Board":
                sort_criterion = "arrival" if board_type == "Arrivals" else "departure"
            else:
                sort_criterion = "departure"  # Default for train number search

            df, _full_journeys = format_journey_data(tgv_journeys, sort_by=sort_criterion)
            logger.debug(f"Formatted {len(df)} journeys for display (sorted by {sort_criterion})")

            # Display styled table (hide ID column)
            display_df = df.drop(columns=["ID"])
            styled_df = display_df.style.apply(apply_row_styling, axis=1)
            st.dataframe(styled_df, width="stretch", hide_index=True)

            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                delayed_count = len(df[df["Status"] == "Delayed"])
                st.metric("Delayed Trains", delayed_count)
            with col2:
                on_time_count = len(df[df["Status"] == "On Time"])
                st.metric("On Time", on_time_count)
            with col3:
                avg_delay = df["Arr. Delay"].mean()
                st.metric("Avg Arrival Delay", f"{avg_delay:.0f} min")

            logger.info(f"Dashboard displayed successfully with {len(df)} trains")

        else:
            if all_journeys:
                logger.warning("No direct high-speed trains found in results")
                st.warning(
                    "No direct high-speed trains found. "
                    "Routes may require connections or use other train types."
                )
            else:
                logger.warning("No journeys found for search criteria")
                st.warning("No upcoming journeys found.")


if __name__ == "__main__":
    main()
