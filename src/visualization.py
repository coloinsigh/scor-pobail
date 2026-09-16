#!usr/bin/env python3

import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

"""
Collection of all tools to aid in visualization of graph data, either using osmnx or otherwise 
"""

def ox_native(g, nearest, node_size = 15, edge_colours="#333333", edge_linewidth=0.5, max_dist_colour_scale=3000.0):
    """
    Using a dict of nearest nodes, as output by networkx.multi_source_dijkstra_path_length(), plot a colourmap of time to walk
    """

    # Attach distances in meters to the graph
    for node_id, dist in nearest.items():
        g.nodes[node_id]["dist_feature"] = dist

    # # Prepare node colors: assign a fallback distance for disconnected nodes
    # max_dist = max_dist_colour_scale  # Cap at 3 km for color scaling
    # node_distances = [
    #     data.get("dist_feature", max_dist) 
    #     for _, data in g.nodes(data=True)
    # ]
    # Prepare node colors: assign a fallback distance for disconnected nodes
    max_dist = max_dist_colour_scale  # Cap at 3 km for color scaling
    node_distances = [
        data.get("walk_time", max_dist) 
        for _, data in g.nodes(data=True)
    ]

    # Plot with parameters used for node size, edge colour and edge linewidth
    fig, ax = ox.plot_graph(
        g,
        node_color=node_distances,
        node_size=node_size,
        edge_color=edge_colours,
        edge_linewidth=edge_linewidth,
        bgcolor="black",
        show=True
    )

    #TODO: add colourbar to signify colour mapping to specific minutes to pitch


def plot_accessibility_graph(g, walk_times_series, max_mins=60.0):
    # Align values with g.nodes order
    node_colors = [walk_times_series.get(node_id, max_mins) for node_id in g.nodes]
    
    cmap = cm.viridis_r
    norm = mcolors.Normalize(vmin=0, vmax=max_mins)

    fig, ax = ox.plot_graph(
        g,
        node_color=node_colors,
        node_size=12,
        edge_color="#222222",
        edge_linewidth=0.4,
        bgcolor="black",
        show=False,
        close=False
    )

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", shrink=0.7, pad=0.02)
    cbar.set_label("Walk Time to Nearest Feature (mins)", color="white", fontsize=10)
    cbar.ax.yaxis.set_tick_params(color="white", labelcolor="white")

    plt.show()
