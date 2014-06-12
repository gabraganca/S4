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

def synplot_abund(abund_dic):
    """
    Writes the Chemical abundances values to SYNPLOT format.

    Parameters
    ----------

    abund_dic: dic;
        A dictionary with the key as the chemical element symbol of its atomic
        number and the value is the abundance for that element.E.g., `{2:10.93,
        'N':7.83}` for solar He and N abundances.

    Returns
    -------

    A string with the format used by SYNPLOT. For the example above, it would
    be `'[2, 2, 10.93, 7, 7, 7.83]'`.
    """

    # If the chemical element is identified with its symbol, swap to the
    #atomic number
    for key in abund_dic:
        if key in PERIODIC:
            abund_dic[PERIODIC[key]] = abund_dic.pop(key)

    # Writes a list with each chemical element and its abundance
    elements = ['{0}, {0}, {1:.2f}'.format(key, val)
                for key, val in abund_dic.iteritems()]
    assert len(elements) == len(abund_dic)

    # Put into SYNPLOT format
    synplot_format = '[' + ', '.join(elements)+ ']'

    return synplot_format


def elem_abund(syn_abund, elem):
    """
    Gets the abudnance of a desired chemical element from a string of abundances
    in the SYNPLOT format.

    Parameters
    ----------

    syn_abund: str;
        String of abundances in the SYNPLOT format, i.e.,
        '[8, 8, 8.81, 14, 14, 7.33]'.

    elem: int, str;
        Chemical element. Can be its symbol or its atomic number.

    Returns
    -------

    The abundance of the desired chemical element as a float.
    """

    if type(elem) == int:
        atom_n = str(elem)
    elif type(elem) == str:
        atom_n = str(PERIODIC[elem])
    else:
        raise TypeError('The variable `elem` should be a string or integer.')


    # Gets abundance
    abund = re.findall(atom_n + r',\s?' + atom_n + r',\s?(\d+(?:\.\d+)?)',
                       syn_abund)

    if len(abund) == 0:
        raise IndexError('The element does not have abundance in the input ' +\
                         'value.')
    else:
        return float(abund[0])


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

    if len(args) == 1:
        return list(*args)
    else:
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
        # I use the iter_params variable in order to obtain 'abund'
        # instead of the chemical elements.
        self.fit_keys = self.iter_params.keys()
        # Create the iterator vector.
        self.iter_values = iterator(*[self.iter_params[k]
                                      for k in self.fit_keys])


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


        # Gets chemical elements and their values and transform
        #to Synplot format.
        abund = {}
        for key in self.fit_params:
            if key in PERIODIC.keys():
                abund[key] = self.iter_params[key]
                del self.iter_params[key]

        # Adds it back to the final dictionary
        if len(abund.keys()) == 1:
            elem = abund.keys()[0]
            self.iter_params['abund'] = [synplot_abund({elem:val})
                                         for val in abund[elem]]
        elif len(abund.keys()) > 1:
            self.iter_params['abund'] = [synplot_abund({k:v for k, v
                                                       in zip(abund.keys(),
                                                              itera)})
                                         for itera in iterator(*abund.values())]


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
        # array to store the values of each parameter and the chisquare
        mdtype = []
        for key in self.fit_keys:
            if type(self.iter_params[key][0]) is type(''):
                mdtype.append((key, 'S14'))
            else:
                mdtype.append((key, type(self.iter_params[key][0])))
        mdtype.append(('chisquare', float))

        shape = np.shape(self.iter_values)

        self.chisq_values = np.ones(shape[0], dtype=mdtype)
        ######

        # Loop it!
        for n, it in enumerate(self.iter_values):

            # Creates a dic with the parameters and values to be fitted
            #in this loop
            if n_params == 1:
                # this case correspond when it is fitting only one parameter
                params = {self.fit_keys[0]:it}
            else:
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

            # Set parameters for synplot
            synplot_params = self.syn_params.copy()
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
            if n_params == 1:
                self.chisq_values[self.iter_params.keys()[0]][n] = it
            else:
                for j, value in enumerate(self.iter_params):
                    self.chisq_values[value][n] = it[j]
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

        self.best_fit = {param:fitted_value
                           for param, fitted_value
                           in zip(self.iter_params.keys(), fitted_vals)}
        self.best_fit['chisq'] = fitted_vals[-1]


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
        chisq = best_fit.pop('chisq')

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

                chisq_values['abund'] = [elem_abund(abund, elem)
                                         for abund in chisq_values['abund']]

            chisquare_arr = np.array([list(i)
                                      for i in chisq_values]).astype(float)

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
