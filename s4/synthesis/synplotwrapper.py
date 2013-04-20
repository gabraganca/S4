#=============================================================================
# Modules
from numpy import loadtxt
from ..idlwrapper import idlwrapper
from os import getenv
#=============================================================================



class synplot:
    """Add docstring"""
    
    def __init__(self, synplot_path = None, **kwargs):
        if synplot_path is None:
            self.path = getenv('HOME')+'/.s4/synthesis/synplot/'
        else:
            self.path = synplot_path
        
        #Check if some params were defined    
        for par in ['teff', 'logg', 'wstart', 'wend']:
            if par not in kwargs.keys():
                raise ValueError(par + ' were not defined.')    
        
        self.parameters = kwargs

    #=============================================================================
    #     
    def synplot_input(self):
        """Build the synplot command to IDL."""
        
        synplot_command = [key+' = '+str(value)                              \
                           for key, value in self.parameters.iteritems()]      
                
        return "CD, '"+self.path+"' & synplot, "+ \
                        ', '.join(synplot_command)
    #============================================================================= 
    
    #=============================================================================
    # Run synplot and return the computed spectra
    def run(self):
        '''Run synplot and store the computed spectra'''
 
        idlwrapper.run_idl(self.synplot_input(), do_log = True)
    
        #load synthetized spectra
        self.spectra = loadtxt(self.path + 'fort.11')    
    #==============================================================================
