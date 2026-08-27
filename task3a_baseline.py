"""Query the isolated Task 3A GraphHopper baseline route twice.

Run this while the Task 3A GraphHopper server is available at localhost:8991.
This script is read-only: it does not modify OSM data, GraphHopper, or its cache.
"""

import math
import sys
import time

import requests


GRAPHHOPPER_URL = "http://localhost:8991/route"
PROFILE = "car"
SOURCE = (12.9674373, 77.6046062)  # Albert Street (latitude, longitude)
TARGET = (12.9673048, 77.6033295)  # Second Street (latitude, longitude)


def haversine_distance_m(point_a, point_b):
    """Return straight-line geodesic distance in metres (not route distance)."""
    earth_radius_m = 6_371_000
    lat1, lon1 = map(math.radians, point_a)
    lat2, lon2 = map(math.radians, point_b)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius_m * math.asin(math.sqrt(haversine))


def query_route():
    """Return the GraphHopper route distance and end-to-end request latency in ms."""
    params = {
        "point": [f"{SOURCE[0]},{SOURCE[1]}", f"{TARGET[0]},{TARGET[1]}"],
        "profile": PROFILE,
        "calc_points": "false",
    }

    started = time.perf_counter()
    try:
        response = requests.get(GRAPHHOPPER_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        raise RuntimeError(f"GraphHopper request failed: {error}") from error
    except ValueError as error:
        raise RuntimeError("GraphHopper returned invalid JSON.") from error

    latency_ms = (time.perf_counter() - started) * 1000
    paths = payload.get("paths")
    if not isinstance(paths, list) or not paths:
        message = payload.get("message", "No route paths were returned.")
        raise RuntimeError(f"GraphHopper returned no route: {message}")

    distance = paths[0].get("distance")
    if not isinstance(distance, (int, float)):
        raise RuntimeError("GraphHopper route response is missing paths[0]['distance'].")

    return float(distance), latency_ms


def main():
    print(f"Task 3A source (Albert Street): {SOURCE}")
    print(f"Task 3A target (Second Street): {TARGET}")

    straight_line_m = haversine_distance_m(SOURCE, TARGET)
    print(
        "TASK 3A HAVERSINE DISTANCE "
        f"{straight_line_m:.3f} metres ({straight_line_m / 1000:.6f} kilometres)"
    )

    measurements = []
    for attempt in range(1, 3):
        try:
            distance_m, latency_ms = query_route()
        except RuntimeError as error:
            print(f"TASK 3A BASELINE REQUEST {attempt} FAILED: {error}", file=sys.stderr)
            return 1

        measurements.append(distance_m)
        print(
            f"TASK 3A BASELINE DISTANCE {attempt}: {distance_m:.3f} metres "
            f"({distance_m / 1000:.6f} kilometres)"
        )
        print(f"TASK 3A REQUEST {attempt} LATENCY: {latency_ms:.1f} ms")

    if measurements[0] == measurements[1]:
        print("TASK 3A BASELINE REPRODUCIBILITY: MATCH")
    else:
        print("TASK 3A BASELINE REPRODUCIBILITY: DIFFERENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
