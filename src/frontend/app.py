"""Streamlit UI for TGV Times train schedule application."""

import json
import os
from datetime import datetime, time, timedelta
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from backend import SNCFAPIClient
from config import get_logger
from frontend.utils import apply_row_styling, filter_tgv_journeys, format_journey_data

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


def load_station_config():
    """Load station configuration from JSON file."""
    try:
        config_path = Path(__file__).parent.parent / "data" / "stations.json"
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

    st.set_page_config(page_title="TGV Times Dashboard", layout="wide")
    st.title("🚄 TGV Times Dashboard")

    # Check if API key is configured
    if not API_KEY:
        logger.error("API key not configured")
        st.error("⚠️ API key not configured. Please set SNCF_API_KEY in your .env file.")
        return

    # Check if station config is loaded
    if not STATION_CONFIG:
        logger.error("Station configuration not loaded")
        st.error("⚠️ Station configuration not loaded. Please check the logs.")
        return

    # Initialize API client
    try:
        client = SNCFAPIClient(API_KEY)
        logger.debug("API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API client: {e}")
        st.error(f"⚠️ Failed to initialize API client: {e}")
        return

    # Get list of stations from config
    stations = list(STATION_CONFIG.keys())
    logger.debug(f"Loaded {len(stations)} stations")

    # Sidebar filters
    st.sidebar.header("Search Mode")
    search_mode = st.sidebar.radio(
        "Search by:",
        ["Station Route", "Train Number"],
        index=0
    )

    st.sidebar.header("Filters")

    if search_mode == "Station Route":
        departure_station = st.sidebar.selectbox("Departure Station", stations, index=3)

        # Filter arrival stations based on connections from departure station
        available_arrivals = STATION_CONFIG[departure_station]["connections"]
        if not available_arrivals:
            st.error(f"No TGV connections available from {departure_station}")
            return

        arrival_station = st.sidebar.selectbox("Arrival Station", available_arrivals)
        train_number = None
    else:
        # Train Number search mode
        train_number = st.sidebar.text_input("Train Number:", placeholder="e.g., 6611")
        departure_station = None
        arrival_station = None

    # Date filter
    st.sidebar.subheader("Date & Time Filter")

    # Day selection
    today = datetime.now().astimezone().date()
    selected_date = st.sidebar.date_input(
        "Travel Date:",
        value=today,
        min_value=today,
        max_value=today + timedelta(days=60)
    )

    # Time filter (only for station route mode)
    selected_time = None
    use_time_filter = False
    if search_mode == "Station Route":
        use_time_filter = st.sidebar.checkbox("Filter by departure time", value=True)
        departure_time_filter = None

        if use_time_filter:
            selected_time = st.sidebar.time_input("Departure after:", value=time(8, 0))
            departure_datetime = datetime.combine(selected_date, selected_time)
            departure_time_filter = departure_datetime.strftime("%Y%m%dT%H%M%S")
        else:
            # If no time filter, use start of selected day
            departure_datetime = datetime.combine(selected_date, time(0, 0))
            departure_time_filter = departure_datetime.strftime("%Y%m%dT%H%M%S")
    else:
        # For train number search, use start of day
        departure_datetime = datetime.combine(selected_date, time(0, 0))
        departure_time_filter = departure_datetime.strftime("%Y%m%dT%H%M%S")

    # Initialize session state for auto-load and tracking settings changes
    if "initial_load" not in st.session_state:
        st.session_state.initial_load = True
    if "last_settings" not in st.session_state:
        st.session_state.last_settings = {}

    # Build current settings dictionary
    if search_mode == "Station Route":
        current_settings = {
            "mode": search_mode,
            "departure": departure_station,
            "arrival": arrival_station,
            "date": selected_date,
            "use_time_filter": use_time_filter,
            "time": selected_time if use_time_filter else None,
        }
    else:
        current_settings = {
            "mode": search_mode,
            "train_number": train_number,
            "date": selected_date,
        }

    # Check if settings have changed
    settings_changed = st.session_state.last_settings != current_settings

    # Auto-load on page load, when search button is clicked, or when settings change
    search_clicked = st.sidebar.button("🔍 Search Trains", type="primary")
    should_load = (
        search_clicked
        or (st.session_state.initial_load and search_mode == "Station Route")
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
                if search_mode == "Station Route":
                    logger.info(f"Searching trains: {departure_station} → {arrival_station}")
                    logger.debug(f"Date: {selected_date}, Time filter: {use_time_filter}")

                    # Get station IDs from config
                    departure_station_id = STATION_CONFIG[departure_station]["id"]
                    arrival_station_id = STATION_CONFIG[arrival_station]["id"]

                    # Get journeys
                    all_journeys = client.get_journeys(
                        departure_station_id,
                        arrival_station_id,
                        count=20,
                        datetime=departure_time_filter
                    )

                    logger.info(f"Retrieved {len(all_journeys)} total journeys")

                    # Filter for direct TGV trains only
                    tgv_journeys = filter_tgv_journeys(all_journeys)
                    logger.info(f"Filtered to {len(tgv_journeys)} direct TGV journeys")

                else:  # Train Number search mode
                    if not train_number:
                        st.warning("⚠️ Please enter a train number to search.")
                        return

                    logger.info(f"Searching for train number: {train_number}")

                    # Get all station IDs
                    station_ids = [STATION_CONFIG[station]["id"] for station in stations]

                    # Search for train by number
                    all_journeys = client.search_train_by_number(
                        train_number,
                        station_ids,
                        datetime=departure_time_filter
                    )

                    logger.info(f"Retrieved {len(all_journeys)} journeys for train {train_number}")

                    # Filter for direct TGV trains only
                    tgv_journeys = filter_tgv_journeys(all_journeys)
                    logger.info(f"Filtered to {len(tgv_journeys)} direct TGV journeys")

        except Exception as e:
            logger.error(f"Error fetching train data: {e}", exc_info=True)
            st.error(f"⚠️ Error fetching train schedules: {e!s}")
            st.info("Please try again or check your network connection.")
            return

        if tgv_journeys:
            # Store journeys in session state
            st.session_state.tgv_journeys = tgv_journeys

            # Display route info
            date_str = selected_date.strftime("%A, %B %d, %Y")
            if search_mode == "Station Route":
                st.subheader(f"🚉 {departure_station} → {arrival_station}")
                st.caption(f"Showing {len(tgv_journeys)} direct TGV trains on {date_str}")
            else:
                st.subheader(f"🚄 Train Number: {train_number}")
                st.caption(f"Found {len(tgv_journeys)} journey(s) on {date_str}")

            # Convert to DataFrame and get full journey data
            df, _full_journeys = format_journey_data(tgv_journeys)
            logger.debug(f"Formatted {len(df)} journeys for display")

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
                logger.warning("No direct TGV trains found in results")
                st.warning(
                    "⚠️ No direct TGV trains found. Routes may require connections or use other train types."
                )
            else:
                logger.warning("No journeys found for search criteria")
                st.warning("⚠️ No upcoming journeys found.")


if __name__ == "__main__":
    main()
