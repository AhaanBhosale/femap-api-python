import numpy as np
import sys

# Get connectivity matrix of elements
def get_connect_matrix(app, elem_set):

    #Initialize the Element entity object
    fe_elem = app.feElem

    # Bulk import data for the set. 
    rc, _,_, _, _, _, _, _, _, _, _, _, _, _, connect_flatten, *_ = fe_elem.GetAllArray(elem_set.ID)
    if rc == -1:
        # By default, every element has 20 nodes.
        connectivity_matrix = np.asarray(connect_flatten).reshape(-1, 20)

        # Keep only the 4 nodes of interest
        connectivity_matrix = connectivity_matrix[:, :4]

        # Return
        return connectivity_matrix
    else:
        sys.error("No elements present in current set")

# Get nodal ids
def get_nodal_ids(app, node_set):

    # Create a node object
    fe_node = app.feNode

    # Bulk import data for nodes in set
    rc, _,  node_id_flat, *_ = fe_node.GetAllArray(node_set.ID)

    # Extract ids if exists
    if rc == -1:
        ids = np.asarray(node_id_flat, dtype=np.float64)
        return ids
    else:
        sys.exit("No nodes found in nodeset")

# Get nodal coordinates
def get_nodal_coords(app, node_set):

    # Create a node object
    fe_node = app.feNode

    # Bulk import data for nodes in set
    rc, _,  _, coords_flat, *_ = fe_node.GetAllArray(node_set.ID)

    # Extract coordinates if exists
    if rc == -1:
        coords = np.asarray(coords_flat, dtype=np.float64).reshape(-1, 3)
        return coords
    else:
        sys.exit("No nodes found in nodeset")