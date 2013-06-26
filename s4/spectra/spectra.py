"""
Tools to handle spectra.
"""

#=============================================================================
# Modules
import numpy as np
from scipy.constants import c
#=============================================================================

#=============================================================================
# Function that corrects for radial velocity, putting the shifted spectrum 
# at rest reference
def rvcorr(rad_vel):
    '''rvcorr(float) -> float\n
    Correction for radial velocity.\n
    When wavelength array is multiplied by RVCORR, the array is dislocated
    to the standard rest frame.
    '''  
    
    return 1-rad_vel/(c/1000)
    #return 1+rad_vel/(c/1000)
#=============================================================================  
 
#=============================================================================
# Obtain the position of the line center
def line_position(spec, line_center, res = 0.1, mode = 'absorption'):
    """Obtain the poition of the line center"""
    
    lista = []
    for i in range(len(spec)):
        if spec[i, 0] > line_center and \
           spec[i, 0] < line_center + res:
            lista.append(i)
    spec2 = spec[lista[0]:lista[-1]]
    #Now obtains the line_center and its flux
    if mode.lower() == 'absorption':
        line_pos = spec2[np.argsort(spec2[:, 1])[0]]
    elif mode.lower() == 'emission':
        line_pos = spec2[np.argsort(spec2[:, 1])[-1]]
        
    return line_pos
#=============================================================================

#=============================================================================
# Subselect the observed array to fit [min_wl,max_wl]            
def subselect_spectra(spec, min_wl, max_wl, rad_vel = 0):
    """Subselect the observed array to fit [min_wl,max_wl]"""

    #Argument in which min_wl is located ...
    wstart_arg = np.where(spec[:, 0]>=min_wl)[0][0]  
     #...and the one which max_wl is.        
    wend_arg = np.where(spec[:, 0]<=max_wl)[0][-1]   
    cut_spec = np.array([spec[wstart_arg:wend_arg+1, 0]*rvcorr(rad_vel), \
                 spec[wstart_arg:wend_arg+1, 1]])
                 
    return cut_spec
#=============================================================================

#==============================================================================
# Obtain FWHM of a spectral line
def get_fwhm(spec, line_center):
    """Obtain FWHM of a spectral line"""
    
    size = 20                                     #Maximum size of half wing
    
    line_pos = line_position(spec, line_center)   #get line_center coords
    res = spec[1, 0] - spec[0, 0]                 #get resolution
    arg = list(spec[:, 0]).index(line_pos[0])     #get argument of line center
    half_max = 1 - (1  -line_pos[1])/2            #get half maximum flux
    
    left_values = []
    right_values = []
    for i in range(arg-int(size/res), arg):
        if spec[i, 1] > half_max - 0.005 and spec[i, 1] < half_max + 0.005:
            left_values.append(spec[i, 0])
    for i in range(arg, arg+int(size/res)):
        if spec[i, 1] > half_max - 0.005 and spec[i, 1] < half_max + 0.005:
            right_values.append(spec[i, 0])
    
    return (np.mean(right_values) - np.mean(left_values)) 
#==============================================================================