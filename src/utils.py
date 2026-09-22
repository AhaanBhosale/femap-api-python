"""Helper functions for reading Femap node and element data into NumPy.

Help:
    These functions wrap Femap bulk-array API calls and convert the returned
    data into arrays used by the model-building workflows. Pass a connected
    Femap application object and a populated Femap set object to each helper.
"""

import numpy as np
import sys

# Get connectivity matrix of elements
def get_connect_matrix(app, elem_set):
    """Return the first four node IDs for each element in a Femap set.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    elem_set : femap.feSet
        Populated element set. Its ID is passed to Femap's bulk element API.

    Returns
    -------
    numpy.ndarray, shape (N_elements, 4)
        Element connectivity using Femap's node IDs. The helper reshapes the
        returned data using a 20-node record and keeps the first four entries.

    Raises
    ------
    SystemExit
        If the Femap bulk query does not return element data.
    """

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
    """Return the Femap node IDs contained in a node set.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    node_set : femap.feSet
        Populated node set whose ID is passed to Femap's bulk node API.

    Returns
    -------
    numpy.ndarray, shape (N_nodes,)
        Node IDs as floating-point NumPy values, preserving Femap numbering.

    Raises
    ------
    SystemExit
        If the Femap bulk query does not return node data.
    """

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
    """Return the Cartesian coordinates for nodes in a Femap node set.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    node_set : femap.feSet
        Populated node set whose ID is passed to Femap's bulk node API.

    Returns
    -------
    numpy.ndarray, shape (N_nodes, 3)
        Node coordinates as floating-point NumPy values in Femap model units.

    Raises
    ------
    SystemExit
        If the Femap bulk query does not return node data.
    """

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