"""
Parameters
---------

abund: str, dic (optional);
    Chemical abundance. It overrides the values set by Synspec.
    It can be set as the Synplot format, e.g., '[2, 2, 10.93'] or as a
    dictionary, e.g., {2:10.93}. As a dictionary, it also accepts the chemical
    element symbol, i.e., {'He':10.93}.
"""
#=============================================================================
# Modules
import shutil
import numpy as np
import os
import matplotlib.pyplot as plt
import re
from ..spectools import rvcorr
from ..utils import File
from ..plottools import plot_windows, plot_line_ids
from ..io import specio, wrappers
from synplot_abund import Synplot_abund
#=============================================================================



class Synplot:
    """Add docstring"""

    def __init__(self, teff, logg, synplot_path = None, idl = False,
                 **kwargs):
        if synplot_path is None:
            self.spath = os.getenv('HOME')+'/.s4/synthesis/synplot/'
        else:
            self.spath = synplot_path

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
            kwargs['wstart'] = float(File(self.spath + 'fort.19').\
                               head()[0].split()[0]) * 10
            print 'wstart not defined.'
            print 'Setting as {:.2f} Angstrons.\n'.format(kwargs['wstart'])

        if 'wend' not in kwargs.keys():
            kwargs['wend'] = float(File(self.spath + 'fort.19').\
                               tail()[0].split()[0]) * 10
            print 'wend not defined.'
            print 'Setting as {:.2f} Angstrons.\n'.format(kwargs['wend'])

        self.parameters = kwargs

        # Check if a observation spectrum is available
        if 'observ' in self.parameters:
            self.observation = specio.load_spectrum(self.parameters['observ'])
            #Delete entry to not input in IDL
            del self.parameters['observ']

        #Override IDL plotting
        self.parameters['noplot'] = '1'

        # check for normalization
        if 'relative' not in self.parameters:
            self.parameters['relative'] = 0

        # Check for line list
        if 'linlist' in self.parameters:
            abspath = os.path.abspath(self.parameters['linlist'])
            if os.path.isfile(abspath):
                self.parameters['linlist'] = r"'{}'".format(abspath)
            else:
                raise IOError("File '{}' does not exist.".format(abspath))

        # Initizalize variable 'spectrum'
        self.spectrum = None


    #=========================================================================
    #
    def synplot_input(self):
        """Build the synplot command to IDL/GDL."""

        # Copy the parameters
        parameters_copy = self.parameters.copy()
        if 'abund' in parameters_copy:
            abund = Synplot_abund(parameters_copy['abund'])
            parameters_copy['abund'] = abund.to_synplot()

        synplot_command = [key+' = '+str(value)                              \
                           for key, value in parameters_copy.iteritems()]

        cmd = "CD, '"+self.spath+"' & synplot, "+ \
                        ', '.join(synplot_command)

        return self.software + ' -e "' + cmd + '"'
    #=========================================================================

    #=========================================================================
    # Run synplot and return the computed spectra
    def run(self):
        """Run synplot and store the computed spectra"""

        # remove old calculated spectrum
        # Stack Overflow #10840533
        try:
            os.remove((self.spath + 'fort.11'))
        except OSError:
            pass


        # Synplot erases the fort.19 (line list) if parameter `linlist` has
        # been set.
        # Thus, we will need to do a backup of the original and restore it
        # after.

        if 'linlist' in self.parameters:
            ## Make a backup of the original line list
            shutil.copyfile(self.spath + '/fort.19', '/tmp/fort.19')


        wrappers.run_command(self.synplot_input(), do_log = True)

        if 'linlist' in self.parameters:
            ## Make a backup of the original line list
            shutil.copyfile('/tmp/fort.19', self.spath + '/fort.19')

        #load synthetized spectra
        try:
            self.spectrum = specio.loadtxt_fast(self.spath + 'fort.11',
                                                np.float)
        except IOError:
            raise IOError('Calculated spectrum is not available. Check if ' +
                'syn(spec|plot) ran correctly.')

    def save_spec(self, file_name, **kwargs):
        """
        Save spectrum fo a file.

        Parameters
        ----------

        file_name: str;
            Name of the file to be saved.

        kwargs:
            Numpy.savetxt arguments.
        """

        self.check_if_run()

        np.savetxt(file_name, self.spectrum, **kwargs)

    # Plot
    def plot(self, ymin = None, ymax = None, windows = None, file_name = None,
             title = None, ident = False):
        """
        Plot the synthetic spectra.
        If the synthetic spectra were not calculated, it will calculate.

        Parameters
        ----------

        ymin : lower limit on y-axis
        ymax : upper limit on y-axis

        file_name: str;
            Name of the file to be saved.
        """

        self.check_if_run()

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

        # Set ax
        ## If identification of the lines is required, set different size to ax
        if ident:
            ax = fig.add_axes([0.1, 0.1, 0.85, 0.55])
        else:
            ax = fig.gca()

        # If a observation spectra is available, plot it
        if hasattr(self, 'observation'):
            ax.plot(observation_copy[:, 0], observation_copy[:, 1], c='#377eb8',
                    label = 'Observation')

        # Plot synthetuc spectrum
        ax.plot(spectrum_copy[:, 0], spectrum_copy[:, 1], c='#e41a1c',
                label = 'Synthetic')

        # If windows were set, plot it
        if windows is not None:
            plot_windows(windows)

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
        if ident:
            # Obtain the spectral line wavelength and identification
            line_wave, line_label = self.lineid_select(ident)
            _, _ = plot_line_ids(spectrum_copy[:, 0], spectrum_copy[:, 1],
                                 line_wave, line_label, label1_size = 8,
                                 ax = ax, box_axes_space=0.2)

        # Adds a legend
        ## A small workaround to no plot the line identification labels
        if hasattr(self, 'observation'):
            n_legend = 2
        else:
            n_legend = 1

        handles, labels = ax.get_legend_handles_labels()

        ax.legend(handles[:n_legend], labels[:n_legend],
                  fancybox = True, loc = 'lower right')

        if title is not None:
            plt.title(title, verticalalignment = 'baseline')

        # Plot figure
        if not fig_exists:
            fig.show()
        else:
            fig.canvas.draw()

        # Save file
        if file_name is not None:
            plt.savefig(file_name, dpi = 100)

    #=========================================================================

    #=========================================================================
    # Select lines to line identification
    def lineid_select(self, ident):
        """Identify lines to be plot by lineid_plot"""
        # List of chemical elements
        table = open(self.spath + 'fort.12').read() +                         \
                open(self.spath + 'fort.14').read()

        # Pattern for regex
        ptrn = r'(\d{4}\.\d{3})\s+(\w{1,2}\s+I*V*I*).+(\b\d+\.\d)\s+(\*+)'

        #Find patterns
        regex_table = re.findall(ptrn, table)

        # Parse table
        wavelengths = [float(line[0]) for line in regex_table
                       if float(line[2]) >= ident]
        chem_elements = [line[1] + ' ' + line[0] + '  ' + line[2]
                         for line in regex_table
                         if float(line[2]) >= ident]

        return wavelengths, chem_elements
    #=========================================================================

    #=========================================================================
    #Apply scale
    def apply_scale(self):
        """ Apply scale. """
        self.spectrum[:, 1] *= self.parameters['scale']


    def check_if_run(self):
        """
        Check if spectrum was already calculated. If not, calculate it.
        """

        if isinstance(self.spectrum, type(None)):
            self.run()
