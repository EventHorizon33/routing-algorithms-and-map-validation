"""Query the Task 3A modified-map GraphHopper route twice.

Before running this client, start tools/setup_gh_task3a_modified.ps1. That
script imports only MODIFIED_PBF into MODIFIED_GRAPH_CACHE and starts GraphHopper
11.0 on localhost:8993. This client never imports, rebuilds, or alters a graph.
"""

import math
import sys
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent
MODIFIED_PBF = PROJECT_ROOT / "data" / "task3a-area-modified.osm.pbf"
MODIFIED_GRAPH_CACHE = PROJECT_ROOT / "graph-cache-task3a-modified"
MODIFIED_CONFIG = PROJECT_ROOT / "config-task3a-modified.yml"
GRAPHHOPPER_URL = "http://localhost:8993/route"
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


def validate_modified_setup():
    """Fail before routing if the modified-only import setup is not present."""
    if not MODIFIED_PBF.is_file():
        raise RuntimeError(f"Modified PBF is missing: {MODIFIED_PBF}")
    if not MODIFIED_CONFIG.is_file():
        raise RuntimeError(f"Modified config is missing: {MODIFIED_CONFIG}")
    if not MODIFIED_GRAPH_CACHE.is_dir():
        raise RuntimeError(
            "Modified graph cache is missing. Run tools/setup_gh_task3a_modified.ps1 first."
        )

    config_text = MODIFIED_CONFIG.read_text(encoding="utf-8")
    pbf_path = MODIFIED_PBF.as_posix()
    cache_path = MODIFIED_GRAPH_CACHE.as_posix()
    if pbf_path not in config_text or cache_path not in config_text:
        raise RuntimeError("Modified config does not point to the required modified PBF and cache.")


def query_route():
    """Return GraphHopper paths[0]['distance'] and request latency in ms."""
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
        raise RuntimeError(f"GraphHopper returned no route: {payload.get('message', 'No paths returned.')}")
    distance = paths[0].get("distance")
    if not isinstance(distance, (int, float)):
        raise RuntimeError("GraphHopper route response is missing paths[0]['distance'].")
    return float(distance), latency_ms


def main():
    try:
        validate_modified_setup()
    except RuntimeError as error:
        print(f"TASK 3A MODIFIED SETUP FAILED: {error}", file=sys.stderr)
        return 1

    print(f"Modified PBF: {MODIFIED_PBF}")
    print(f"Modified graph cache: {MODIFIED_GRAPH_CACHE}")
    print(f"GraphHopper route endpoint: {GRAPHHOPPER_URL}")
    print(f"Task 3A source (Albert Street): {SOURCE}")
    print(f"Task 3A target (Second Street): {TARGET}")
    straight_line_m = haversine_distance_m(SOURCE, TARGET)
    print(f"TASK 3A HAVERSINE DISTANCE: {straight_line_m:.3f} metres ({straight_line_m / 1000:.6f} kilometres)")

    measurements = []
    for attempt in range(1, 3):
        try:
            distance_m, latency_ms = query_route()
        except RuntimeError as error:
            print(f"TASK 3A MODIFIED REQUEST {attempt} FAILED: {error}", file=sys.stderr)
            return 1
        measurements.append(distance_m)
        print(f"TASK 3A MODIFIED DISTANCE {attempt}: {distance_m:.3f} metres ({distance_m / 1000:.6f} kilometres)")
        print(f"TASK 3A REQUEST {attempt} LATENCY: {latency_ms:.1f} ms")

    print("TASK 3A MODIFIED REPRODUCIBILITY: " + ("MATCH" if measurements[0] == measurements[1] else "DIFFERENT"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
