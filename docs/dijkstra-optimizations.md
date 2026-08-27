# Dijkstra Optimizations

Three optimizations will be applied incrementally to the naive Dijkstra implementation.

The baseline execution time is **46.586 ms** with a route distance of **920.46 m**.

Each optimization must:

1. Preserve the route result.
2. Modify only the intended implementation.
3. Be independently documented.
4. Be benchmarked against the previous version.

---


## Optimization 1: Reuse EdgeExplorer

### Change

Reused a single GraphHopper `EdgeExplorer` instance inside `runDijkstra()` instead of creating a new explorer for every settled node.

The explorer is created once and its base node is updated with `setBaseNode(node)` as Dijkstra processes each settled node.

### Why it should be faster

The previous implementation repeatedly allocated short-lived `EdgeExplorer` objects inside Dijkstra's hot loop. Reusing the explorer removes those allocations and reduces allocation/GC overhead while preserving the same edge traversal.

### Result

Baseline execution time: **46.586 ms**

Optimization 1 execution time: **32.981 ms**

Observed improvement: **13.605 ms (~29.2% faster)**

Distance remained unchanged at **920.46 m (0.920 km)**.

### Correctness

The priority-queue ordering, stale-entry handling, target termination, directed edge traversal, edge weighting, and distance relaxation remain unchanged.

### Complexity

- Time: **O((V + E) log V)**, unchanged asymptotically.
- Working space: **O(V)**, unchanged.
- `EdgeExplorer` allocations: reduced from repeated allocations to **O(1)**.

## Optimization 2

_To be added after implementation and verification._

## Optimization 3

_To be added after implementation and verification._