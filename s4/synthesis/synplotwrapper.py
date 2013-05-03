#=============================================================================
# Modules
from numpy import loadtxt
from os import getenv
import matplotlib.pyplot as plt
import re
import lineid_plot
from ..idlwrapper import idlwrapper
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
        
        #Override IDL plotting
        self.parameters['noplot'] = '1'
        
        # Check if line identification is required
        if 'ident' in self.parameters:
            # Tells Synplot to not identify lines
            self.parameters['ident'] = '0'
            self.line_id = True
        else:
            self.line_id = False

    #=========================================================================
    #     
    def synplot_input(self):
        """Build the synplot command to IDL."""
        
        synplot_command = [key+' = '+str(value)                              \
                           for key, value in self.parameters.iteritems()]      
                
        return "CD, '"+self.path+"' & synplot, "+ \
                        ', '.join(synplot_command)
    #========================================================================= 
    
    #=========================================================================
    # Run synplot and return the computed spectra
    def run(self):
        '''Run synplot and store the computed spectra'''
 
        idlwrapper.run_idl(self.synplot_input(), do_log = True)
    
        #load synthetized spectra
        self.spectra = loadtxt(self.path + 'fort.11')    
    #=========================================================================
    
    #=========================================================================
    # Plot     
    def plot(self):
        """
        Plot the synthetic spectra. 
        If the synthetic spectra were not calculated, it will calculate.
        
        Feature to add:
            - Overplot
        """
        
        # Check if spectra were calculated
        if 'self.spectra' not in globals():
            self.run()
            
        # Plot
        if self.line_id:
            # Obtain the spectral line wavelength and identification
            line_wave, line_label = self.lineid_select()
            #ax = fig.add_axes([0.1, 0.1, 0.85, 0.65])
            #ax.plot(self.spectra[:, 0], self.spectra[:, 1])
            lineid_plot.plot_line_ids(self.spectra[:, 0], self.spectra[:, 1],
                                      line_wave, line_label, label1_size = 10,
                                      extend = False,  
                                      box_axes_space = 0.12)
        else:
            plt.plot(self.spectra[:, 0], self.spectra[:, 1])
        plt.xlabel(r'Wavelength $(\AA)$')
        plt.xlim([self.parameters['wstart'], self.parameters['wend']])
        if 'relative' in self.parameters:
            plt.ylabel('Normalized Flux')
            plt.ylim([0, 1.05])
        else:
            plt.ylabel('Flux')
        
        plt.show(block = False)    
        plt.clf()        
    #=========================================================================
    
    #=========================================================================
    # Select lines to line identification
    def lineid_select(self):
        """Identify lines to be plot by lineid_plot"""
        # List of chemical elements 
        table = open(self.path + 'fort.12').read() +                         \
                open(self.path + 'fort.14').read()
        
        # Pattern for regex
        ptrn  = '(\d{4}\.\d{3})\s+(\\w{1,2}\s+I{1,3}).+(\*+)'   
        
        #Find patterns
        regex_table = re.findall(ptrn, table)
        
        # Parse table
        wavelengths = [float(line[0]) for line in regex_table]
        chem_elements = [line[1] + ' ' + line[0] for line in regex_table]
        
        return wavelengths, chem_elements        
    #=========================================================================
