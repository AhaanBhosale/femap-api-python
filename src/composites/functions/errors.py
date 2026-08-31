from pyfemap import constants  
import sys

def check_error(rc):

    
    if rc != constants.FE_OK:
        sys.exit("Error code: " + str(rc))