"""Build and assign composite properties in the active Femap model.

Help:
    Run this script while Femap is open with a model loaded. Select the
    leading edge, trailing edge, and root node sets when prompted, then choose
    an Excel layup-definition file. The script creates the required materials,
    calculates each element's distance from the selected boundaries, creates
    composite layup properties, and assigns those properties to the elements.

    The Excel file must contain the material, thickness, and boundary-offset
    columns expected by the workflow. Install the project dependencies before
    running the script.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import pythoncom
import pyfemap
from pyfemap import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from .get_elem_dist_from_edge import get_elem_dist_from_edge

def check_error(rc):
    """Exit the script when a Femap API call does not return ``FE_OK``.

    Parameters
    ----------
    rc : int
        Return code from a Femap API operation.
    """
    if rc != constants.FE_OK:
        sys.exit(f"Femap API Error code: {rc}")

def create_mats_from_df(app, df):
    """Create one orthotropic material for each unique material name.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    df : pandas.DataFrame
        Layup definition table containing a ``Material`` column.

    Returns
    -------
    dict
        Mapping from material names in ``df`` to the newly created Femap
        material IDs.
    """

    # Extract all the unique materials from the dataframe
    df_uniq = df.drop_duplicates(subset="Material", keep="first")

    # Initialise an array to store index of material objects
    mat_ids = np.empty(shape=(len(df_uniq,)), dtype=np.int64)

    # Add each material to the array
    xi = 0
    for row in df_uniq.itertuples(index=False):

        # Create a material object
        curr_mat = app.feMatl
        id = curr_mat.NextEmptyID()
        curr_mat.type = 1 #Orthotropic 2D
        curr_mat.title = row.Material

        # Add it to the window
        rc = curr_mat.Put(id)
        check_error(rc)

        # Save the mat id in the array
        mat_ids[xi] = id
        xi += 1

    # Create dictionary of names and id pairings
    out = dict(zip(df_uniq["Material"], mat_ids))
    return out

def create_property_per_elem(app, layup_list, thickness_list):
    """Create or reuse a Femap composite property for each element layup.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    layup_list : sequence of sequence of int
        Material IDs for each element, ordered through the element layup.
        Empty layups receive a property ID of ``-1``.
    thickness_list : sequence of sequence of float
        Ply thicknesses corresponding to ``layup_list``.

    Returns
    -------
    numpy.ndarray
        Property ID for each element, or ``-1`` when no layup is assigned.
    """

    # Iterate through each layup
    prev_layups = []
    prev_prop_idx = []
    out = np.empty(shape=(len(layup_list,)), dtype=np.int64)
    for xi in range(len(layup_list)):

        # COntinue if no layup
        if not layup_list[xi]:
            out[xi] = -1
            continue

        # Get the current layup
        curr_layup = layup_list[xi]
        curr_ts = thickness_list[xi]

        # Check if existing layup is already created. If so, use the existing layup id
        match_idx = next((idx for idx, arr in enumerate(prev_layups) if np.array_equal(curr_layup, arr)), None)
        if match_idx:
            out[xi] = prev_prop_idx[match_idx]
            continue

        # Create the layup
        fe_layup = app.feLayup
        id = fe_layup.NextEmptyID()
        fe_layup.title = 'Layup-'+ str(xi)
        for xj in range(len(curr_layup)):
            fe_layup.AddPly(curr_layup[xj], curr_ts[xj], 0, 0)

        # ADd the layup to the app
        rc = fe_layup.Put(id)

        # Create a property with this layup
        fe_prop = app.feProp
        prop_id = fe_prop.NextEmptyID()
        fe_prop.title = 'Property' + str(xi)
        fe_prop.type = 21
        fe_prop.layupID = id

        # Add the property to the app
        rc = fe_prop.Put(prop_id)
        check_error(rc)

        # Save the layup ids and update the prev layup list
        out[xi] = prop_id
        prev_layups.append(curr_layup)
        prev_prop_idx.append(prop_id)

    return out

def assign_property_to_element(app, elset, prop_ids):
    """Assign the supplied Femap property IDs to the elements in a set.

    Parameters
    ----------
    app : femap.model
        Connected Femap application object.
    elset : femap.feSet
        Element set whose elements will receive properties. Elements are read
        in the set's iteration order.
    prop_ids : sequence of int
        Property ID for each element in ``elset``. Negative IDs are skipped.

    Notes
    -----
    The function resets the module-level ``elset_all`` set before iterating,
    so the supplied set is expected to be that active element set.
    """

    # Rest the pointer for the set
    elset_all.Reset()

    # initialise a holder element object
    fe_elem = app.feElem

    for xi in range(len(elset)):

        # Get current element id. Done before checking if property exists
        # to make sure element id is incremented
        rc = fe_elem.Get(elset.Next())
        check_error(rc)
        el_id = fe_elem.ID

        # Check if property exists for element
        if prop_ids[xi] < 0 :
            continue

        # Assign the property to the element
        fe_elem.propID = prop_ids[xi]
        fe_elem.Put(el_id)

# Connect to running Femap application
try:
    exist_obj = pythoncom.connect(pyfemap.model.CLSID)
    app = pyfemap.model(exist_obj)
except Exception:
    sys.exit("Femap is not running. Please start Femap and try again.")

# Select nodes for the boundaries of the model
nset_LE = app.feSet
rc = nset_LE.Select(constants.FT_NODE, True, "Select Nodes on the leading edge")
if rc != constants.FE_OK or nset_LE.Count() == 0:
    sys.exit("No nodes selected or selection was cancelled.")

nset_TE = app.feSet
rc = nset_TE.Select(constants.FT_NODE, True, "Select Nodes on the trailing edge")
if rc != constants.FE_OK or nset_TE.Count() == 0:
    sys.exit("No nodes selected or selection was cancelled.")

nset_root = app.feSet
rc = nset_root.Select(constants.FT_NODE, True, "Select Nodes on the root")
if rc != constants.FE_OK or nset_root.Count() == 0:
    sys.exit("No nodes selected or selection was cancelled.")

# Create a set of all the elements and nodes
elset_all = app.feSet
rc = elset_all.AddAll(constants.FT_ELEM)
check_error(rc)
nset_all = app.feSet
rc = nset_all.AddAll(constants.FT_NODE)
check_error(rc)

# Read the excel file with the layup definition
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
file = filedialog.askopenfilename(parent=root, title="Select the layup definition Excel file", filetypes=[("Excel files", "*.xlsx *.xls")])
root.destroy()
if not file:
    sys.exit("No file selected.")
layup_df = pd.read_excel(file)

# Create the materials in the app and get the mapping of material name and id in femap
mat_map = create_mats_from_df(app, layup_df)

# Find the distance of each element from each edge
dist_le = get_elem_dist_from_edge(app, elset_all, nset_all, nset_LE)
dist_te = get_elem_dist_from_edge(app, elset_all, nset_all, nset_TE)
dist_root = get_elem_dist_from_edge(app, elset_all, nset_all, nset_root)

# initialise empty 2d list for storage of material layup per element
mat_layup_per_elem = [[] for _ in range(len(elset_all))]
layup_thickness_per_elem = [[] for _ in range(len(elset_all))]

# Go line by line through the layup definition to assign the layup to the elements
for row in layup_df.itertuples():

    # Get the current material id and thickness from the map
    mat_id = mat_map[row.Material]
    mat_thickness = row[3]

    # Get the values
    offset_le = row[4]
    offset_te = row[5]
    offset_root1 = row[7]
    offset_root2 = row[8]

    # Get the elements that meet the criteria of being within the boundary of this ply
    is_in_bound = (
        (dist_le >= offset_le)
        & (dist_te >= offset_te)
        & (dist_root >= offset_root1)
        & (dist_root <= offset_root2)
    )

    # Add the current material id to all the elements where the criteria is true
    for xi, in_bound in enumerate(is_in_bound):
        if in_bound:
            mat_layup_per_elem[xi].append(mat_id)
            layup_thickness_per_elem[xi].append(mat_thickness)

# Create all the properties with the layups
prop_ids = create_property_per_elem(app, mat_layup_per_elem, layup_thickness_per_elem)

# Assign the properties to the elements
assign_property_to_element(app, elset_all, prop_ids)
