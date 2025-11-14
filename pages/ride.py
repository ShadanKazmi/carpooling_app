import time
import json
import pydeck as pdk
import streamlit as st
from utils.db_connection import get_connection
from datetime import datetime

from utils.ride_utils import create_notification, get_route_coordinates_for_ride, update_ride_position_index
 
st.set_page_config(page_title="Ride Tracking", layout="wide")


 
st.header("Ride Tracking — Simulation")
 
try:
    import pymysql
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""
        SELECT r.ride_id, r.offer_id, r.passenger_id, r.driver_id, r.start_time, r.end_time,
               r.current_position_index, r.status,
               rr.from_city, rr.to_city, u.name AS passenger_name, du.name AS driver_name
        FROM rides r
        LEFT JOIN ride_offers ro ON r.offer_id = ro.offer_id
        LEFT JOIN ride_requests rr ON ro.request_id = rr.request_id
        LEFT JOIN passengers p ON r.passenger_id = p.passenger_id
        LEFT JOIN users u ON p.user_id = u.user_id
        LEFT JOIN drivers dr ON r.driver_id = dr.driver_id
        LEFT JOIN users du ON dr.user_id = du.user_id
        WHERE r.status IN ('booked','active')
        ORDER BY r.start_time DESC
    """)
    active_rides = cur.fetchall()
    cur.close()
    conn.close()
except Exception as e:
    st.error("Error fetching active rides: " + str(e))
    active_rides = []
 
if not active_rides:
    st.info("No active rides to track (rides with status 'booked' or 'active').")
    st.write("You can start a ride from the Offer / Driver page to test simulation.")
    st.stop()
 
ride_map = {f"{r['ride_id']} — {r['from_city']} ➜ {r['to_city']} ({r.get('driver_name') or 'Unknown driver'})": r for r in active_rides}
choice = st.selectbox("Select an active ride to track", options=list(ride_map.keys()))
ride = ride_map[choice]
 
st.markdown(f"**Ride ID:** {ride['ride_id']}  •  **Status:** {ride['status']}  •  **Driver:** {ride.get('driver_name') or '—'}  •  **Passenger:** {ride.get('passenger_name') or '—'}")
st.write("Start time:", ride.get('start_time'))
 
coords = get_route_coordinates_for_ride(ride)
if not coords:
    st.error("No route coordinates found for this ride. Ensure `routes.coordinates` contains a JSON list of points (lon,lat).")
    st.stop()
 
positions = [(pt['lon'], pt['lat']) for pt in coords]  # pydeck expects lat, lon in many helpers
center_lon = sum(p[0] for p in positions) / len(positions)
center_lat = sum(p[1] for p in positions) / len(positions)
 
sim_key = f"sim_{ride['ride_id']}"
if sim_key not in st.session_state:
    st.session_state[sim_key] = {
        "running": False,
        "paused": False,
        "index": int(ride.get('current_position_index') or 0),
        "speed": 1.0  
    }
 
state = st.session_state[sim_key]
 
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
with col1:
    if not state["running"]:
        if st.button("Start Simulation"):
            state["running"] = True
            state["paused"] = False
            state["index"] = int(ride.get('current_position_index') or 0)
    else:
        if state["paused"]:
            if st.button("Resume"):
                state["paused"] = False
        else:
            if st.button("Pause"):
                state["paused"] = True
with col2:
    if st.button("Step +1"):
        new_idx = min(len(positions) - 1, state["index"] + 1)
        state["index"] = new_idx
        update_ride_position_index(ride['ride_id'], new_idx)
with col3:
    if st.button("Stop Simulation"):
        state["running"] = False
        state["paused"] = False
with col4:
    if st.button("Emergency (stop & notify)"):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE rides SET status='cancelled' WHERE ride_id=%s", (ride['ride_id'],))
            conn.commit()
            st.warning("Ride marked as cancelled (emergency). Notifications created.")
            cur.execute("SELECT d.user_id AS driver_user_id, p.user_id AS passenger_user_id FROM rides r JOIN drivers d ON r.driver_id = d.driver_id JOIN passengers p ON r.passenger_id = p.passenger_id WHERE r.ride_id=%s", (ride['ride_id'],))
            uu = cur.fetchone()
            if uu:
                try:
                    driver_uid = uu[0]
                    passenger_uid = uu[1]
                    create_notification(driver_uid, f"Ride {ride['ride_id']} cancelled due to emergency.")
                    create_notification(passenger_uid, f"Ride {ride['ride_id']} cancelled due to emergency.")
                except Exception:
                    pass
        except Exception as e:
            conn.rollback()
            st.error("Error cancelling ride: " + str(e))
        finally:
            cur.close()
            conn.close()
        state["running"] = False
        state["paused"] = False
 
state["speed"] = st.slider("Step delay (seconds per step)", min_value=0.2, max_value=5.0, value=float(state["speed"]), step=0.2)
 
map_height = 600
deck_container = st.empty()

def render_deck(idx):
    path_data = [{"path": positions}]
 
    path_layer = pdk.Layer(
        "PathLayer",
        data=path_data,
        get_path="path",
        get_width=5,
        width_min_pixels=3,
        opacity=0.8,
        color=[255, 255, 0],
    )
 
    current_point = {
        "lon": positions[idx][0],
        "lat": positions[idx][1]
    }
 
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[current_point],
        get_position="[lon, lat]",
        get_radius=120,
        radius_min_pixels=10,
        opacity=1,
        color=[255, 0, 0],
    )
 
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12,
        bearing=0,
        pitch=45
    )
 
    deck = pdk.Deck(
        layers=[path_layer, point_layer],
        initial_view_state=view_state,
        map_style="light",          # ✔ light map for dark UI
        tooltip={"text": "Current Position"}
    )
 
    deck_container.pydeck_chart(deck)
 
curr_index = int(state["index"])
curr_index = min(curr_index, len(positions) - 1)
render_deck(curr_index)
st.caption(f"Position index: {curr_index} / {len(positions)-1}")
 
if state["running"] and not state["paused"]:
    try:
        while state["running"] and not state["paused"]:
            if state["index"] < len(positions) - 1:
                state["index"] += 1
                update_ride_position_index(ride['ride_id'], state["index"])
                render_deck(state["index"])
                # st.caption(f"Position index: {state['index']} / {len(positions)-1}  — updated {datetime.now().strftime('%H:%M:%S')}")
                time.sleep(state["speed"])
            else:
                st.success("Simulation reached the end of the route.")
                conn = get_connection(); cur = conn.cursor(); cur.execute("UPDATE rides SET status='completed' WHERE ride_id=%s", (ride['ride_id'],)); conn.commit(); cur.close(); conn.close()
                state["running"] = False
                break
    except Exception as e:
        st.error("Simulation stopped due to error: " + str(e))
        state["running"] = False
 
col5, col6 = st.columns(2)
with col5:
    if st.button("Reset position to start"):
        state["index"] = 0
        update_ride_position_index(ride['ride_id'], 0)
        render_deck(0)
with col6:
    if st.button("Set position to end"):
        state["index"] = len(positions) - 1
        update_ride_position_index(ride['ride_id'], state["index"])
        render_deck(state["index"])
 
st.write("---")
st.info("Notes: This is a client-side simulation. The DB's `rides.current_position_index` is updated during simulation so other pages can read it for the active ride. To simulate 'real' tracking in production you'd push position updates from the driver's device via websocket / API.")