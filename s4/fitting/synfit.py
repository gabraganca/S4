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
import re
import json
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from ..io import specio
from ..synthesis import Synplot
from ..spectools import rvcorr

# Loads the chemical elements and their atomic numbers
PERIODIC = json.load(open(os.path.dirname(__file__)+\
                          '/chemical_elements.json'))

def iterator(*args):
    """
    Create the iterator vector.

    Parameters
    ----------

    args: list;
        One or more lists or arrays.

    Returns
    -------

    If there is only one argument, this is returned.
    If there is two or more, it returns the internal
    product of these lists.
    """

#    if len(args) == 1:
#        return list(*args)
#    else:
#        return list(product(*args))
    return list(product(*args))


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
        self.fit_params = fit_params.copy()
        # Fixed parameters
        self.syn_params = kwargs.copy()
        ##########

        # Creates the values in which each parameter will be fitted
        self.iter_params = {}
        self.sample_params()

        # Get the name of the parameters to be fitted
        self.fit_keys = self.iter_params.keys()

        # Create the iterator vector.
        iter_values = iterator(*[self.iter_params[k] for k in self.fit_keys])

        ## add the iterrating values to self as a numpy array
        data_type = [(key, float) for key in self.fit_keys]
        self.iter_values = np.array(iter_values, dtype=data_type)

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
            self.synplot_path = None

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
            assert len(self.syn_params['windows']) == 2
            index_lower = obs_spec[:,0] > self.syn_params['windows'][0]
            index_upper = obs_spec[:,0] < self.syn_params['windows'][1]
            compound_index = index_lower & index_upper

            self.weights = np.where(compound_index, np.ones_like(obs_spec[:,0]),
                               np.zeros_like(obs_spec[:,0]))

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

        #Test if the parameter were given properly.
        for key in self.fit_params:
            # Test if the parameters were inserted correctly.
            try:
                assert len(self.fit_params[key]) == 3

                min_value = float(self.fit_params[key][0])
                max_value = float(self.fit_params[key][1])

                step = float(self.fit_params[key][2])
                n_values = np.rint((max_value - min_value)/step + 1)
                vector = np.linspace(min_value, max_value, n_values)

                self.iter_params[key] = vector
            except:
                raise Exception("Value of '{}' must be a list ".format(key)+\
                                "with three values.")


#        # Gets all chemical elements asked to be fit
#        abund = {key:val
#                 for key, val in self.iter_params.iteritems()
#                 if key in PERIODIC}
#        for key in abund:
#            del self.iter_params[key]
#
#        # Adds it back to the final dictionary
#        if len(abund.keys()) == 1:
#            elem = abund.keys()[0]
#            self.iter_params['abund'] = {elem:abund[elem]}
#        elif len(abund.keys()) > 1:
#            self.iter_params['abund'] = [{k:v for k, v
#                                          in zip(abund.keys(), itera)}
#                                         for itera in iterator(*abund.values())]
#
#        # Adds fixed abundances if defined by user
#        if ('abund' in self.syn_params) and ('abund' in self.iter_params):
#            tmp = self.syn_params['abund'][1:]
#            self.iter_params['abund'] = [it_abund[:-1] + ', ' + tmp
#                                         for it_abund in
#                                         self.iter_params['abund']]
#            del self.syn_params['abund']


    def fit(self):
        r"""
        Fit a spectral line by iterating on user defined parameter
        an returns the best fit by minimizing the $\chi^2$ of the
        synthetic spectrum and the observed spectrum.

        Based on the homonym IDL software created by Dr. Ivan
        Hubeny.
        """

        #Obtain the number of varying params
        n_params = len(self.fit_keys)

        ######
        # Array to store the values of each parameter and the chisquare

        ## Create an array of NaN
        chisquare = np.empty([len(self.iter_values), 1])
        chisquare.fill(np.nan)

        ## Create the array with the iteration avlues + NaN for the chisquare

        ### Remove the data type of the iter_values array.
        ### this is necessary in order to add the chisquare array
        #### Removes data type
        tmp_array = self.iter_values.view((float, n_params))
        #### Guarantee that the format will be correct for any number of
        #### parameters
        tmp_array = tmp_array.reshape(len(self.iter_values), -1)

        ### Join the arrays
        self.chisq_values = np.hstack((tmp_array, chisquare))

        ### Set the data type for the chisq_values array
        data_type = [(key, float) for key in self.fit_keys]
        data_type.append(('chisquare', float))
        self.chisq_values.dtype = data_type
        ######

        # Loop it!
        for n, it in enumerate(self.iter_values):

            # Creates a dic with the parameters and values to be fitted
            #in this loop
#            if n_params == 1:
#                # this case correspond when it is fitting only one parameter
#                single_param = self.fit_keys[0]
#                params = {single_param:it[single_param]}
#            else:
#                params = {key:val for key, val in zip(self.fit_keys, it)}
            params = {key:val for key, val in zip(self.fit_keys, it)}


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
                     if key in PERIODIC}
            if abund:
                ## delete the chemical elements parameters from the dictionary
                for key in abund:
                    del params[key]

            # Set parameters for synplot
            synplot_params = self.syn_params.copy()
            ## The abundance should be merged individually because it could be
            ## a mix of fixed and varying abundances.
            if abund and 'abund' in synplot_params:
                synplot_params['abund'].update(abund)
            if abund and 'abund' not in synplot_params:
                params['abund'] = abund

            synplot_params.update(params)

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
#            if n_params == 1:
#                self.chisq_values[self.iter_params.keys()[0]][n] = it
#            else:
#                for j, value in enumerate(self.iter_params):
#                    self.chisq_values[value][n] = it[j]
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


        # Find the best value
        self.find_best_fit()


    def find_best_fit(self):
        """
        Obtain the fitted parameters for the chosen parameters and the
        value of the chi^2.
        """
        fitted_vals = self.chisq_values[np.argmin(
                                        self.chisq_values['chisquare'])]
        #best_fit = list(fitted_vals[0])

        self.best_fit = {param:fitted_value[param]
                           for param, fitted_value
                           in zip(self.iter_params.keys(), fitted_vals)}
        self.best_fit['chisquare'] = fitted_vals['chisquare'][0]


    def best_plot(self, title=None):
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
        synplot_params = self.syn_params.copy()
        best_fit = self.best_fit.copy()
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
                 if key in PERIODIC}
        if abund:
            for key in abund:
                del best_fit[key]

        ## The abundance should be merged individually because it could be
        ## a mix of fixed and varying abundances.
        if abund and 'abund' in synplot_params:
            synplot_params['abund'].update(abund)
        if abund and 'abund' not in synplot_params:
            synplot_params['abund'] = abund

        # Add the best values found to the Synplot parameters
        for key, value in best_fit.iteritems():
            synplot_params[key] = value


        # Synthesize spectrum
        synthesis = Synplot(self.teff, self.logg, self.synplot_path,
                            self.idl, **synplot_params)
        synthesis.plot(title=title, windows=self.windows)


    def plot_chisquare(self, interpolation='linear', log=False, **kwargs):
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
            ax.plot(self.iter_params[self.fit_keys[0]],
                    self.chisq_values['chisquare'], **kwargs)

            ax.set_xlabel(self.fit_keys[0])
            ax.set_ylabel(r'$\chi^2$')
        elif number_params == 2:
            from scipy.interpolate import griddata

            # Transform the chisquare array in a proper array
            #and not an array of tuples
            chisq_values = self.chisq_values.copy()

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

            if log:
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
