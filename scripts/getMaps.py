"""
generate_routes_dataset_graphhopper.py
 
Fixed script to fetch pairwise routes from GraphHopper and save to JSON.
Key fixes:
- Use repeated query parameters for 'point' (requests supports a list of tuples)
- Save progress incrementally to resume on failures
- Retry with exponential backoff on transient errors
- Respect polite delays to avoid rate limits
"""

import requests
import json
import time
import os
from math import ceil
 
API_KEY = 'd4bb4356-607f-46a8-ba93-5f16fe3dca3b'
BASE_URL = "https://graphhopper.com/api/1/route"
OUTPUT_FILE = "static_routes_dataset.json"
TMP_OUTPUT = "static_routes_dataset_progress.json"
SLEEP_BETWEEN_REQS = 1.0 
MAX_RETRIES = 4
 
cities = {
    # Maharashtra
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Aurangabad": (19.8762, 75.3433),
 
    # Gujarat
    "Ahmedabad": (23.0225, 72.5714),
    "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812),
    "Rajkot": (22.3039, 70.8022),
 
    # Madhya Pradesh
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Gwalior": (26.2183, 78.1828),
    "Jabalpur": (23.1815, 79.9864),
 
    # Rajasthan
    "Jaipur": (26.9124, 75.7873),
    "Udaipur": (24.5854, 73.7125),
    "Jodhpur": (26.2389, 73.0243),
    "Kota": (25.2138, 75.8648)
}
 
def save_progress(routes_list, path=TMP_OUTPUT):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(routes_list, f, indent=2, ensure_ascii=False)
 
def load_progress(path=TMP_OUTPUT):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
 
def finalize_output(tmp_path=TMP_OUTPUT, out_path=OUTPUT_FILE):
    if os.path.exists(tmp_path):
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Finalized dataset to {out_path}")
    else:
        print("No progress file to finalize.")
 
def get_route(lat1, lon1, lat2, lon2, vehicle="car"):
    """
    Uses repeated 'point' parameters. Returns dict or None.
    Note: We set points_encoded=False so response.points.coordinates is [lon, lat] pairs.
    """
    params = [
        ("point", f"{lat1},{lon1}"),
        ("point", f"{lat2},{lon2}"),
        ("vehicle", vehicle),
        ("locale", "en"),
        ("key", API_KEY),
        ("points_encoded", "false") 
    ]
 
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
 
            if "paths" not in data or not data["paths"]:
                msg = data.get("message", data)
                raise RuntimeError(f"Invalid response (no paths): {msg}")
 
            path = data["paths"][0]
            distance_km = round(path["distance"] / 1000.0, 3)
            duration_min = round(path["time"] / 60000.0, 3)
 
            coords = path.get("points", {}).get("coordinates", None)
            if coords is None:
                coords = []
 
            return {
                "distance_km": distance_km,
                "duration_min": duration_min,
                "coordinates_lonlat": coords 
            }
 
        except requests.exceptions.RequestException as e:
            wait = 2 ** attempt
            print(f"RequestException on attempt {attempt}/{MAX_RETRIES}: {e}. Retrying in {wait}s...")
            time.sleep(wait)
        except RuntimeError as e:
            print(f"Runtime error for route ({lat1},{lon1}) -> ({lat2},{lon2}): {e}")
            return None
    print(f"Failed to fetch route after {MAX_RETRIES} attempts.")
    return None
 
def main():
    routes = load_progress()
    seen_pairs = {(r["from_city"], r["to_city"]) for r in routes}
    city_items = list(cities.items())
    total_cities = len(city_items)
    total_pairs = total_cities * (total_cities - 1)
 
    counter = 1
    if routes:
        counter = len(routes) + 1
        print(f"Resuming from saved progress. Already have {len(routes)} routes.")
 
    print(f"Total to fetch (ordered pairs): {total_pairs}")
 
    for i, (c1, (lat1, lon1)) in enumerate(city_items):
        for j, (c2, (lat2, lon2)) in enumerate(city_items):
            if c1 == c2:
                continue
 
            if (c1, c2) in seen_pairs:
                counter += 1
                continue
 
            print(f"[{counter}/{total_pairs}] Fetching {c1} -> {c2}")
 
            result = get_route(lat1, lon1, lat2, lon2)
            if result:
                entry = {
                    "from_city": c1,
                    "to_city": c2,
                    "distance_km": result["distance_km"],
                    "duration_min": result["duration_min"],
                    "coordinates_lonlat": result["coordinates_lonlat"]
                }
                routes.append(entry)
                seen_pairs.add((c1, c2))
                save_progress(routes)
                print(f"Saved route: {c1} -> {c2} ({result['distance_km']} km, {result['duration_min']} min)")
            else:
                entry = {
                    "from_city": c1,
                    "to_city": c2,
                    "error": "no_route_or_failed_fetch"
                }
                routes.append(entry)
                seen_pairs.add((c1, c2))
                save_progress(routes)
                print(f"Saved placeholder for failed route: {c1} -> {c2}")
 
            counter += 1
            time.sleep(SLEEP_BETWEEN_REQS)
 
    finalize_output()
    print("Done.")
 
if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
        print("Please set your GraphHopper API key in the GRAPHHOPPER_API_KEY env var or edit the script.")
    else:
        main()