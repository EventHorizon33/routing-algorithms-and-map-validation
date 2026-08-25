# Bellman-Ford Optimizations

## Optimization 1: Reuse EdgeExplorer

### Change

Reused a single GraphHopper `EdgeExplorer` instance inside `runBellmanFord()` instead of creating a new explorer for every reachable node during every relaxation pass.

The reusable explorer is created once and its base node is updated with `setBaseNode(node)` as the algorithm visits each node.

### Why this should improve performance

The original implementation repeatedly allocated short-lived `EdgeExplorer` objects inside the hottest nested loop of Bellman-Ford. Reusing one explorer reduces object-allocation and garbage-collection overhead.

### Complexity

- Bellman-Ford traversal remains `O(VE)` time.
- Previous implementation could create up to `O(V²)` `EdgeExplorer` objects in the worst case.
- Optimized implementation uses `O(1)` `EdgeExplorer` allocations.
- Working memory remains `O(V)` for the distance array.

### Correctness

The optimization does not change the traversal order, outgoing edges, edge weights, relaxation rule, or early-convergence condition. Therefore, the resulting shortest-path distance remains unchanged.

### Benchmark

|   Version      |    Execution Time    | Distance |
|----------------|---------------------:|---------:|
| Baseline       | 1,705,729 ms (28:28) | 920.46 m |
| Optimization 1 | 1,058,858 ms (17:40) | 920.46 m |

**Observed improvement:** approximately **37.9% lower execution time**.

The optimized run produced the same displayed route distance as the baseline.

### Result: Optimization 1 substantially reduced Bellman-Ford execution time while preserving the observed route result.