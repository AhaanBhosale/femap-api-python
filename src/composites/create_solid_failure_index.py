import pythoncom
import pyfemap
from pyfemap import constants
import sys
import numpy as np

def check_error(rc):
    if rc != constants.FE_OK:
        #sys.exit("Error code: " + str(rc))
        print("Skipping vector")

# Try making connection to Femap application
try:
    exist_obj = pythoncom.connect(pyfemap.model.CLSID)
    app = pyfemap.model(exist_obj)
except:
    sys.exit("Femap is not running. Please start Femap and try again.")

# User input
ply1_id1 = 16000088
n_vecs = 6
gap = 500
nPlies = 30

# Get the active output set id in femap
feView = app.feView
rc, viewID = app.feAppGetActiveView() 
rc = feView.Get(viewID)
output_set_id = feView.OutputSet

# Get all the required vector ids for all plies. Flatten it to a single array
ply1_ids = np.linspace(ply1_id1, ply1_id1+n_vecs-1, n_vecs, dtype=int)
all_vec_ids = []
for xi in range(nPlies):
    ply_vec_ids = ply1_ids + gap*xi
    all_vec_ids.append(ply_vec_ids)
all_vec_ids = np.array(all_vec_ids).flatten()

# Create a femap result browing object
fr = app.feResults

# Add a column for each vector id to the result browsing object
for vec_id in all_vec_ids:
    rc, nCol, nColIds = fr.AddColumnV2(output_set_id, vec_id, False)
    check_error(rc)

# Create an envelope for the failure index across all plies
#rc, nCol, envColID = fr.AddEnvelopeColumn(constants.FOPE_MAX)

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
for xi in range(fr.NumberOfRows()):

    # Get the element ids and data for this column
    rc, elemID, idxs = fr.GetRow(xi)
    check_error(rc)

    # Save the element number and the max failure index for this row
    if np.any(np.array(idxs) != 0):
        elems.append(elemID)
        fis.append(max(idxs))
    else:
        print("Element " + str(elemID) + " has zero failure index across all plies.")

# Extract the data from the rbo
#num_data_cols = fr.NumberOfColumns()
#rc, raw_data = fr.GetRowsByID(fs.ID)

# Convert to Numpy and Reshape
#full_table = np.array(raw_data).reshape(-1, num_data_cols)

# Extract the enveloped data
#rc, entIDs, dMax = fr.GetColumn(envColID)

# Get the element ids by reading a random column (here we read the first column, but it can be any column since they all have the same element ids)
#rc, entIDs, dMax = fr.GetColumn(0)
#check_error(rc)

# Create the enveloped data by taking the max across all the columns for each element
#dMax = np.max(full_table, axis=1)

# Delete the rows with zero values
#entIDs = np.nonzero(dMax)
#dMax = dMax[entIDs]

# Convert to list for putting back into femap
#dMax = dMax.tolist()
#entIDs = entIDs[0].tolist()

# Clear the result browsing object and create a new output vector in femap
fr.clear()
newVecID = fr.NonExistingUserVectorV2(output_set_id)
rc, newColIdx = fr.AddScalarAtElemColumnV2(output_set_id, newVecID, "Max Failure Index", constants.FOT_ANY, False)
check_error(rc)

# Put the Python data back into this new column and save
numVals = len(elems)
rc = fr.SetColumn(newColIdx, numVals, elems, fis)
check_error(rc)
rc = fr.Save()
check_error(rc)




