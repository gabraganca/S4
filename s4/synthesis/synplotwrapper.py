#=============================================================================
# Modules
from numpy import loadtxt
from ..idlwrapper import idlwrapper
from os import getenv
#=============================================================================

#=============================================================================
# Global constants
SYNPLOT_PATH  = getenv('HOME')+'/.s4/synthesis/synplot/'
#=============================================================================

#=============================================================================
# Change synplot path
def change_spath(new_path):
    """Change synplot path"""
    global SYNPLOT_PATH
    SYNPLOT_PATH = new_path
#=============================================================================

#=============================================================================
#     
def synplot_input(**kwargs):
    """Build the synplot command to IDL.
    
    It also checks if Teff, logg, wstart and wend were defined.
    
    """
    #Check if some params were defined
    for par in ['teff', 'logg', 'wstart', 'wend']:
        if par not in kwargs.keys():
            raise ValueError(par + ' were not defined.')
            
    return "CD, '"+SYNPLOT_PATH+"' & synplot, "+ \
       ', '.join([key+' = '+str(value) for key, value in kwargs.iteritems()])
#============================================================================= 

#=============================================================================
# Run synplot and return the computed spectra
def run_load(synplot_inp):
    '''Run synplot and return the computed spectra'''
    
    #Run Synplot
    idlwrapper.run_idl(synplot_inp, do_log = True)

    #load synthetized spectra
    return loadtxt(SYNPLOT_PATH + 'fort.11')    
#==============================================================================
