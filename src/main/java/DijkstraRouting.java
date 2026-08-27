import com.graphhopper.GraphHopper;
import com.graphhopper.jackson.Jackson;
import com.graphhopper.config.Profile;
import com.graphhopper.routing.ev.BooleanEncodedValue;
import com.graphhopper.routing.weighting.Weighting;
import com.graphhopper.storage.BaseGraph;
import com.graphhopper.storage.index.LocationIndex;
import com.graphhopper.storage.index.Snap;
import com.graphhopper.util.EdgeExplorer;
import com.graphhopper.util.EdgeIterator;
import com.graphhopper.util.PMap;
import com.graphhopper.util.CustomModel;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class DijkstraRouting {

    // ------------------------------------------------------------
    // Test coordinate
    // Same coordinates as the Bellman-Ford baseline.
    // ------------------------------------------------------------

    static class Point {
        double lat;
        double lon;

        Point(double lat, double lon) {
            this.lat = lat;
            this.lon = lon;
        }
    }

    // ------------------------------------------------------------
    // Result
    // ------------------------------------------------------------

    static class Result {
        double distanceMeters;
        long elapsedNanos;

        Result(double distanceMeters, long elapsedNanos) {
            this.distanceMeters = distanceMeters;
            this.elapsedNanos = elapsedNanos;
        }
    }

    // ------------------------------------------------------------
    // Priority-queue entry
    // ------------------------------------------------------------

    static class NodeDistance implements Comparable<NodeDistance> {
        int node;
        double distance;

        NodeDistance(int node, double distance) {
            this.node = node;
            this.distance = distance;
        }

        @Override
        public int compareTo(NodeDistance other) {
            return Double.compare(this.distance, other.distance);
        }
    }

    // ------------------------------------------------------------
    // Convert latitude/longitude to nearest routable graph node
    // ------------------------------------------------------------

    static int snapToNode(
            LocationIndex locationIndex,
            double lat,
            double lon,
            BooleanEncodedValue carAccess
    ) {

        Snap snap = locationIndex.findClosest(
                lat,
                lon,
                edge -> edge.get(carAccess)
        );

        if (!snap.isValid()) {
            throw new IllegalArgumentException(
                    "Could not snap coordinate: "
                    + lat + ", " + lon
            );
        }

        return snap.getClosestNode();
    }

    // ------------------------------------------------------------
    // Naive Dijkstra
    // ------------------------------------------------------------

    static Result runDijkstra(
            BaseGraph graph,
            Weighting weighting,
            int source,
            int target
    ) {

        long start = System.nanoTime();

        int nodeCount = graph.getNodes();

        double[] distance = new double[nodeCount];

        Arrays.fill(
                distance,
                Double.POSITIVE_INFINITY
        );

        distance[source] = 0.0;

        PriorityQueue<NodeDistance> queue =
                new PriorityQueue<>();

        queue.add(
                new NodeDistance(source, 0.0)
        );

        EdgeExplorer edgeExplorer =
                graph.createEdgeExplorer();

        while (!queue.isEmpty()) {

            NodeDistance current =
                    queue.poll();

            int node = current.node;
            double currentDistance =
                    current.distance;

            // Ignore stale queue entries.
            if (currentDistance >
                    distance[node]) {
                continue;
            }

            // Target has been settled.
            if (node == target) {
                break;
            }

            EdgeIterator edges =
                    edgeExplorer.setBaseNode(node);

            while (edges.next()) {

                int adjacentNode =
                        edges.getAdjNode();

                double edgeWeight =
                        weighting.calcEdgeWeight(
                                edges,
                                false
                        );

                if (Double.isInfinite(edgeWeight)) {
                    continue;
                }

                double newDistance =
                        currentDistance + edgeWeight;

                if (newDistance <
                        distance[adjacentNode]) {

                    distance[adjacentNode] =
                            newDistance;

                    queue.add(
                            new NodeDistance(
                                    adjacentNode,
                                    newDistance
                            )
                    );
                }
            }
        }

        long elapsed =
                System.nanoTime() - start;

        if (Double.isInfinite(distance[target])) {
            return new Result(
                    Double.POSITIVE_INFINITY,
                    elapsed
            );
        }

        return new Result(
                distance[target],
                elapsed
        );
    }

    // ------------------------------------------------------------
    // MAIN
    // ------------------------------------------------------------

    public static void main(String[] args) throws IOException {

        System.out.println(
                "Loading existing GraphHopper graph..."
        );

        // --------------------------------------------------------
        // Tell GraphHopper where the existing graph lives.
        //
        // We are NOT importing the PBF.
        // --------------------------------------------------------

        GraphHopper hopper =
                new GraphHopper();

        hopper.setGraphHopperLocation(
                "graphhopper/graph-cache"
        );

        hopper.setAllowWrites(false);

        CustomModel carModel = Jackson.newObjectMapper().readValue(
                new File("graphhopper/aarambh-car.json"),
                CustomModel.class
        );

        Profile carProfile =
                new Profile("car")
                        .putHint(
                                "custom_model_files",
                                List.of("aarambh-car.json")
                        );

        carProfile.getHints().remove("custom_model");
        carProfile.setCustomModel(carModel);

        hopper.setProfiles(carProfile);

        // Load existing graph-cache.
        boolean loaded =
                hopper.load();

        if (!loaded) {
            throw new RuntimeException(
                    "Could not load graph-cache."
            );
        }

        System.out.println(
                "Graph loaded successfully."
        );

        // --------------------------------------------------------
        // Get underlying road graph.
        // --------------------------------------------------------

        BaseGraph graph =
                hopper.getBaseGraph();

        System.out.println(
                "Nodes: " + graph.getNodes()
        );

        System.out.println(
                "Edges: " + graph.getEdges()
        );

        // --------------------------------------------------------
        // Get car routing profile.
        // --------------------------------------------------------

        Profile carProfile1 =
                hopper.getProfile("car");

        if (carProfile1 == null) {
            throw new RuntimeException(
                    "Car profile not found."
            );
        }

        Weighting weighting =
                hopper.createWeighting(
                        carProfile1,
                        new PMap()
                );

        // --------------------------------------------------------
        // Location index.
        // --------------------------------------------------------

        LocationIndex locationIndex =
                hopper.getLocationIndex();

        BooleanEncodedValue carAccess =
                hopper.getEncodingManager()
                        .getBooleanEncodedValue(
                                "car_access"
                        );

        // --------------------------------------------------------
        // TEST CASE
        //
        // Same coordinates as the Bellman-Ford baseline.
        // --------------------------------------------------------

        Point A =
                new Point(
                        12.9719,
                        77.6412
                );

        Point B =
                new Point(
                        12.9320,
                        77.6227
                );

        // --------------------------------------------------------
        // Snap coordinates to graph nodes.
        // --------------------------------------------------------

        int source =
                snapToNode(
                        locationIndex,
                        A.lat,
                        A.lon,
                        carAccess
                );

        int target =
                snapToNode(
                        locationIndex,
                        B.lat,
                        B.lon,
                        carAccess
                );

        System.out.println(
                "Source node: " + source
        );

        System.out.println(
                "Target node: " + target
        );

        // --------------------------------------------------------
        // Run Dijkstra.
        // --------------------------------------------------------

        System.out.println(
                "\nRunning Dijkstra..."
        );

        Result result =
                runDijkstra(
                        graph,
                        weighting,
                        source,
                        target
                );

        // --------------------------------------------------------
        // Results.
        // --------------------------------------------------------

        System.out.println(
                "\n========== RESULTS =========="
        );

        System.out.printf(
                "Distance: %.2f m%n",
                result.distanceMeters
        );

        System.out.printf(
                "Distance: %.3f km%n",
                result.distanceMeters / 1000.0
        );

        System.out.printf(
                "Execution time: %.3f ms%n",
                result.elapsedNanos / 1_000_000.0
        );

        System.out.println(
                "=============================="
        );

        hopper.close();
    }
}
