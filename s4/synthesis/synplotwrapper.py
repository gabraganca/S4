#=============================================================================
# Modules
from numpy import loadtxt
from os import getenv
import matplotlib.pyplot as plt
import re
import lineid_plot
from ..idlwrapper import idlwrapper
from ..utils import handling
#=============================================================================



class synplot:
    """Add docstring"""
    
    def __init__(self, teff, logg, synplot_path = None, **kwargs):
        if synplot_path is None:
            self.path = getenv('HOME')+'/.s4/synthesis/synplot/'
        else:
            self.path = synplot_path
            
        # Setting teff and logg on the dictionary
        kwargs['teff'] = teff
        kwargs['logg'] = logg
            
        #Check if some params were defined    
        if 'wstart' not in kwargs.keys():
            kwargs['wstart'] = float(handling.File(self.path + 'fort.19').\
                               head()[0].split()[0]) * 10
            print 'wstart not defined.'
            print 'Setting as {:.2f} Angstrons.\n'.format(kwargs['wstart'])

        if 'wend' not in kwargs.keys():
            kwargs['wend'] = float(handling.File(self.path + 'fort.19').\
                               tail()[0].split()[0]) * 10
            print 'wend not defined.'
            print 'Setting as {:.2f} Angstrons.\n'.format(kwargs['wend'])     
        
        self.parameters = kwargs
        
        #Override IDL plotting
        self.parameters['noplot'] = '1'
        
        # Check if line identification is required
        if 'ident' in self.parameters:
            # Tells Synplot to not identify lines
            self.line_id = self.parameters['ident']
            self.parameters['ident'] = '0'
            
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
        fig = plt.figure()

        # Identify lines, if required
        if self.line_id is not False:
            ax = fig.add_axes([0.1, 0.1, 0.85, 0.6])
        else:
            ax = fig.gca()
        ax.plot(self.spectra[:, 0], self.spectra[:, 1])
        plt.xlabel(r'Wavelength $(\AA)$')
        plt.xlim([self.parameters['wstart'], self.parameters['wend']])
        if 'relative' in self.parameters:
            plt.ylim([0, 1.05])
            plt.ylabel('Normalized Flux')
        else:
            plt.ylabel('Flux')
        
        # Identify lines, if required
        if self.line_id is not False:
            # Obtain the spectral line wavelength and identification
            line_wave, line_label = self.lineid_select()
            lineid_plot.plot_line_ids(self.spectra[:, 0], self.spectra[:, 1],
                                      line_wave, line_label, label1_size = 10,
                                      extend = False, ax = ax,
                                      box_axes_space = 0.15)


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
        ptrn = r'(\d{4}\.\d{3})\s+(\w{1,2}\s+I*V*I*).+(\b\d+\.\d)\s+(\*+)'

        #Find patterns
        regex_table = re.findall(ptrn, table)
 
        # Parse table
        wavelengths = [float(line[0]) for line in regex_table 
                       if float(line[2]) >= self.line_id] 
        chem_elements = [line[1] + ' ' + line[0] + '  ' + line[2]
                         for line in regex_table 
                         if float(line[2]) >= self.line_id]
        
        return wavelengths, chem_elements        
    #=========================================================================
