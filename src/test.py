import pythoncom
import pyfemap
import sys

# Try making connection to Femap application
try:
    exist_obj = pythoncom.connect(pyfemap.model.CLSID)
    app = pyfemap.model(exist_obj)
except:
    sys.exit("Femap is not running. Please start Femap and try again.")

# Print success message within femap
app.feAppMessage(0, "Successfully connected to Femap application.")