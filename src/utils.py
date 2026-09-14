import numpy as np

# Get connectivity matrix of elements
def get_connect_matrix(app, elem_set):
    
    connectivity_list = []
    element_ids = []

    #Initialize the Element entity object
    fe_elem = app.feElem

    # 4. Iterate through element IDs in the Set
    elem_id = elem_set.First()
    while elem_id > 0:
        rc = fe_elem.Get(elem_id)
        if rc == -1:  # FE_OK
            # fe_elem.Nodes returns a tuple of node IDs for the element (fixed length, usually 8 or 20)
            nodes = list(fe_elem.Nodes)
            
            # Trim trailing zero IDs (empty node slots in FEMAP's fixed-size node buffer)
            # or slice based on topology (e.g., fe_elem.Topology)
            active_nodes = [n for n in nodes if n > 0]
            
            element_ids.append(elem_id)
            connectivity_list.append(active_nodes)
            
        elem_id = elem_set.Next()

    # Convert to NumPy array (if uniform topology, e.g., all QUAD4s)
    # Note: FEMAP node IDs are 1-based; subtract 1 if mapping to 0-based coordinate arrays.
    try:
        connectivity_matrix = np.array(connectivity_list, dtype=np.int64)
        print(f"Connectivity Matrix Shape: {connectivity_matrix.shape}")
    except ValueError:
        # Handles mixed topologies (e.g., mixed TRIs and QUADs)
        print("Mixed element topologies detected; stored as variable-length list.")
        connectivity_matrix = connectivity_list

    print(f"Processed {len(element_ids)} elements.")
    return connectivity_matrix

# Get nodal ids
def get_nodal_ids(app, node_set):

    # Initialize empty array
    ids = np.empty(shape=(len(node_set),), dtype= np.int64)

    # Initialize the empty node object
    fe_node = app.feNode

    # Reset the set pointer
    node_set.Reset()

    # Iterate through all the nodes
    for xi in range(len(node_set)):

        rc = fe_node.Get(node_set.Next())
        if rc == -1:  # FE_OK
            ids[xi] = fe_node.ID

    # return the ids
    return ids

# Get nodal coordinates
def get_nodal_coords(app, node_set):

    # Initialize empty array
    coords = np.empty(shape=(len(node_set),3), dtype=np.float64)

    # Initialize the empty node object
    fe_node = app.feNode

    # Reset the set pointer
    node_set.Reset()

    # Iterate through all the nodes
    for xi in range(len(node_set)):
        rc = fe_node.Get(node_set.Next())
        if rc == -1:  # FE_OK
            coords[xi] = [fe_node.x, fe_node.y, fe_node.z]

    # return the ids
    return coords