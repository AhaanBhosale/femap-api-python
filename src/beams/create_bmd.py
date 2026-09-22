"""Create a bending moment diagram for selected Femap beam/bar elements.

Help
----
Prerequisites:
        - Femap must be open with a model loaded.
        - The active view should reference an output set containing beam moment
            results. If no output set is active, the first available output set is
            used.
        - Python dependencies from requirements.txt must be installed.

Usage:
        1. Run this script while Femap is open.
        2. Select the beam or bar elements to include in the diagram.
        3. Enter optional X-coordinates, separated by commas, to label the nearest
             plotted points.
        4. Review the generated Plane 1 End A moment diagram in the plot window.

The script reads the Plane 1 End A moment result (vector 3014), sorts selected
elements by the X-coordinate of their End A node, and plots the resulting
moment diagram with optional annotations.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import pythoncom
import pyfemap
from pyfemap import constants

def check_error(rc):
    if rc != constants.FE_OK:
        sys.exit(f"Femap API Error code: {rc}")

# 1. Connect to running Femap application
try:
    exist_obj = pythoncom.connect(pyfemap.model.CLSID)
    app = pyfemap.model(exist_obj)
except Exception:
    sys.exit("Femap is not running. Please start Femap and try again.")

# 2. Get active output set from current view
feView = app.feView
rc, viewID = app.feAppGetActiveView()
check_error(rc)
rc = feView.Get(viewID)
check_error(rc)

output_set_id = feView.OutputSet
if output_set_id <= 0:
    # Fallback to the first available output set if no active view set is chosen
    feOutputSet = app.feOutputSet
    rc = feOutputSet.First()
    check_error(rc)
    output_set_id = feOutputSet.ID

# Nastran/Femap standard output vector for Beam EndA Plane 1 Moment
VEC_PLANE1_MOMENT = 3014

# 3. Select beam/bar elements using feSet
fs = app.feSet
rc = fs.Select(constants.FT_ELEM, True, "Select Beam Elements to Plot")
if rc != constants.FE_OK or fs.Count() == 0:
    sys.exit("No elements selected or selection was cancelled.")

# 4. Populate Results Browsing Object (feResults)
fr = app.feResults
rc, nCol, nColIds = fr.AddColumnV2(output_set_id, VEC_PLANE1_MOMENT, False)
check_error(rc)

rc = fr.DataNeeded(constants.FT_ELEM, fs.ID)
check_error(rc)
rc = fr.Populate()
check_error(rc)

# 5. Extract X-coordinates at End A and corresponding Moments
feElem = app.feElem
feNode = app.feNode

x_coords = []
moments = []

for row_idx in range(fr.NumberOfRows()):
    rc, elemID, values = fr.GetRow(row_idx)
    check_error(rc)

    # Get element details to locate End A node
    rc = feElem.Get(elemID)
    if rc == constants.FE_OK:
        # Check if the element is a Beam (type 4) or Bar (type 5)
        if feElem.type in [constants.FET_L_BEAM, constants.FET_L_BAR]:
            endA_node_id = feElem.Nodes[0]
            
            # Fetch node coordinates
            rc = feNode.Get(endA_node_id)
            if rc == constants.FE_OK:
                x_coords.append(feNode.x)
                moments.append(values[0])  # values[0] corresponds to column 0 (VEC_PLANE1_MOMENT)

if not x_coords:
    sys.exit("No valid beam elements or moment results found in the selected set.")

# 6. Sort by X-coordinate to generate a continuous curve
sorted_indices = np.argsort(x_coords)
x_sorted = np.array(x_coords)[sorted_indices]
moments_sorted = np.array(moments)[sorted_indices]

# Print status to Femap message pane
app.feAppMessage(0, f"Successfully extracted Plane 1 Moments for {len(x_coords)} beam elements.")

# 6. Sort by X-coordinate
sorted_indices = np.argsort(x_coords)
x_sorted = np.array(x_coords)[sorted_indices]
moments_sorted = np.array(moments)[sorted_indices]

app.feAppMessage(0, f"Successfully extracted Plane 1 Moments for {len(x_coords)} beam elements.")

# 7. Prompt user for target X-coordinates to label
print(f"\nX-coordinate range available: [{x_sorted.min():.3f}, {x_sorted.max():.3f}]")
user_input = input("Enter X-coordinate(s) to label (comma-separated, e.g., '10.5, 25.0'): ").strip()

target_indices = []
if user_input:
    for raw_val in user_input.split(','):
        try:
            target_x = float(raw_val.strip())
            # Find the index of the closest available x-coordinate
            nearest_idx = int(np.abs(x_sorted - target_x).argmin())
            target_indices.append(nearest_idx)
        except ValueError:
            print(f"Skipping invalid input: '{raw_val.strip()}'")

# 8. Plot the Moment Diagram with Datatips
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x_sorted, moments_sorted, marker='o', markersize=4, linestyle='-', color='#1f77b4', linewidth=2, label="Plane 1 End A Moment")
ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)

# Add datatips for unique nearest matches
for idx in set(target_indices):
    pt_x = x_sorted[idx]
    pt_m = moments_sorted[idx]
    
    # Highlight the nearest node point
    ax.scatter(pt_x, pt_m, color='#d62728', s=60, zorder=5)
    
    # Add annotated datatip box
    label_text = f"X: {pt_x:.2f}\nM: {pt_m:.2e}"
    ax.annotate(
        label_text,
        xy=(pt_x, pt_m),
        xytext=(0, 25),
        textcoords="offset points",
        ha='center',
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="#fffae6", ec="#d62728", lw=1.2),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0", color="#d62728", lw=1.2)
    )
ax.set_title(f"Beam Plane 1 End A Moment (Output Set ID: {output_set_id})", fontsize=12, fontweight='bold')
ax.set_xlabel("X Coordinate [Model Units]", fontsize=11)
ax.set_ylabel("Bending Moment Plane 1 [Force × Length]", fontsize=11)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend()
plt.tight_layout()
plt.show()