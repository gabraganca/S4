# -*- coding: utf-8 -*-
"""
Synfit
======

This routine allows the user to automatically fit a spectral line or wavelength
region. Is is allowed any number of parameters.

The best fit is found by minimizing the chi^2. `Synfit` calculates the
synthetic spectrum for all values asked and then select the one with minimum
chi^2 and returns it to the user.

It is also possible to select a subregion of the spectrum by using the
`windows` argument.
"""
import os
import shutil
import re
import json
import shutil
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from ..io import specio
from ..synthesis import Synplot
from ..spectools import rvcorr

# Loads the chemical elements and their atomic numbers
PERIODIC = json.load(open(os.getenv('HOME')+'/.s4/extra_resc'+\
                          '/chemical_elements.json'))

REVERSE_PERIODIC = {val:key for key, val in PERIODIC.iteritems()}

def iterator(fit_keys, iter_params):
    """
    Create an array with the values to iterate.

    Parameters
    ----------

    fit_keys: dict;
        A dictionary containing the name of the parameters,

    fit_params: dict;
        A dictionary containing the parameters as keys and the values to be
        fitted.

    Returns
    -------

    iter_values: numpy.ndarray;
        The values to be fitted as a structured array
    """
    # Create the iterator vector.
    args = [iter_params[k] for k in fit_keys]
    iter_values = list(product(*args))

    ## add the iterrating values to self as a numpy array
    data_type = [(key, float) for key in fit_keys]

    return np.array(iter_values, dtype=data_type)


class Synfit:
    """
    Fit a spectral line by iterating on user defined parameter
    an returns the best fit by minimizing the $\chi^2$ of the
    synthetic spectrum and the observed spectrum.

    Based on the homonym IDL software created by Dr. Ivan
    Hubeny.

    Parameters
    ----------

    fit_params: dic;
        Parameters to be fitted. It should be a dictionary in
        which each key is the setllar parameter of the chemical
        element to be fitted. The values should be list with three
        elements: the initial and findal values and the step.

    kwargs;
        All Synplot parameters desired to be use, including `teff`,
        `logg`, `synplot_path`, `idl`, `noplot`.

        abund: dic (optional);
            Abundance of chosen chemical elements.

            Should be passsed as a dictionary which the keys are the chemical
            element symbol or atomic number i(can be mixed) and the values are
            the abundance, e.g, for Helium and Oxygen abundance of 10.93 and
            8.69, respectively:

            {2:10.93, 'O':8.69}


            ATTENTION: it does not accept the Synplot format.

        windows: list (optional);
            Spectral region in which the chi-sqaure will be calculated. At
            this point, it only accept a single window, i.e., the list should
            contains only two values: the lower and the upper wavelength.
    """

    def __init__(self, fit_params, **kwargs):
        # Parameters to be fitted
        self.fit_params = deepcopy(fit_params)
        # Fixed parameters
        self.syn_params = deepcopy(kwargs)
        ##########

        # Initalizaze varibales.
        self.iter_params = None
        self.fit_keys = None
        self.no_rot_keys = None
        self.rot_keys = None

        # Check for radial velocity
        if 'rv' in self.syn_params:
            self.rad_vel = self.syn_params['rv']
        else:
            self.rad_vel = 0

        # Check if there is a an observed spectrum.
        # If not quit.
        try:
            # If there is, load it to calculate the weights
            obs_spec = specio.load_spectrum(self.syn_params['observ'])
            # Correct for radial velocity
            obs_spec[:,0] *= rvcorr(self.rad_vel)
        except IOError:
            raise IOError('There is not any observed spectrum.')


        #Prepare kwargs
        if 'synplot_path' in self.syn_params:
            self.synplot_path = self.syn_params.pop('synplot_path')
        else:
            self.synplot_path = os.getenv('HOME')+'/.s4/synthesis/synplot/'

        if 'idl' in self.syn_params:
            self.idl = self.syn_params.pop('idl')
        else:
            self.idl = True

        if 'noplot' in self.syn_params and self.syn_params['noplot'] == True:
            self.noplot = True
            del self.syn_params['noplot']
        else:
            self.noplot = False

        if 'windows' in self.syn_params:
            self.weights = np.zeros_like(obs_spec[:, 0])

            for window in np.reshape(self.syn_params['windows'], (-1, 2)):
                index_lower = obs_spec[:, 0] > window[0]
                index_upper = obs_spec[:, 0] < window[1]
                self.weights[index_lower & index_upper] = 1

            self.windows = self.syn_params.pop('windows')
        else:
            self.weights = np.ones_like(obs_spec[:,0])
            self.windows = None

        # Obtain teff and logg if set on syn_params
        if 'teff' in self.syn_params:
            self.teff = self.syn_params.pop('teff')

        if 'logg' in self.syn_params:
            self.logg = self.syn_params.pop('logg')

        # Initialize variable to store the best fit values
        self.best_fit = {}


    def sample_params(self):
        """
        Creates the values to fit for each parameter. It also merge
        the chemical elements to a parameter accepted by `Synplot`.
        """
        def values_to_fit(key, val):
            """
            Creates the values to fit from a three-value list.

            Parameters
            ----------

            key: string
                Parameter to be fitted.

            val: list;
                List with initial value, final value and the step.
            """
            try:
            # Test if the parameters were inserted correctly.
                assert len(val) == 3

                min_value, max_value, step = [float(i) for i in val]

                n_values = np.rint((max_value - min_value)/step + 1)
                vector = np.linspace(min_value, max_value, n_values)

                return vector
            except :
                raise Exception("Value of '{}' must be a ".format(key)+\
                                "list with three values.")


        self.iter_params = {key:values_to_fit(key, val)
                            for key, val in self.fit_params.iteritems()}

        # Get the name of the parameters to be fitted
        self.fit_keys = self.iter_params.keys()

        # Segregate paramates in convolution related and unrelated.
        ## Get the keys convolution unrelated (i.e. not in ['vrot', 'vmac_rt'])
        self.no_rot_keys = [key
                            for key in self.fit_keys
                            if key not in ['vrot', 'vmac_rt']]
        ## Get the keys convolution related (i.e. in ['vrot', 'vmac_rt'])
        self.rot_keys = [key
                         for key in self.fit_keys
                         if key in ['vrot', 'vmac_rt']]



    def fit(self):
        r"""
        Fit a spectral line by iterating on user defined parameter
        an returns the best fit by minimizing the $\chi^2$ of the
        synthetic spectrum and the observed spectrum.

        Based on the homonym IDL software created by Dr. Ivan
        Hubeny.
        """
        # Creates the values in which each parameter will be fitted
        self.sample_params()

        # Create iterator.
        iter_values = iterator(self.fit_keys, self.iter_params)

        #Obtain the number of varying params
        n_params = len(self.fit_keys)

        ######
        # Array to store the values of each parameter and the chisquare

        ## Create an array of NaN
        chisquare = np.empty([len(iter_values), 1])
        chisquare.fill(np.nan)

        ## Create the array with the iteration avlues + NaN for the chisquare

        ### Remove the data type of the iter_values array.
        ### this is necessary in order to add the chisquare array
        #### Removes data type
        tmp_array = iter_values.view((float, n_params))
        #### Guarantee that the format will be correct for any number of
        #### parameters
        tmp_array = tmp_array.reshape(len(iter_values), -1)

        ### Join the arrays
        self.chisq_values = np.hstack((tmp_array, chisquare))

        ### Set the data type for the chisq_values array
        data_type = [(key, float) for key in self.fit_keys]
        data_type.append(('chisquare', float))
        self.chisq_values.dtype = data_type
        ######

        # Create a library of unconvolved spectra
        self.build_library()

        # Loop it!
        for n, it in enumerate(iter_values):
            self.iteration(n, it)

        # Find the best value
        self.find_best_fit()


    def build_library(self):
        """Build spectra library of unconvolved spectra"""
        if len(self.no_rot_keys) > 0 and len(self.rot_keys) > 0:
            # Build library for non rotation parameters with vsini=vmac_rt=0
            no_rot_values = iterator(self.no_rot_keys, self.iter_params)
            for n, it in enumerate(no_rot_values):
                ## Creates a dic with the parameters and values to be fitted
                ## in this loop
                params = {key:val for key, val in zip(it.dtype.names, it)}

                ## Set vsini=vmac_rt=0
                params['vrot'] = 0
                params['vmac_rt'] = 0

                ## Check if teff and logg were selected to be fitted.
                ## If yes, set a variable to them.
                if 'teff' in params:
                    self.teff = params.pop('teff')

                if 'logg' in params:
                    self.logg = params.pop('logg')

                ## Join the abundances

                ### Gets all chemical elements asked to be fit
                abund = {key:it[key]
                         for key in it.dtype.names
                         if (key in PERIODIC) or (key in REVERSE_PERIODIC)}
                if abund:
                    ### delete the chemical elements parameters from the
                    ### dictionary
                    for key in abund:
                        del params[key]

                ## Set parameters for synplot
                synplot_params = deepcopy(self.syn_params)
                synplot_params.update(params)

                ## Deal with fixed and varying abundances
                self.merge_abundances(abund, synplot_params)

                ## Synthesize spectrum
                self.synthesis = Synplot(self.teff, self.logg,
                                         self.synplot_path, self.idl,
                                         **synplot_params)
                self.synthesis.run()

                ## Backup fort.7 and fort.17
                spec_name = '_'.join(['{}_{}'.format(key, val)
                                      for key, val in zip(it.dtype.names, it)])
                shutil.move('{}fort.7'.format(self.synplot_path),
                            '/tmp/synfit_{}.7'.format(spec_name))
                shutil.move('{}fort.17'.format(self.synplot_path),
                            '/tmp/synfit_{}.17'.format(spec_name))

        elif len(self.no_rot_keys) == 0 and len(self.rot_keys) > 0:
            # There is only 'vrot' or/and 'vmac_rt'. All iteration fits will
            # be just convolutions. It creates only one spectrum

            ## Set parameters for synplot
            synplot_params = deepcopy(self.syn_params)

            ## Set values of rotation to 0
            synplot_params['vrot'] = 0
            synplot_params['vmac_rt'] = 0

            ## Synthesize spectrum
            synthesis = Synplot(self.teff, self.logg, self.synplot_path,
                                self.idl, **synplot_params)
            synthesis.run()

            ## Backup fort.7 and fort.17
            shutil.move('{}fort.7'.format(self.synplot_path),
                        '/tmp/synfit.7')
            shutil.move('{}fort.17'.format(self.synplot_path),
                        '/tmp/synfit.17')

        elif len(self.no_rot_keys) > 0 and len(self.rot_keys) == 0:
            # No rotational parameters
            # Do not build library.
            # There is no need since Synspec will have to run every time.
            pass
        else:
            # There is no parameters. Something wen wrong?
            raise RuntimeError("There is no parameters or it was not " + \
                               "classified as rotational or non rotational. " +\
                               "It seems that something went wrong.")


    def iteration(self, n, it):
        """Code to be iterated on a loop."""

        # Creates a dic with the parameters and values to be fitted
        #in this loop
        params = {key:val for key, val in zip(it.dtype.names, it)}


        #make plot title before removing teff and logg
        if self.noplot == False:
            plot_title = ', '.join(['{}={}'.format(key, val)
                                    for key, val in params.iteritems()])

        # Check if teff and logg were selected to be fitted.
        # If yes, set a variable to them.
        if 'teff' in params:
            self.teff = params.pop('teff')

        if 'logg' in params:
            self.logg = params.pop('logg')

        # Join the abundances

        ## Gets all chemical elements asked to be fit
        abund = {key:it[key]
                 for key in it.dtype.names
                 if (key in PERIODIC) or (key in REVERSE_PERIODIC)}
        if abund:
            ## delete the chemical elements parameters from the dictionary
            for key in abund:
                del params[key]

        # Set parameters for synplot
        synplot_params = deepcopy(self.syn_params)
        synplot_params.update(params)

        # Deal with fixed and varying abundances
        self.merge_abundances(abund, synplot_params)


        # Copy not convolved spectrum to Synplot folder
        if len(self.no_rot_keys) > 0 and len(self.rot_keys) > 0:
            # Set to not calculate spectrum, just convolve
            ## I tried to set the parameter 'ispec' to -1 but it didn't work.
            ## So it will use the parameter 'norun'.
            synplot_params['norun'] = 1

            ## There are rotational and non rotational parameters
            spec_name = '_'.join(['{}_{}'.format(key, val)
                                  for key, val in zip(it.dtype.names, it)
                                  if key not in ['vrot', 'vmac_rt']])
            shutil.copy('/tmp/synfit_{}.7'.format(spec_name),
                        '{}fort.7'.format(self.synplot_path))
            shutil.copy('/tmp/synfit_{}.17'.format(spec_name),
                        '{}fort.17'.format(self.synplot_path))

        elif len(self.no_rot_keys) == 0 and len(self.rot_keys) > 0:
            # Set to not calculate spectrum, just convolve
            ## I tried to set the parameter 'ispec' to -1 but it didn't work.
            ## So it will use the parameter 'norun'.
            synplot_params['norun'] = 1

            ## There is only 'vrot' or/and 'vmac_rt'.
            shutil.copy('/tmp/synfit.7',
                        '{}fort.7'.format(self.synplot_path))
            shutil.copy('/tmp/synfit.17',
                        '{}fort.17'.format(self.synplot_path))
        elif len(self.no_rot_keys) > 0 and len(self.rot_keys) == 0:
            # No rotational parameters
            pass
        else:
            # There is no parameters. Something wen wrong?
            raise RuntimeError("There is no parameters or it was not " + \
                               "classified as rotational or non rotational. " +\
                               "It seems that something went wrong.")


        # Synthesize spectrum
        self.synthesis = Synplot(self.teff, self.logg, self.synplot_path,
                                 self.idl, **synplot_params)
        self.synthesis.run()

        # Apply scale and radial velocity if needed
        if 'scale' in self.synthesis.parameters:
            self.synthesis.apply_scale()

        self.synthesis.observation[:, 0] *= rvcorr(self.rad_vel)

        #Do an interpolation

        flm = np.interp(self.synthesis.observation[:,0],
                        self.synthesis.spectrum[:,0],
                        self.synthesis.spectrum[:,1])
                        #/max(syn.observation[:,1])

        #Some kind of normalization on the observed flux?
        fobm = self.synthesis.observation[:,1]#/max(syn.observation[:,1])

        # Calculate the chi**2
        chisq = np.sum(((fobm - flm)**2/flm) * self.weights)
        #chisq = chisq * max(fobs)                 #????

        # store the values of the parameters
        self.chisq_values['chisquare'][n] = chisq

        # Plot, if desired
        if self.noplot == False:
            # The synthetic spectrum was corrected by scale and the
            #observed one by radial velocity. The plot function in Synplot
            #also does that, so we need to set those parameters to 1 and 0,
            # respectively.
            self.synthesis.parameters['scale'] = 1
            self.synthesis.parameters['rv'] = 0

            # Adds the value of chisquare to the title
            plot_title += r'$\chi^2$='+'{:.06f}'.format(chisq)
            self.synthesis.plot(title=plot_title, windows=self.windows)


    @staticmethod
    def merge_abundances(abund, synplot_params):
        """
        Merge varying and fixed parameters. It change the `abund` and
        `synplot_params` in place.
        """
        # The abundance should be merged individually because it could be
        # a mix of fixed and varying abundances.
        if abund and 'abund' in synplot_params:
            ## Check for overlapping elements.
            ### Transform all elements to its symbol
            for key, val in deepcopy(abund).iteritems():
                try:
                    abund[REVERSE_PERIODIC[key]] = val
                    del abund[key]
                except KeyError:
                    #### The chemical element is already as a symbol
                    pass

            for key, val in deepcopy(synplot_params['abund']).iteritems():
                try:
                    synplot_params['abund'][REVERSE_PERIODIC[key]] = val
                    del synplot_params['abund'][key]
                except KeyError:
                    #### The chemical element is already as a symbol
                    pass

            ## Get the fixed abundances
            try:
                abund.update({k:v
                              for k, v in synplot_params['abund'].iteritems()
                              if k not in deepcopy(abund)})
            except ValueError:
                # There no fixed abundance
                pass

            ## Adds to the synplot_params dictionary
            synplot_params['abund'] = abund
        if abund and 'abund' not in synplot_params:
            synplot_params['abund'] = abund


    def find_best_fit(self):
        """
        Obtain the fitted parameters for the chosen parameters and the
        value of the chi^2.
        """
        fitted_vals = self.chisq_values[np.argmin(
                                        self.chisq_values['chisquare'])]

        self.best_fit = {param:fitted_value
                           for param, fitted_value
                           in zip(self.iter_params.keys(),
                                  fitted_vals.view(float))}
        self.best_fit['chisquare'] = fitted_vals['chisquare'][0]


    def plot_best_fit(self, title=None):
        """
        Plot the observed spectrum and the synthetic using the best values
        found.

        Parameters
        ----------

        title: str (optional);
            A title for the plot. If the string 'default' is passed, it will
            contain the parameters fitted with the best values found.
        """

        # Set parameters for synplot
        synplot_params = deepcopy(self.syn_params)
        best_fit = deepcopy(self.best_fit)
        chisq = best_fit.pop('chisquare')

        #make plot title before removing teff and logg
        if title == 'default':
            title = r'$\chi^2$=' + '{:.4f}: '.format(chisq)
            title += ', '.join(['{}={}'.format(key, val)
                                    for key, val in best_fit.iteritems()])

        ## Replace parameters for best value
        if 'teff' in best_fit:
            self.teff = best_fit.pop('teff')

        if 'logg' in best_fit:
            self.logg = best_fit.pop('logg')


        # Join the abundances

        ## Gets all chemical elements asked to be fit
        abund = {key:val
                 for key, val in self.best_fit.iteritems()
                 if (key in PERIODIC) or (key in REVERSE_PERIODIC)}
        if abund:
            for key in abund:
                del best_fit[key]

        # Deal with fixed and varying abundances
        self.merge_abundances(abund, synplot_params)

        # Add the best values found to the Synplot parameters
        for key, value in best_fit.iteritems():
            synplot_params[key] = value


        # Synthesize spectrum
        synthesis = Synplot(self.teff, self.logg, self.synplot_path,
                            self.idl, **synplot_params)
        synthesis.plot(title=title, windows=self.windows)


    def plot_chisquare(self, interpolation='linear', logscale=False, **kwargs):
        """
        Plot the distribution of chi-square for one given parameter.
        It obly works if the number of parameters to be fitted are one or two.

        Parameters
        ----------

        interpolation: str (optional);
            Type of interpolation for the color plot when fitting two
            parameters. One of ['nearest', 'linear', 'cubic']. More explanation
            here:

            http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html

        scale: boolean (optional):
            If set to True, it will plot the logarithmic of the chi-square.

        kwargs;
            Matplotlib.pyplot.plot kwargs.
        """
        # Number of parameters fitted.
        number_params = len(self.fit_keys)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        if number_params == 1:
            if logscale:
                y_axis = np.log(self.chisq_values['chisquare'])
            else:
                y_axis = self.chisq_values['chisquare']

            ax.plot(self.iter_params[self.fit_keys[0]],
                    y_axis, **kwargs)

            ax.set_xlabel(self.fit_keys[0])
            ax.set_ylabel(r'$\chi^2$')
        elif number_params == 2:
            from scipy.interpolate import griddata

            # Transform the chisquare array in a proper array
            #and not an array of tuples
            chisq_values = deepcopy(self.chisq_values)

            ## Check for abundance
            if 'abund' in self.chisq_values.dtype.names:
                elem = [param for param in self.fit_params.keys()
                        if param in PERIODIC][0]

                chisq_values['abund'] = [abund
                                         for abund in chisq_values['abund']]

            ## Removes data type
            chisquare_arr = chisq_values.view((float, 3))
            ## Guarantee that the format will be correct for any number of
            ## parameters
            chisquare_arr = chisquare_arr.reshape(len(chisq_values), -1)

            edges = np.hstack([(min(param_vector), max(param_vector))
                               for param_vector in chisquare_arr.T[:-1]])

            # Points in wich the grid will be calculated
            grid_points = [np.linspace(edges[i], edges[i+1], 200)
                           for i in np.arange(0, 2*number_params, 2)]

            # Makes a mesh grid to griddata
            grid_params = np.meshgrid(*grid_points)
            grid_params = tuple([i for i in grid_params])

            # Grid the data
            Z = griddata(chisquare_arr[:,:number_params], chisquare_arr[:,-1],
                         grid_params, method=interpolation)

            if logscale:
                # Get the log to increase the contrast between limits
                from matplotlib.colors import LogNorm
                kwargs['norm'] = LogNorm()


            # Plot
            cax = ax.imshow(Z, aspect='auto', extent=edges,
                            origin='lower', **kwargs)

            # Set labels
            ax.set_xlabel(self.fit_keys[0])
            ax.set_ylabel(self.fit_keys[1])

            # Add colorbar
            cbar = fig.colorbar(cax)
            cbar.ax.set_ylabel(r'$\chi^2$')

        else:
            raise ValueError('The number of parameters is greater than 2.')
