"""Utilities for calculating element distances from a Femap model edge.

The module provides a NumPy/SciPy calculation for element-centroid distances
and a wrapper that retrieves the required node and element data from Femap.
Femap node IDs are expected to use one-based numbering; they are converted to
zero-based indices internally for array and sparse-graph operations.
"""

import numpy as np
from scipy.sparse import csgraph, csr_matrix

from ..utils import get_connect_matrix, get_nodal_coords, get_nodal_ids

def compute_centroid_distances(nodes_xyz, elements, edge_node_indices):
    """Calculate each element centroid's shortest distance from a node edge.

    Parameters
    ----------
    nodes_xyz : array-like, shape (N_nodes, 3)
        Cartesian coordinates for the model nodes. Rows are indexed by the
        corresponding zero-based position in the element connectivity data.
    elements : array-like, shape (N_elements, M)
        Element corner node IDs using Femap's one-based numbering.
    edge_node_indices : array-like, shape (N_edge_nodes,)
        Node IDs defining the boundary edge, also using Femap's one-based
        numbering. These nodes are treated as zero-distance source nodes.

    Returns
    -------
    numpy.ndarray, shape (N_elements,)
        Shortest distance from each element centroid to the boundary edge,
        measured along the element connectivity graph and through the element
        corners.

    Notes
    -----
    The function converts Femap's one-based node IDs to zero-based NumPy
    indices internally and uses a sparse Dijkstra search for the mesh distance.
    """
    num_nodes = len(nodes_xyz)
    num_nodes_boundary = len(edge_node_indices)
    
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
    mesh_rows = np.concatenate([u_uniq, v_uniq])
    mesh_cols = np.concatenate([v_uniq, u_uniq])
    mesh_weights = np.concatenate([dists, dists])

    # Create a single "virtual node" to represent the boundary edge.
    # This allows the dijkstra algorithm to be used just once
    vir_node_idx = num_nodes # Give it the last index

    # Add the virtual node to the network. The virtual node has 0 distance to all the boundary nodes
    v_rows = np.full(num_nodes_boundary, vir_node_idx, dtype=int)
    v_cols = edge_node_indices
    v_weights = np.zeros(num_nodes_boundary, dtype=float)
    row_idx = np.concatenate([mesh_rows, v_rows, v_cols])
    col_idx = np.concatenate([mesh_cols, v_cols, v_rows])
    edge_weights = np.concatenate([mesh_weights, v_weights, v_weights])

    # Build a sparse matrix of distances. Row idx is from node, and col idx is to node
    graph = csr_matrix((edge_weights, (row_idx, col_idx)), shape=(num_nodes+1, num_nodes+1))

    # Single source Dijkstra run
    dist_vector = csgraph.dijkstra(csgraph = graph, directed=False, indices=vir_node_idx)
    node_distances = dist_vector[:num_nodes]

    # Vectorized centroid distances
    elem_coords = nodes_xyz[elements]
    centroids = np.mean(elem_coords, axis=1, keepdims=True)
    
    corner_to_centroid = np.linalg.norm(elem_coords - centroids, axis=2)
    dists_via_corners = node_distances[elements] + corner_to_centroid
    
    return np.min(dists_via_corners, axis=1)

def get_elem_dist_from_edge(app, elset, nset, nset_edge):
    """Return element-centroid distances from a Femap node-set edge.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    elset : int
        Femap ID of the element set whose distances should be calculated.
    nset : int
        Femap ID of the node set used to retrieve model coordinates.
    nset_edge : int
        Femap ID of the node set defining the boundary edge.

    Returns
    -------
    numpy.ndarray
        One distance value for each element in ``elset``, in the same order as
        returned by the element connectivity matrix.

    Notes
    -----
    The required Femap sets must exist and contain compatible element or node
    data before this function is called.
    """

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

