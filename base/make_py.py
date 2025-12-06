import sys
import os
from win32com.client import makepy

# Get the directory where this script is located (base folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_dir, "PyFemap.py")

# Create the Python wrapper for the Femap type library
sys.argv = ["makepy", "-o", output_path, r"C:\Program Files\Siemens\Femap 2506\femap.tlb"]
makepy.main()