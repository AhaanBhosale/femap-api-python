import pythoncom
import pyfemap
from pyfemap import constants
import sys
import numpy as np

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
ply1_id1 = 16000026
n_vecs = 2
gap = 500

# Get the active output set id in femap
feView = app.feView
rc, viewID = app.feAppGetActiveView() 
rc = feView.Get(viewID)
output_set_id = feView.OutputSet

# Create a femap result browing object
fr = app.feResults

# Get the number of plies in the model
all_vec_ids = find_plies(ply1_id1, gap, n_vecs, output_set_id)

# Add a column for each vector id to the result browsing object
for vec_id in all_vec_ids:
    rc, nCol, nColIds = fr.AddColumnV2(output_set_id, vec_id, False)
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
elems = []
fis = []
col_idx = np.arange(0, fr.NumberOfColumns())
shears = np.zeros(fr.NumberOfColumns()//2)
for xi in range(fr.NumberOfRows()):

    # Get the element ids and data for this column
    rc, elemID, idxs = fr.GetRow(xi)
    check_error(rc)

    # Iteratre through each row, and find the shear failure index for each ply seperately
    for xj, xk in zip(col_idx[0::2], col_idx[1::2]):
    
        # Get the S23 and S13 stresses for this element and ply
        S23 = idxs[xj]
        S13 = idxs[xk]

        # Calculate the pythagorean sum
        shear_total = np.sqrt(S23**2 + S13**2)

        # Update the array
        shears[xj//2] = shear_total

    # Save the element number and the max failure index for this row
    if np.any(np.array(shears) != 0):
        elems.append(elemID)
        fis.append(max(shears))

# Clear the result browsing object and create a new output vector in femap
fr.clear()
newVecID = fr.NonExistingUserVectorV2(output_set_id)
rc, newColIdx = fr.AddScalarAtElemColumnV2(output_set_id, newVecID, "RMS OOP Shear Stress", constants.FOT_ANY, False)
check_error(rc)

# Put the Python data back into this new column and save
numVals = len(elems)
rc = fr.SetColumn(newColIdx, numVals, elems, fis)
check_error(rc)
rc = fr.Save()
check_error(rc)

# Print to femap console
app.feAppMessage(0, "Succesfully created RMS OOP Shear Stress output.")



