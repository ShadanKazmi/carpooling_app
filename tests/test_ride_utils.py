import pytest
from unittest.mock import MagicMock
import json
from utils.ride_utils import (
    get_driver_id,
    fetch_routes,
    fetch_route_cities,
    get_route_coordinates,
    create_ride_request,
    create_ride_offer,
    get_open_ride_requests,
    get_open_ride_offers,
    get_matched_ride_details,
    accept_ride_request,
    get_driver_assigned_rides,
    update_ride_status,
    get_available_rides,
    find_matching_offers,
    book_ride,
    get_passenger_id_by_user,
    has_user_already_rated,
    save_rating_and_update_averages,
    get_rides_for_driver,
    get_rides_for_passenger,
    update_ride_position,
    get_active_ride,
    notify_user,
    get_unread_notification_count,
    fetch_active_rides,
    get_route_coordinates_for_ride,
    update_ride_position_index,
    create_notification,
    log_incident,
    create_user_report,
)

 
@pytest.fixture
def mock_db(mocker):
    """Mock the DB connection + cursor for every test."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
 
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch("utils.ride_utils.get_connection", return_value=mock_conn)
 
    return mock_conn, mock_cursor
 
 
 
def test_get_driver_id(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = {"driver_id": 7}
 
    d = get_driver_id(5)
    assert d == 7
 
 
def test_fetch_routes(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [
        {"route_id": 1, "from_city": "A", "to_city": "B"}
    ]
 
    routes = fetch_routes()
    assert len(routes) == 1
    assert routes[0]["from_city"] == "A"
 
 
def test_fetch_route_cities(mock_db):
    _, cursor = mock_db
    cursor.fetchall.side_effect = [
        [{"from_city": "Mumbai"}, {"from_city": "Delhi"}],
        [{"to_city": "Pune"}, {"to_city": "Goa"}],
    ]
 
    fc, tc = fetch_route_cities()
    assert "Mumbai" in fc
    assert "Goa" in tc
 
 
 
def test_get_route_coordinates(mock_db):
    _, cursor = mock_db
    coords = [[72.5, 19.1], [72.6, 19.2]]
    cursor.fetchone.return_value = {"coordinates": json.dumps(coords)}
 
    data = get_route_coordinates(1)
    assert len(data) == 2
    assert data[0]["lat"] == 19.1
 
 
 
def test_create_ride_request_success(mock_db):
    conn, cursor = mock_db
    cursor.fetchone.return_value = {"passenger_id": 4}
 
    ok = create_ride_request(
        passenger_id=10,
        from_city="A",
        to_city="B",
        date_time="2024-01-01 10:00:00",
        passengers_count=2,
        preferences={"ac": True},
    )
    assert ok is True
    assert conn.commit.called
 
 
def test_create_ride_offer(mock_db):
    conn, cursor = mock_db
 
    ok = create_ride_offer(
        driver_id=9, vehicle_no="MH12", route_id=2,
        available_seats=3, price_per_km=10, estimated_fare=250
    )
    assert ok is True
    assert conn.commit.called
 
 
 
def test_get_open_ride_requests(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [{"request_id": 1}]
    data = get_open_ride_requests()
    assert len(data) == 1
 
 
def test_get_open_ride_offers(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [{"offer_id": 1}]
    offers = get_open_ride_offers()
    assert len(offers) == 1
 
 
def test_get_matched_ride_details(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = {"offer_id": 10, "driver_name": "John"}
 
    d = get_matched_ride_details(5)
    assert d["driver_name"] == "John"
 
 
def test_accept_ride_request(mock_db):
    conn, cursor = mock_db
 
    cursor.fetchone.side_effect = [
        {"from_city": "A", "to_city": "B", "passenger_id": 4, "passengers_count": 2},
        {"route_id": 1, "distance_km": 10},
    ]
 
    ok = accept_ride_request(driver_id=5, request_id=9)
    assert ok is True
    assert conn.commit.called
 
 
def test_update_ride_status(mock_db):
    conn, cursor = mock_db
 
    ok = update_ride_status(ride_id=3, new_status="completed")
    assert ok is True
    assert conn.commit.called
 
 
def test_find_matching_offers(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [
        {"offer_id": 1, "driver_name": "A"}
    ]
    offers = find_matching_offers("Mumbai", "Pune", "2024-01-01", 2)
    assert len(offers) == 1
 
 
def test_book_ride(mock_db):
    conn, cursor = mock_db
    cursor.fetchone.return_value = {"available_seats": 3, "estimated_fare": 200, "driver_id": 5}
 
    ok = book_ride(offer_id=2, passenger_id=7, seats_requested=2)
    assert ok is True
    assert conn.commit.called
 
 
def test_get_passenger_id_by_user(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = {"passenger_id": 20}
 
    pid = get_passenger_id_by_user(7)
    assert pid == 20
 
 
def test_has_user_already_rated(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = {"rating_id": 1}
 
    assert has_user_already_rated(1, 2) is True
 
 
def test_save_rating_and_update_averages(mock_db):
    conn, cursor = mock_db
 
    cursor.fetchone.side_effect = [
        {},  # first select (avg)
        {"driver_id": 5},  # belongs to driver
    ]
 
    ok = save_rating_and_update_averages(
        ride_id=1,
        rated_by_user_id=2,
        rated_user_id=3,
        rating_value=5,
        feedback_text="Great ride",
    )
    assert ok is True
    assert conn.commit.called

def test_get_rides_for_driver(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [{"ride_id": 1}]
    data = get_rides_for_driver(4)
    assert len(data) == 1
 
 
def test_get_rides_for_passenger(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = [{"ride_id": 2}]
    data = get_rides_for_passenger(9)
    assert len(data) == 1
 
 
def test_update_ride_position(mock_db):
    conn, cursor = mock_db
 
    update_ride_position(ride_id=5, new_index=12)
    assert conn.commit.called
 
 
def test_update_ride_position_index(mock_db):
    conn, cursor = mock_db
 
    ok = update_ride_position_index(ride_id=3, new_index=7)
    assert ok is True
    assert conn.commit.called
 
 
def test_get_active_ride(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = {"ride_id": 9}
 
    r = get_active_ride(8)
    assert r["ride_id"] == 9
 
 
def test_notify_user(mock_db):
    conn, cursor = mock_db
 
    notify_user(5, "hello")
    assert conn.commit.called
 
 
def test_get_unread_notification_count(mock_db):
    _, cursor = mock_db
    cursor.fetchone.return_value = (3,)
 
    cnt = get_unread_notification_count(4)
    assert cnt == 3
 
 
def test_create_notification(mock_db):
    conn, cursor = mock_db
 
    create_notification(8, "Test")
    assert conn.commit.called
 
 
def test_fetch_active_rides(mock_db):
    _, cursor = mock_db
    cursor.fetchall.return_value = []
 
    active = fetch_active_rides()
    assert active == []
 
 
def test_get_route_coordinates_for_ride(mock_db):
    _, cursor = mock_db
    coords = [[72.5, 19.1], [72.6, 19.2]]
    cursor.fetchone.return_value = (json.dumps(coords),)
 
    pts = get_route_coordinates_for_ride({"ride_id": 5})
    assert len(pts) == 2
    assert pts[0]["lat"] == 19.1
 

 
def test_log_incident(mock_db):
    conn, cursor = mock_db
 
    log_incident(ride_id=1, user_id=5, incident_type="emergency", description="test")
    assert conn.commit.called
 
 
def test_create_user_report(mock_db):
    conn, cursor = mock_db
 
    create_user_report(1, 2, 3, "behaviour", "Bad behavior")
    assert conn.commit.called