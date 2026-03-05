import pythoncom
import pyfemap
from pyfemap import constants
import sys
import numpy as np
import tkinter as tk
from tkinter import simpledialog

def check_error(rc):
    if rc != constants.FE_OK:
        sys.exit("Error code: " + str(rc))


# Try making connection to Femap application
try:
    exist_obj = pythoncom.connect(pyfemap.model.CLSID)
    app = pyfemap.model(exist_obj)
except:
    sys.exit("Femap is not running. Please start Femap and try again.")

def find_plies(ply1_id1, gap, n_vecs, osID):

    # Setup a layup object
    layup = app.feLayup

    # Count the number of plies
    nPlies = 0
    while layup.Next() == constants.FE_OK:
        nPlies += layup.NumberOfPlys

    # Get the possible vector ids
    ply1_ids = np.linspace(ply1_id1, ply1_id1+n_vecs-1, n_vecs, dtype=int)
    all_vec_ids = []
    for xi in range(nPlies):
        ply_vec_ids = ply1_ids + gap*xi
        all_vec_ids.append(ply_vec_ids)
    all_vec_ids = np.array(all_vec_ids).flatten()

    # Keep only the vector ids that exist in the model
    out_ids = np.array([], dtype=int)
    for vec_id in all_vec_ids:
        if fr.VectorExistsV2(osID, vec_id):
            out_ids = np.append(out_ids, vec_id)
    return out_ids

# User input
ply1_id1 = 16000058
n_vecs = 1
gap = 500

# Ask user for output sets to consider using a dialog box
root = tk.Tk()
root.withdraw()  # Hide the main window
user_input = simpledialog.askstring("Input", "Enter output set IDs (comma-separated):")
root.destroy()

# Convert the user input into a list of integers
if user_input:
    output_set_ids = [int(x) for x in user_input.split(",")]
else:
    sys.exit("No output set IDs entered. Exiting.")

# Create a femap result browing object
fr = app.feResults

# Get the number of plies in the model. 
# Use the first output set id only since all the output sets should have the same plies and vector ids
all_vec_ids = find_plies(ply1_id1, gap, n_vecs, output_set_ids[0])

# Add a column for each vector id and each output set to the result browsing object
# The table will be organized as follows: [vec1_os1, vec1_os2, vec1_os3, vec2_os1, vec2_os2, vec2_os3, ...]
for vec_id in all_vec_ids:
    for osID in output_set_ids:
        rc, nCol, nColIds = fr.AddColumnV2(osID, vec_id, False)
        check_error(rc)

# Create a set of all elements
fs = app.feSet
rc = fs.AddAll(constants.FT_ELEM)
check_error(rc)

# Ask femap to calculate results for all the elements, and populate the rbo
rc = fr.DataNeeded(constants.FT_ELEM, fs.ID)
check_error(rc)
rc = fr.Populate()  
check_error(rc)

# Get the element number and max failure index for each element in the result browsing object
n_elems = fr.NumberOfRows()
col_idx = np.arange(0, fr.NumberOfColumns())
max_strains = np.zeros(n_elems)
min_strains = np.zeros(n_elems)
mean_strains = np.zeros(n_elems)
elems = []
for xi in range(n_elems):

    # Get the element ids and data for this column
    rc, elemID, idxs = fr.GetRow(xi)
    check_error(rc)

    # Get the max strain , min strain and mean strain for this element
    max_strains[xi] = max(idxs)
    min_strains[xi] = min(idxs)
    mean_strains[xi] = np.mean(idxs)

    # Save the element number only if strain data exists for this element
    if not (max_strains[xi]==0 and min_strains[xi]==0):
        elems.append(elemID)

# Calculate the strain amplitude for each element
strain_amplitudes = (max_strains - min_strains) / 2

# Create a new output set to store the fatigue strain results
os_results = app.feOutputSet
os_results.title = "Fatigue Strain Results"
os_results_id = os_results.NextEmptyID()
rc = os_results.Put(os_results_id)
check_error(rc)

# Clear the result browsing object and create a new output vector in femap for the strain amplitude results
fr.clear()
newVecID = fr.NonExistingUserVectorV2(os_results_id)
rc, newColIdx = fr.AddScalarAtElemColumnV2(os_results_id, newVecID, "Strain Amplitude", constants.FOT_ANY, False)
check_error(rc)

# Put the Python data back into this new column and save
numVals = len(elems)
rc = fr.SetColumn(newColIdx, numVals, elems, strain_amplitudes)
check_error(rc)
rc = fr.Save()
check_error(rc)

# Print to femap console
app.feAppMessage(0, "Succesfully created Strain Amplitude output.")

# Clear the result browsing object and create a new output vector in femap for the mean strain results
fr.clear()
newVecID = fr.NonExistingUserVectorV2(os_results_id)
rc, newColIdx = fr.AddScalarAtElemColumnV2(os_results_id, newVecID, "Mean Strain", constants.FOT_ANY, False)
check_error(rc)

# Put the Python data back into this new column and save
numVals = len(elems)
rc = fr.SetColumn(newColIdx, numVals, elems, mean_strains)
check_error(rc)
rc = fr.Save()
check_error(rc)

# Print to femap console
app.feAppMessage(0, "Succesfully created Mean Strain output.")

