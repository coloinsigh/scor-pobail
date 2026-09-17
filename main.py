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

g = ox.projection.project_graph(g, to_crs='EPSG:2157')
                                          
# Visualize time to walk through a colourmap
visualization.ox_native(g, nearest, edge_colours=None, edge_linewidth=1.2, node_size=0)
# visualization.plot_accessibility_graph(g, gdf_nodes['pitch_walk_min'], max_mins=MAX_MINUTES)