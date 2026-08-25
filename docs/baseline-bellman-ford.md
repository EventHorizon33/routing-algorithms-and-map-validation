# Bellman-Ford Baseline

## Purpose: This is the initial naive Bellman-Ford implementation used as the
baseline for Task 2.

## Graph: -

- Graph source: Southern Zone OSM PBF
- Graph engine: GraphHopper 11.0
- Routing profile: car

## Baseline implementation: The implementation is intentionally naive and has not yet been
optimized.

Source:
`src/main/java/BellmanFordRouting.java`

## Baseline result

The naive implementation completed successfully.

Nodes: 6050121
Edges: 7663806
Source Node: 5260424
Target Node: 5236774

========= RESULTS =========
*Distance: 920.46 m, 0.92046 km*

Execution Time: 1705729.220 ms

*Total Time: 28:28 min*
Finished at: 2026-08-25T00:43:11+05:30


The exact runtime and route output are recorded from the initial run.

## Purpose of keeping this baseline

All subsequent optimizations will be compared against this implementation
for:

1. Runtime
2. Route distance
3. Correctness
4. Algorithmic changes

The baseline implementation should remain recoverable through Git history.