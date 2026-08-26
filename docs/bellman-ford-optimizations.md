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



++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


## Optimization 2: Frontier-Based Bellman-Ford Relaxation

### Change

Replaced the full-node scan on every Bellman-Ford relaxation pass with a frontier-based approach.

The algorithm now tracks only nodes whose distances changed during the previous pass. These active nodes are processed in the next pass, and their improved neighbours are added to the next frontier.

A `BitSet` is used to track the active and next-active nodes.

### Why this is faster

The previous implementation scanned every graph node on every relaxation pass, even when most node distances had not changed.

The frontier-based approach avoids these unnecessary node scans and edge traversals by processing only nodes whose distances were improved in the previous pass.

This is particularly beneficial for the large road graph used in this project, where the active search area is much smaller than the full graph.

### Correctness

The implementation remains Bellman-Ford edge relaxation.

Whenever a node's distance improves, its outgoing edges are scheduled for relaxation in the following pass. The existing distance calculation, edge weighting, relaxation rule, early-convergence behavior, and output format remain unchanged.

The optimized implementation therefore produced the same observed shortest-path distance as the previous implementation.

### Complexity

- Previous implementation: `O(V(V + E))`, conventionally expressed as `O(VE)` for Bellman-Ford, with `O(V)` working memory.
- Optimized implementation: worst-case `O(VE)`, while avoiding full `O(V)` node scans and unnecessary edge work when the active frontier is sparse.
- Memory remains `O(V)`; the two frontier `BitSet`s add `O(V)` bits.

### Benchmark

|    Version     |     Execution Time    | Distance |
|----------------|----------------------:|---------:|
|    Baseline    | 1,705,729 ms (28:28)  | 920.46 m |
| Optimization 1 | 1,058,858 ms (17:40)  | 920.46 m |
| Optimization 2 | 143,386.742 ms (2:23) | 920.46 m |

**Observed improvement:** approximately **86.5% lower execution time than Optimization 1**, and approximately **91.6% lower execution time than the original baseline**.

The optimized run produced the same displayed route distance of **920.46 m**.

### Result

Optimization 2 substantially reduced Bellman-Ford execution time by eliminating repeated full-graph node scans and focusing relaxation work on the active frontier.