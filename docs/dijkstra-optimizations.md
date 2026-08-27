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



++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


## Optimization 2: Settled-Node Edge Pruning

### Change

Added a `BitSet` to track settled nodes during `runDijkstra()`.

After a non-stale priority-queue entry is settled, edges whose destination node has already been settled are skipped before performing edge-weight calculation and relaxation.

### Why it should be faster

Dijkstra guarantees that once a node is settled, its shortest distance is final. Therefore, edges leading to already-settled nodes cannot produce a better distance.

Skipping these edges avoids unnecessary GraphHopper edge-weight calculations and relaxation checks, particularly for back-edges in the bidirectional road graph.

### Correctness

Correctness was preserved. Dijkstra's non-negative-weight property guarantees that a settled node cannot later receive a shorter distance.

The priority queue, stale-entry handling, target termination, directed traversal, edge weighting, distance calculation, and Optimization 1's reusable `EdgeExplorer` remain unchanged.

### Complexity

- Time: remains `O((V + E) log V)` in the worst case.
- Working space: remains `O(V + E)` in the worst case.
- The additional `BitSet` requires `O(V)` bits.
- The optimization reduces edge-weight calculations in practice but does not change the asymptotic bound.

### Result

Distance remained unchanged at **920.46 m (0.920 km)**.

Observed execution times:

- Optimization 1: **32.981 ms**
- Optimization 2, run 1: **61.269 ms**
- Optimization 2, run 2: **49.023 ms**

Optimization 2 therefore **did not improve runtime for this workload**. Both observed runs were slower than Optimization 1.

### Conclusion

Optimization 2 was retained as a documented experimental result but is not considered a performance improvement for the selected workload.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



### Optimization 3: Distance-Dominance Pruning

**Optimization #3:** Added distance-dominance pruning before GraphHopper edge-weight calculation.

**Bottleneck addressed:** `weighting.calcEdgeWeight(...)` was being evaluated for outgoing edges even when the adjacent node already had a distance less than or equal to the current settled distance.

**Change:** Before calculating an edge's weight, the implementation now checks:

```java
if (currentDistance >= distance[adjacentNode]) {
    continue;
}