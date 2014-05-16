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
import json
import numpy as np
from itertools import product
from ..io import specio
from ..synthesis import Synplot
from ..spectools import rvcorr

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
    periodic = json.load(open(os.path.dirname(__file__)+\
                              '/chemical_elements.json'))

    for key in abund_dic:
        if key in periodic:
            abund_dic[periodic[key]] = abund_dic.pop(key)

    # Writes a list with each chemical element and its abundance
    elements = ['{0}, {0}, {1:.2f}'.format(key, val)
                for key, val in abund_dic.iteritems()]
    assert len(elements) == len(abund_dic)

    # Put into SYNPLOT format
    synplot_format = '[' + ', '.join(elements)+ ']'

    return synplot_format


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

    syn_params: dic;
        All Synplot parameters desired to be use, including `teff`,
        `logg`, `synplot_path`, `idl`, `noplot`.

    """

    def __init__(self, fit_params, syn_params):
        # Parameters to be fitted
        self.fit_params = fit_params.copy()
        # Fixed parameters
        self.syn_params = syn_params.copy()
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
        if 'observ' not in self.syn_params:
            raise IOError('There is not any observed spectrum.')
        else:
            # If there is, load it to calculate the weights
            obs_spec = specio.load_spectrum(self.syn_params['observ'])
            # Correct for radial velocity
            obs_spec[:,0] *= rvcorr(self.rad_vel)

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

        for key in self.fit_params:
            assert len(self.fit_params[key]) == 3

            min_value = float(self.fit_params[key][0])
            max_value = float(self.fit_params[key][1])

            step = float(self.fit_params[key][2])
            n_values = np.rint((max_value - min_value)/step + 1)
            vector = np.linspace(min_value, max_value, n_values)

            self.iter_params[key] = vector

        # Loads the chemical elements and their atomic numbers
        periodic = json.load(open(os.path.dirname(__file__)+\
                                  '/chemical_elements.json'))

        # Gets chemical elements and their values and transform
        #to Synplot format.
        abund = {}
        for key in self.fit_params:
            if key in periodic.keys():
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

        self.chisq_values = np.ones([shape[0], 1], dtype=mdtype)
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

            if self.noplot == False:
                self.synthesis.plot(title=plot_title, windows=self.windows)

            # Apply scale and radial velocity if needed
            if 'scale' in self.synthesis.parameters:
                self.synthesis.apply_scale()

            if 'rv' in self.synthesis.parameters:
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

        # Find the best value
        self.find_best_fit()


    def find_best_fit(self):
        """
        Obtain the fitted parameters for the chosen parameters and the
        value of the chi^2.
        """
        fitted_vals = self.chisq_values[np.argmin(
                                        self.chisq_values['chisquare'])]
        best_fit = list(fitted_vals[0])

        self.best_fit = {param:fitted_value
                           for param, fitted_value
                           in zip(self.iter_params.keys(), best_fit[:-1])}
        self.best_fit['chisq'] = fitted_vals[0][-1]


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
