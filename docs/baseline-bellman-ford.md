# Bellman-Ford Baseline

## Purpose

This is the initial naive Bellman-Ford implementation used as the
baseline for Task 2.

## Graph

- Graph source: Southern Zone OSM PBF
- Graph engine: GraphHopper 11.0
- Routing profile: car

## Baseline implementation

The implementation is intentionally naive and has not yet been
optimized.

Source:
`src/main/java/BellmanFordRouting.java`

## Baseline result

The naive implementation completed successfully.

Runtime:
~30 minutes

The exact runtime and route output are recorded from the initial run.

## Purpose of keeping this baseline

All subsequent optimizations will be compared against this implementation
for:

1. Runtime
2. Route distance
3. Correctness
4. Algorithmic changes

The baseline implementation should remain recoverable through Git history.