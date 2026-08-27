# Dijkstra Baseline

## Baseline Result

*Distance: 920.46 m, 0.920 km*

Execution Time: 46.586 ms

*Graph: 60,501,21 nodes, 7,663,806 edges*

Source node: 5260424  
Target node: 5236774

## Baseline Implementation

The baseline implementation uses Dijkstra's algorithm with:

- A distance array
- `PriorityQueue`
- Stale-entry skipping
- GraphHopper `EdgeIterator`
- GraphHopper weighting via `calcEdgeWeight(..., false)`
- Early termination when the target node is settled

Graph loading, local `aarambh-car.json` model loading, graph cache, source/target selection, coordinate handling, and output formatting are kept consistent with the Bellman-Ford implementation.

## Purpose of Keeping This Baseline

This implementation is preserved as the reference point for three subsequent Dijkstra optimizations.

The route distance must remain unchanged after each optimization. Execution time will be compared against this baseline.