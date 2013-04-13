'''
idltools is a module containing several functions to run ITT's IDL.

This is a workaround. The best way would be to translate all idl scripts to 
python.
'''
#=============================================================================
# Modules
from subprocess import Popen, PIPE
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
