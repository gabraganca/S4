#=============================================================================
# Modules
import numpy as np
from os import getenv
import matplotlib.pyplot as plt
import re
import lineid_plot
from ..spectools import rvcorr
from ..utils import *
from ..plottools import *
from ..io import fits, wrappers
#=============================================================================



class Synplot:
    """Add docstring"""

    def __init__(self, teff, logg, synplot_path = None, idl = True,
                 **kwargs):
        if synplot_path is None:
            self.path = getenv('HOME')+'/.s4/synthesis/synplot/'
        else:
            self.path = synplot_path

        # Set software to run Synplot.pro
        if idl:
            self.software = 'idl'
        else:
            self.software = 'gdl'

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

        # Check if a observation spectra is available
        if 'observ' in self.parameters:
            if self.parameters['observ'][-4:] == 'fits':
                self.observation = \
                                  fits.load_spectrum(self.parameters['observ'])
            else:
                self.observation = np.loadtxt(self.parameters['observ'])
            #Delete entry to not input in IDL
            del self.parameters['observ']

        #Override IDL plotting
        self.parameters['noplot'] = '1'

        # check for normalization
        if 'relative' not in self.parameters:
            self.parameters['relative'] = 0

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
        """Build the synplot command to IDL/GDL."""

        synplot_command = [key+' = '+str(value)                              \
                           for key, value in self.parameters.iteritems()]

        cmd = "CD, '"+self.path+"' & synplot, "+ \
                        ', '.join(synplot_command)

        return self.software + ' -e "' + cmd + '"'
    #=========================================================================

    #=========================================================================
    # Run synplot and return the computed spectra
    def run(self):
        """Run synplot and store the computed spectra"""

        wrappers.run_command(self.synplot_input(), do_log = True)

        #load synthetized spectra
        self.spectrum = np.loadtxt(self.path + 'fort.11')
    #=========================================================================

    #=========================================================================
    # Plot
    def plot(self, ymin = None, ymax = None, windows = None, save_name = None,
             title = None):
        """
        Plot the synthetic spectra.
        If the synthetic spectra were not calculated, it will calculate.

        Parameters
        ----------

        ymin : lower limit on y-axis
        ymax : upper limit on y-axis
        """

        # Check if spectra were calculated
        #if 'self.spectra' not in globals():
        if not hasattr(self, 'spectrum'):
            self.run()

        # make a copy of array
        spectrum_copy = self.spectrum.copy()
        if hasattr(self, 'observation'):
            observation_copy = self.observation.copy()
            #Apply radial velocity correction if needed.
            if 'rv' in self.parameters:
                observation_copy[:, 0] *= rvcorr(self.parameters['rv'])

        # Apply scale correction needed
        if 'scale' in self.parameters:
            spectrum_copy[:, 1] *= self.parameters['scale']

        # check if figure was already plotted
        if plt.fignum_exists(1):
            fig_exists = True
            plt.clf()
        else:
            fig_exists = False
        # Plot
        fig = plt.figure(num = 1)

        # Identify lines, if required
        if self.line_id is not False:
            ax = fig.add_axes([0.1, 0.1, 0.85, 0.6])
        else:
            ax = fig.gca()
        ax.plot(spectrum_copy[:, 0], spectrum_copy[:, 1],
                label = 'Synthetic')

        # If a observation spectra is available, plot it
        if hasattr(self, 'observation'):
            ax.plot(observation_copy[:, 0], observation_copy[:, 1],
                    label = 'Observation')

        # If windows were set, plot it
        if windows is not None:
            plot.plot_windows(windows)

        # set labels
        plt.xlabel(r'Wavelength $(\AA)$')
        if self.parameters['relative'] != 0:
            if ymin is None:
                ymin = 0
            if ymax is None:
                ymax = 1.05
            plt.ylabel('Normalized Flux')
        else:
            plt.ylabel('Flux')
        # Set size of plot
        plt.xlim([self.parameters['wstart'], self.parameters['wend']])
        if ymin is not None:
            plt.ylim(ymin = ymin)
        if ymax is not None:
            plt.ylim(ymax = ymax)
        ####


        # Identify lines, if required
        if self.line_id is not False:
            # Obtain the spectral line wavelength and identification
            line_wave, line_label = self.lineid_select()
            lineid_plot.plot_line_ids(spectrum_copy[:, 0],
                                      spectrum_copy[:, 1],
                                      line_wave, line_label, label1_size = 10,
                                      extend = False, ax = ax,
                                      box_axes_space = 0.15)

        plt.legend(fancybox = True, loc = 'lower right')

        if title is not None:
            plt.title(title)

        # Plot figure
        if not fig_exists:
            fig.show()
        else:
            fig.canvas.draw()

        # Save file
        if save_name is not None:
            plt.savefig(save_name, dpi = 100)

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

    #=========================================================================
    #Apply scale
    def apply_scale(self):
        """ Apply scale. """
        self.spectrum[:, 1] *= self.parameters['scale']

    #=========================================================================
