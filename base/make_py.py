import sys
import os
from win32com.client import makepy

# Get the directory where this script is located (base folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_dir, "PyFemap.py")

# Locate femap tlb file. Change based on femap installation
tlb_path = "C:\\Program Files\\Siemens\\Femap 2506\\femap.tlb"

# Create the Python wrapper for the Femap type library
sys.argv = ["makepy", "-o", output_path, tlb_path]
makepy.main()