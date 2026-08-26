import osmnx as ox
import geopandas as gp
import time

print(f"OSMNX vesion {ox.__version__}")
print(f"Geopandas vesion {gp.__version__}")

LOCATION = "Galway, Ireland"    # central point
DISTANCE = 10000.0              # radius of circle in m

# Fetch initial graph, centred at a specific location
g = ox.graph_from_address(LOCATION, DISTANCE, dist_type="bbox", network_type="walk", retain_all=True)

# Fetch list of amenities
pitches = ox.features_from_address(LOCATION, tags={'leisure': 'pitch'}, dist=DISTANCE)

# We compare nearest nodes using the pre-computed graph
nearest_node = []
for ind in range(len(pitches)):
    # iterate across all amenities and find nearest node
    p_loc = pitches.iloc[ind][0].centroid

    nearest_node.append(ox.nearest_nodes(g, p_loc.x, p_loc.y))
# Handle deduplication of repeated nodes
nearest_node_dedup = set(nearest_node)
