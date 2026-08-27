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


++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


### Optimization 3: Reuse Frontier BitSets

#### Change

Reused the two `BitSet` frontier objects across Bellman-Ford relaxation passes instead of allocating a new `nextActiveNodes` `BitSet` on every pass.

The implementation now:

- Allocates `activeNodes` and `nextActiveNodes` once.
- Clears `nextActiveNodes` at the beginning of each pass.
- Swaps the two frontier references after a non-empty pass.
- Preserves the existing frontier-based relaxation from Optimization 2.

#### Why it should be faster

The previous implementation allocated a new `BitSet` for every Bellman-Ford iteration. On longer searches, these repeated allocations can increase allocation and garbage-collection overhead.

Reusing the two `BitSet` instances eliminates those per-pass allocations while preserving the same frontier contents and relaxation sequence.

#### Correctness

The optimization does not change the Bellman-Ford relaxation logic. `clear()` produces the same empty frontier state as a newly allocated `BitSet`, and the populated next frontier becomes the active frontier after each pass.

Edge weighting, directed traversal, distance updates, source and target nodes, and early convergence behavior remain unchanged.

#### Complexity

- **Time:** remains worst-case `O(VE)`. The optimization reduces allocation and garbage-collection overhead rather than changing the asymptotic amount of relaxation work.
- **Memory:** remains `O(V)`.
- **Frontier allocation:** reduced from repeated per-pass allocation to two reusable `BitSet` objects.

#### Result

The optimized implementation produced the same route distance:

**920.46 m (0.920 km)**

Observed execution time:

**238,572.687 ms ≈ 3.98 min**

This was substantially faster than the 28:28 baseline and confirms that the third optimization runs successfully while preserving the observed result.

> Note: this result is an observed single-run comparison, not a controlled multi-run benchmark.