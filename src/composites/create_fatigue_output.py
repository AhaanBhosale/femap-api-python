from functions.utils import connect_to_femap, find_plies, create_output_vector
from functions.errors import check_error
import tkinter as tk
from tkinter import simpledialog
import sys
from pyfemap import constants
import numpy as np
from functions.ui_utils import get_user_inputs

# Connect to Femap application
app = connect_to_femap()

# Create a dictionary of default input values for the user to modify using a dialog box
defaults = {
    'direction': 1,
    'output sets (comma-separated)': '1,2,3',
    'gMa': 2.205,
    'gMb': 1.96,
    'gMd': 2.205,
    '%Rk,t': 2.05,
    '%Rk,c': 1.54,
    'm': 10,
    'n': 2000000,

}

# Ask the user for input and store the results
inputs = get_user_inputs(defaults)
dir = inputs['direction']
os_ids = [int(x) for x in inputs['output sets (comma-separated)'].split(",")]
gMa = inputs['gMa']
gMb = inputs['gMb']
gMd = inputs['gMd']
Rk_t = inputs['%Rk,t'] / 100
Rk_c = inputs['%Rk,c'] / 100
m = inputs['m']
n = inputs['n']

# Get the required vector ids. 
# For the same ply, different directions are consecutive.
ply1_id1 = 16000057 + dir

# Find all the plies in the model and the corresponding vector ids for the specified direction
# Use only the first output set id since all of them will have the same vector ids.
gap = 500
n_vecs = 1
all_vec_ids = find_plies(app, ply1_id1, gap, n_vecs, os_ids[0])

# Create a result browsing object and add a column for each vector id and each output set.
# The table will be organized as follows: [vec1_os1, vec1_os2, vec1_os3, vec2_os1, vec2_os2, vec2_os3, ...]
fr = app.feResults
for vec_id in all_vec_ids:
    for os_id in os_ids:
        rc, nCol, nColIds = fr.AddColumnV2(os_id, vec_id, False)
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

# Calculate the life for each element using the strain amplitude and the provided fatigue parameters
c1b = n**(1/m)
N = ((Rk_t + abs(Rk_c) - abs(2 * gMa * mean_strains - Rk_t + abs(Rk_c))) / (2 *gMb/c1b * strain_amplitudes))**m 
damage = n / N * 100
effort = (n/N) ** (1/m) *100

# Create a new output set to store the fatigue strain results
os_results = app.feOutputSet
os_results.title = "Fatigue Strain Results"
os_results_id = os_results.NextEmptyID()
rc = os_results.Put(os_results_id)
check_error(rc)

# Create the output vectos in femap
create_output_vector(app, np.column_stack((elems, strain_amplitudes)), os_results_id, "Strain Amplitude")
create_output_vector(app, np.column_stack((elems, mean_strains)), os_results_id, "Mean Strain")
create_output_vector(app, np.column_stack((elems, effort)), os_results_id, "Fatigue Effort")
create_output_vector(app, np.column_stack((elems, damage)), os_results_id, "Fatigue Damage")
create_output_vector(app, np.column_stack((elems, N)), os_results_id, "Fatigue Life (N)")

