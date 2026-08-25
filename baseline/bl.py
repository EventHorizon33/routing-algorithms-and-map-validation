"""
baseline_benchmark.py
Queries a local GraphHopper instance for A-to-B road distance + latency,
compares against straight-line distance, and saves results to CSV.

Run this WHILE the GraphHopper server (localhost:8989) is running.
"""

import requests
import time
import math
import pandas as pd

GRAPHHOPPER_URL = "http://localhost:8989/route"
PROFILE = "car"

# Test A-to-B coordinate pairs (lat, lon) within the Southern Zone extract.
# Replace/add real pairs relevant to your use case as needed.
TEST_PAIRS = [
    # Karnataka
    {"name": "Bangalore to Mysore", "a": (12.9716, 77.5946), "b": (12.2958, 76.6394)},
    {"name": "Hubli to Dharwad",    "a": (15.3647, 75.1239), "b": (15.4589, 75.0060)},

    # Kerala
    {"name": "Kochi to Thiruvananthapuram", "a": (9.9312, 76.2673), "b": (8.5241, 76.9366)},
    {"name": "Kozhikode to Kannur",         "a": (11.2588, 75.7804), "b": (11.8745, 75.3704)},

    # Tamil Nadu
    {"name": "Chennai to Pondicherry",      "a": (13.0827, 80.2707), "b": (11.9416, 79.8083)},
    {"name": "Madurai to Tiruchirappalli",  "a": (9.9252, 78.1198),  "b": (10.7905, 78.7047)},

    #Inside Bangalore
    {"name": "blr_urban_route_1", "a": (12.9719, 77.6412), "b": (12.9320, 77.6227)},
    {"name": "blr_urban_route_2", "a": (13.0081, 77.5648), "b": (12.9709, 77.5658)},

    #Inside Ahmedabad
    #{"name": "ahm_urban_route_1", "a": (23.0364, 72.5611), "b": (23.0131, 72.5625)},
    #{"name": "ahm_urban_route_2", "a": (23.0263, 72.6739), "b": (23.0634, 72.5662)},

    #Inside Mumbai
    #{"name": "mum_urban_route_1", "a": (19.0616, 72.8480), "b": (19.0576, 72.8284)},
    #{"name": "mum_urban_route_2", "a": (19.1087, 72.8933), "b": (19.1624, 72.8694)},

    #Inside Chennai
    {"name": "che_urban_route_1", "a": (13.0827, 80.2707), "b": (13.0136, 80.2393)},
    {"name": "che_urban_route_2", "a": (13.14096, 80.24818), "b": (13.0827, 80.2707)},

    #Inside Hyderabad
    {"name": "hyd_urban_route_1", "a": (17.383912, 78.47083), "b": (17.409755, 78.488209)},
    {"name": "hyd_urban_route_2", "a": (17.34613, 78.550752), "b": (17.462149, 78.429523)},
]


def haversine_distance_m(coord1, coord2):
    """Straight-line (geodesic) distance in meters — NOT road distance, used as a reference floor."""
    R = 6371000
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def query_graphhopper(point_a, point_b):
    """Sends one routing request, returns (road_distance_m, gh_reported_time_ms, request_latency_ms)."""
    params = {
        "point": [f"{point_a[0]},{point_a[1]}", f"{point_b[0]},{point_b[1]}"],
        "profile": PROFILE,
        "calc_points": "false",  # we don't need the route geometry, just distance/time
    }
    start = time.perf_counter()
    response = requests.get(GRAPHHOPPER_URL, params=params, timeout=30)
    request_latency_ms = (time.perf_counter() - start) * 1000

    response.raise_for_status()
    data = response.json()

    path = data["paths"][0]
    return path["distance"], path["time"], request_latency_ms


def run_benchmark():
    results = []

    for test in TEST_PAIRS:
        name, point_a, point_b = test["name"], test["a"], test["b"]
        try:
            road_distance_m, gh_time_ms, request_latency_ms = query_graphhopper(point_a, point_b)
        except Exception as e:
            print(f"[FAILED] {name}: {e}")
            continue

        straight_line_m = haversine_distance_m(point_a, point_b)
        detour_ratio = road_distance_m / straight_line_m if straight_line_m > 0 else None

        results.append({
            "name": name,
            "point_a": point_a,
            "point_b": point_b,
            "road_distance_m": round(road_distance_m, 1),
            "straight_line_m": round(straight_line_m, 1),
            "detour_ratio": round(detour_ratio, 3),
            "gh_travel_time_ms": gh_time_ms,
            "request_latency_ms": round(request_latency_ms, 1),
        })

        print(f"[OK] {name}: road={road_distance_m:.0f}m, straight-line={straight_line_m:.0f}m, "
              f"ratio={detour_ratio:.2f}, latency={request_latency_ms:.1f}ms")

    df = pd.DataFrame(results)
    df.to_csv("baseline_results.csv", index=False)

    print("\n--- Summary ---")
    print(f"Avg request latency: {df['request_latency_ms'].mean():.1f} ms")
    print(f"Avg detour ratio (road/straight-line): {df['detour_ratio'].mean():.2f}")
    print(f"Saved {len(df)} results to baseline_results.csv")


if __name__ == "__main__":
    run_benchmark()