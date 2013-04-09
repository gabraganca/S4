'''
idltools is a module containing several functions to run ITT's IDL.

This is a workaround. The best way would be to translate all idl scripts to 
python.
'''
#=============================================================================
# Modules
from subprocess import Popen, PIPE
from os import getenv
from numpy import loadtxt
#=============================================================================

#=============================================================================
# Global constants
HOME = getenv('HOME')
SYNPLOT_PATH  = HOME +'/synplot/synplot/'
#=============================================================================

#=============================================================================
# Run idl
def run_idl(inp, do_log = False):
    """Run idl"""
    
    if do_log:
        with open('idl.log', 'w') as log:
            idl = Popen(['nice', '-n0', 'idl'], stdin = PIPE, \
                           stdout = log, stderr = log)
            idl.communicate(inp)
                           
    else:
        print '########### IDL ##################'
        idl = Popen(['nice', '-n0', 'idl'], stdin = PIPE)
        idl.communicate(inp)
        print '######## Quitting IDL ############'    
    
    """
    #An alternative way
    
    import pidly
    
    idl = pidly.IDL()
    
    if do_log:        
        with open('idl.log', 'w') as log:
            spam = idl(inp, print_output = False, ret = True)
            log.write(spam)
    else:
        print '########### IDL ##################'
        idl(inp)
        print '######## Quitting IDL ############'
        
    idl.close()    
    
    """
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
    run_idl(synplot_inp, do_log = True)

    #load synthetized spectra
    return loadtxt(SYNPLOT_PATH + '/fort.11')    
#==============================================================================