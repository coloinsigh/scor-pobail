import osmnx as ox
import geopandas as gp
import networkx
from src import visualization
import matplotlib.cm as cm
import matplotlib.colors as mcolors

LOCATION = "Galway, Ireland"    # central point
DISTANCE = 10000.0              # radius of circle in m
SPEED = 5*1000/60               # assumed walking speed in m/min - 5km/h
MAX_DISTANCE = 5000.0
MAX_MINS = 30.0


def compute_edge_colours(nearest, g):
    """
    To aid with later visualization, transform the distance between nodes into an average value
    """
    # Ensure nearest dict values are in minutes
    node_times = {
    node: min(dist / SPEED, MAX_MINS)
    for node, dist in nearest.items()
    }

    # Assign an average walk time to each edge
    edge_times = []
    for u, v in g.edges():
        time_u = node_times.get(u, MAX_MINS)
        time_v = node_times.get(v, MAX_MINS)
        edge_times.append((time_u + time_v) / 2.0)

    norm = mcolors.Normalize(vmin=0, vmax=MAX_MINS)
    cmap = cm.viridis_r  # Green close, purple/dark far

    edge_colors = [cmap(norm(t)) for t in edge_times]
    return edge_colors


all_walkable_filter = (
    '["highway"]'
    '["area"!~"yes"]'
    '["highway"!~"motorway|motorway_link|trunk|trunk_link"]'
    '["foot"!~"no"]'
    '["access"!~"private"]'
)

# Fetch initial graph, centred at a specific location
g = ox.graph_from_address(LOCATION, DISTANCE, dist_type="bbox", custom_filter=all_walkable_filter, retain_all=True)

# Fetch list of amenities
features = ox.features_from_address(LOCATION, tags={'leisure': 'pitch'}, dist=DISTANCE)

# We compare nearest nodes using the pre-computed graph, using vectorization
centroids = features.geometry.centroid
# nearest_node = []

# # Handle deduplication of repeated nodes
# nearest_node_dedup = set(nearest_node)
nearest_node_dedup = set(ox.nearest_nodes(g, X=centroids.x, Y=centroids.y))

# Next, need to calculate the nearest node to every amenity
nearest = networkx.multi_source_dijkstra_path_length(g, sources=nearest_node_dedup, weight="length")

# Unpack nodes into a geodataframe
gdf_nodes = ox.graph_to_gdfs(g, edges=False)
gdf_nodes['feature_dist_m'] = gdf_nodes.index.map(nearest).fillna(MAX_DISTANCE)

# Now convert the metres to minutes, based on reasonable walking speed
gdf_nodes['feature_walk_min'] = gdf_nodes['feature_dist_m']/SPEED

# update fields in original geodataframe
for node_id, val in gdf_nodes["feature_walk_min"].items():
    g.nodes[node_id]["walk_time"] = val

# Handle edge colours
edge_colours = compute_edge_colours(nearest, g)
                                          
# Visualize time to walk through a colourmap
visualization.ox_native(g, nearest, edge_colours=edge_colours, edge_linewidth=1.2, node_size=0)
# visualization.plot_accessibility_graph(g, gdf_nodes['pitch_walk_min'], max_mins=MAX_MINUTES)