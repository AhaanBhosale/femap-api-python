import os
import sys
import numpy as np
from scipy.sparse import csgraph, csr_matrix

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_connect_matrix, get_nodal_coords, get_nodal_ids

def compute_centroid_distances(nodes_xyz, elements, edge_node_indices):
    """
    nodes_xyz: (N_nodes, 3) float array of coordinates
    elements: (N_elements, M) int array of corner node IDs (1-based from FEMAP)
    edge_node_indices: 1D array-like of boundary source node IDs (1-based from FEMAP)
    """
    num_nodes = len(nodes_xyz)
    
    # Convert 1-based FEA IDs to 0-based Python indices
    elements = np.asarray(elements) - 1
    edge_node_indices = np.asarray(edge_node_indices) - 1
    
    # Vectorized edge extraction. 
    # Here, corresponding edges of u and v describe the element edge
    u = elements.flatten()
    v = np.roll(elements, shift=-1, axis=1).flatten()

    # Keep only the unique u,v pairings, since the pairing can occur
    # along elements with shared edges
    uv = np.sort(np.column_stack([u,v]), axis= 1)
    uniq_uv = np.unique(uv, axis=0)
    u_uniq = uniq_uv[:, 0]
    v_uniq = uniq_uv[:, 1]

    # Euclidean edge lengths across all elements
    dists = np.linalg.norm(nodes_xyz[u_uniq] - nodes_xyz[v_uniq], axis=1)
    
    # Graph construction
    row_idx = np.concatenate([u_uniq, v_uniq])
    col_idx = np.concatenate([v_uniq, u_uniq])
    edge_weights = np.concatenate([dists, dists])
    
    graph = csr_matrix((edge_weights, (row_idx, col_idx)), shape=(num_nodes, num_nodes))

    # Multi-source Dijkstra
    dist_matrix = csgraph.dijkstra(csgraph=graph, directed=False, indices=edge_node_indices)
    node_distances = np.min(dist_matrix, axis=0)

    # Vectorized centroid distances
    elem_coords = nodes_xyz[elements]
    centroids = np.mean(elem_coords, axis=1, keepdims=True)
    
    corner_to_centroid = np.linalg.norm(elem_coords - centroids, axis=2)
    dists_via_corners = node_distances[elements] + corner_to_centroid
    
    return np.min(dists_via_corners, axis=1)


def get_elem_dist_from_edge(app, elset, nset, nset_edge):

    # Get nodal ids of the edge
    edge_ids = get_nodal_ids(app, nset_edge)

    # Get all nodal coordinates
    coords = get_nodal_coords(app, nset)

    # Get element connectivity matrix
    conn = get_connect_matrix(app, elset)

    # Get distances of each element centroid from the edge
    dists = compute_centroid_distances(coords, conn, edge_ids)

    # return
    return dists

