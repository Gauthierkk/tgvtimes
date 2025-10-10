from datetime import datetime

import requests
import streamlit as st

API_KEY = "cf2e66b1-d5ef-45cc-87f7-644168728699"
BASE_URL = "https://api.navitia.io/v1/"

def get_station_id(station_name):
    """Get the station ID from the station name."""
    response = requests.get(
        f"{BASE_URL}coverage/sncf/places?q={station_name}&type[]=stop_area",
        headers={"Authorization": API_KEY},
    )
    response.raise_for_status()
    places = response.json().get("places")
    if places:
        return places[0]["id"]
    return None

def get_next_departures(departure_station_id, arrival_station_id):
    """Get the next departures from a station to another."""
    response = requests.get(
        f"{BASE_URL}coverage/sncf/journeys?from={departure_station_id}&to={arrival_station_id}",
        headers={"Authorization": API_KEY},
    )
    response.raise_for_status()
    return response.json().get("journeys")

def main():
    st.title("TGV Times")

    departure_station = st.text_input("Departure Station", "Paris Gare de Lyon")
    arrival_station = st.text_input("Arrival Station", "Lyon Part-Dieu")

    if st.button("Search for trains"):
        with st.spinner("Searching for trains..."):
            departure_station_id = get_station_id(departure_station)
            arrival_station_id = get_station_id(arrival_station)

            if not departure_station_id:
                st.error(f"Could not find departure station: {departure_station}")
                return

            if not arrival_station_id:
                st.error(f"Could not find arrival station: {arrival_station}")
                return

            journeys = get_next_departures(departure_station_id, arrival_station_id)

            if journeys:
                st.subheader("Next Departures")
                for journey in journeys:
                    departure_time = datetime.strptime(journey["departure_date_time"], "%Y%m%dT%H%M%S")
                    arrival_time = datetime.strptime(journey["arrival_date_time"], "%Y%m%dT%H%M%S")
                    duration_in_seconds = journey["duration"]
                    duration_in_minutes = duration_in_seconds // 60
                    duration_hours = duration_in_minutes // 60
                    duration_minutes = duration_in_minutes % 60

                    st.write(f"**Departure:** {departure_time.strftime('%H:%M')}")
                    st.write(f"**Arrival:** {arrival_time.strftime('%H:%M')}")
                    st.write(f"**Duration:** {duration_hours}h {duration_minutes}m")
                    st.write("---")
            else:
                st.warning("No upcoming journeys found.")

if __name__ == "__main__":
    main()
