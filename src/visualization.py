#!usr/bin/env python3

import osmnx as ox
import numpy as np

"""
Collection of all tools to aid in visualization of graph data, either using osmnx or otherwise 
"""

def ox_native(g, nearest):
    """
    Using a dict of nearest nodes, as output by networkx.multi_source_dijkstra_path_length(), plot a colourmap of time to walk
    """

    # Attach distances in meters to the graph
    for node_id, dist in nearest.items():
        g.nodes[node_id]["dist_pitch"] = dist

    # Prepare node colors: assign a fallback distance for disconnected nodes
    max_dist = 3000.0  # Cap at 3 km for color scaling
    node_distances = [
        data.get("dist_pitch", max_dist) 
        for _, data in g.nodes(data=True)
    ]

    fig, ax = ox.plot_graph(
        g,
        node_color=node_distances,
        node_size=15,
        edge_color="#333333",
        edge_linewidth=0.5,
        bgcolor="black",
        show=True
    )
    #TODO: add colourbar to signify colour mapping to specific minutes to pitch
