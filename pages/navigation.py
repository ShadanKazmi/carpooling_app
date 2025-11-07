import streamlit as st
import pydeck as pdk
import time
from utils.ride_utils import get_active_ride, update_ride_position, get_route_coordinates
 
def show():
    st.title("Live Ride Tracking")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
 
    ride = get_active_ride(user["user_id"])
    if not ride:
        st.info("No active rides right now.")
        return
 
    coords = get_route_coordinates(ride["route_id"])
    index = ride["current_position_index"]
 
    map_placeholder = st.empty()
 
    is_driver = (user["role"] == "driver")
 
    while index < len(coords):
        point = coords[index]
 
        map_placeholder.pydeck_chart(
            pdk.Deck(
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=[point],
                        get_position='[lon, lat]',
                        get_color='[255, 0, 0]',
                        get_radius=60000,
                    )
                ],
                initial_view_state=pdk.ViewState(
                    latitude=point["lat"],
                    longitude=point["lon"],
                    zoom=9,
                    pitch=45,
                )
            )
        )
 
        if is_driver:
            if st.button("Move Forward", key=f"step_{index}"):
                update_ride_position(ride["ride_id"], index + 1)
                st.rerun()
 
        time.sleep(1.2)
        ride = get_active_ride(user["user_id"])
        index = ride["current_position_index"]
 
if __name__ == "__main__":
    show()