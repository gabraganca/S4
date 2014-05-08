"""
Test suite for Synfit and complementary functions.
"""

import os
import numpy as np
import s4
from s4.synthesis import Synplot
from s4.fitting import Synfit
from s4.fitting.synfit import iterator
from s4.fitting.synfit import synplot_abund


def test_synplot_abund():
    """Test the `synplot_abund` function."""

    assert synplot_abund({'Si':7.5}) == '[14, 14, 7.50]'
    assert synplot_abund({'Si':7.5, 'O':8.5}) == '[8, 8, 8.50, 14, 14, 7.50]'


def test_iterator():
    """Test the iterator function."""

    # One argument
    itera = iterator(np.arange(0, 10, 2))

    assert np.all([i == j for i, j in zip(itera, np.arange(0, 10, 2))])

    # Two arguments
    itera = iterator(np.arange(0, 10, 5), np.arange(20, 15, -3))

    assert np.all([i == j for i, j in zip(itera, [(0, 20), (0, 17), (5, 20),
                                                  (5, 17)])])


def test_synfit_one():
    """Test synfit with one parameter against a synthetic spectrum."""

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.savetxt(params['observ'])

    ## Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']

    fit = Synfit({'vrot':[10, 20, 2]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['chisq'] == 0 # chi^2


def test_synfit_rv():
    """Test synfit with one parameter against a synthetic spectrum with radial
    velocity."""

    rad_vel = 50
    spec_file = 'test_spectrum.dat'

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1)


    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()
    #Adds a shit on wavelength for the synthetic spectrum due to radial velocity
    syn.spectrum[:, 0] *= s4.spectools.rvcorr(-rad_vel)

    syn.savetxt(spec_file)

    ## Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']
    params_copy['observ'] = 'test_spectrum.dat'
    params_copy['windows'] = [4465, 4475]
    params_copy['rv'] = rad_vel

    fit = Synfit({'vrot':[10, 20, 2]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(spec_file)

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert np.round(fit.best_fit['chisq'], 5) == 0 # chi^2


def test_synfit_two():
    """Test synfit with two parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()

    syn.savetxt(params['observ'])

    ## Test with two parameters
    params_copy = params.copy()
    del params_copy['vrot']
    del params_copy['vmac_rt']


    fit = Synfit({'vrot': [10, 20, 2], 'vmac_rt':[0, 10, 5]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])


    assert len(fit.best_fit.keys()) == 3
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['chisq'] == 0 # chi^2


def test_synfit_three():
    """Test synfit with three parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.savetxt(params['observ'])

    ## Test with three paramters
    params_copy = params.copy()
    del params_copy['teff']
    del params_copy['vrot']
    del params_copy['vmac_rt']

    fit = Synfit({'vrot':[10, 20, 2], 'vmac_rt':[0, 10, 5],
                  'teff':[19000, 22000, 1000]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 4
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['teff'] == params['teff']
    assert fit.best_fit['chisq'] == 0 # chi^2


def test_synfit_abund():
    """Test synfit for abundance against a synthetic spectrum."""

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.savetxt(params['observ'])

    ## Test with one parameter
    params_copy = params.copy()
    del params_copy['abund']

    fit = Synfit({'He':[10.90, 11.0, 0.02]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['abund'] == params['abund']
    assert fit.best_fit['chisq'] == 0 # chi^2


def test_synfit_four():
    """Test synfit with four parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.savetxt(params['observ'])

    ## Test with three paramters
    params_copy = params.copy()
    del params_copy['teff']
    del params_copy['vrot']
    del params_copy['vmac_rt']
    del params_copy['abund']

    fit = Synfit({'vrot':[10, 20, 2], 'vmac_rt':[0, 10, 5],
                  'teff':[19000, 22000, 1000], 'He':[10.90, 11.0, 0.02]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 5
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['teff'] == params['teff']
    assert fit.best_fit['abund'] == params['abund']


def test_synfit_windows():
    """
    Test synfit with one parameter and a windoow
    against a synthetic spectrum.
    """

    # Test with synthetic spectrum

    ## Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund='[2, 2, 10.96]', vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')


    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.savetxt(params['observ'])

    ## Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']
    params_copy['windows'] = [4465, 4475]

    fit = Synfit({'vrot':[10, 20, 2]},
                 params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['chisq'] == 0 # chi^2
    assert fit.best_fit['chisq'] == 0 # chi^2
