import osmnx as ox
import geopandas as gp
import networkx

LOCATION = "Galway, Ireland"    # central point
DISTANCE = 10000.0              # radius of circle in m
SPEED = 5*1000/3600             # assumed walking speed - 5km/h

# Fetch initial graph, centred at a specific location
g = ox.graph_from_address(LOCATION, DISTANCE, dist_type="bbox", network_type="walk", retain_all=True)

# Fetch list of amenities
pitches = ox.features_from_address(LOCATION, tags={'leisure': 'pitch'}, dist=DISTANCE)

# We compare nearest nodes using the pre-computed graph
nearest_node = []
for ind in range(len(pitches)):
    # iterate across all amenities and find nearest node
    p_loc = pitches.iloc[ind].iloc[0].centroid

    nearest_node.append(ox.nearest_nodes(g, p_loc.x, p_loc.y))
# Handle deduplication of repeated nodes
nearest_node_dedup = set(nearest_node)

# Next, need to calculate the nearest node to every amenity
nearest = networkx.multi_source_dijkstra_path_length(g, sources=nearest_node_dedup, weight="length")

# Unpack nodes into a geodataframe
gdf_nodes = ox.graph_from_gdfs(g, edges=False)
gdf_nodes['pitch_dist_m'] = gdf_nodes.index.map(nearest)

# Now convert the metres to minutes, based on reasonable walking speed
gdf_nodes['pitch_walk_min'] = gdf_nodes['pitch_dist_m']/SPEED