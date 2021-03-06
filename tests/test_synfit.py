"""
Test suite for Synfit and complementary functions.
"""
import os
import numpy as np
import s4
from s4.synthesis import Synplot
from s4.fitting import Synfit


def test_sample_params_error():
    """
    Test if the Synfit.sample_params is throwing an error
    for the wrong parameters.
    """
    params = dict(teff=20000, logg=4)

    try:
        Synfit({'vrot': [10, 20, 2, 5]}, **params)
    except KeyError:
        pass


def test_synfit_one():
    """Test synfit with one parameter against a synthetic spectrum."""

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()
    syn.save_spec(params['observ'])

    # Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']

    fit = Synfit({'vrot': [10, 20, 2]},
                 **params_copy)
    try:
        fit.fit()
    except:
        # Print the output log of the Synplot command
        with open('run.log') as log:
            print(log.read())
        raise

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['chisquare'] == 0  # chi^2


def test_synfit_rv():
    """Test synfit with one parameter against a synthetic spectrum with radial
    velocity."""

    rad_vel = 50
    spec_file = 'test_spectrum.dat'

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1)

    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()

    # Adds a shit on wavelength for the synthetic spectrum due to
    # radial velocity
    syn.spectrum[:, 0] *= s4.spectools.rvcorr(-rad_vel)

    syn.save_spec(spec_file)

    # Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']
    params_copy['observ'] = 'test_spectrum.dat'
    params_copy['windows'] = [4465, 4475]
    params_copy['rv'] = rad_vel

    fit = Synfit({'vrot': [10, 20, 2]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(spec_file)

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert np.round(fit.best_fit['chisquare'], 5) == 0  # chi^2


def test_synfit_two():
    """Test synfit with two parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()

    syn.save_spec(params['observ'])

    # Test with two parameters
    params_copy = params.copy()
    del params_copy['vrot']
    del params_copy['vmac_rt']

    fit = Synfit({'vrot': [10, 20, 2], 'vmac_rt': [0, 10, 5]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 3
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['chisquare'] == 0  # chi^2


def test_synfit_three():
    """Test synfit with three parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'],
                  wstart=params['wstart'], wend=params['wend'],
                  relative=params['relative'], vrot=params['vrot'],
                  abund=params['abund'], vmac_rt=params['vmac_rt'])

    syn.run()
    syn.save_spec(params['observ'])

    # Test with three paramters
    params_copy = params.copy()
    del params_copy['teff']
    del params_copy['vrot']
    del params_copy['vmac_rt']

    fit = Synfit({'vrot': [10, 20, 2], 'vmac_rt': [0, 10, 5],
                  'teff': [19000, 22000, 1000]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 4
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['teff'] == params['teff']
    assert fit.best_fit['chisquare'] == 0  # chi^2


def test_synfit_abund():
    """Test synfit for abundance against a synthetic spectrum."""

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93, 'S': 7.12},
                  wstart=4460, wend=4480, noplot=True, relative=1, vmac_rt=5,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.run()
    syn.save_spec(params['observ'])

    # Test with one parameter
    params_copy = params.copy()

    fit = Synfit({'He': [10.89, 10.95, 0.02]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert 'S' in fit.synthesis.parameters['abund']
    assert fit.best_fit['He'] == params['abund']['He']
    assert fit.best_fit['chisquare'] == 0  # chi^2


def test_synfit_four():
    """Test synfit with four parameters against a synthetic spectrum."""

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.run()
    syn.save_spec(params['observ'])

    # Test with three paramters
    params_copy = params.copy()
    del params_copy['teff']
    del params_copy['vrot']
    del params_copy['vmac_rt']
    del params_copy['abund']

    fit = Synfit({'vrot': [10, 20, 2], 'vmac_rt': [0, 10, 5],
                  'teff': [19000, 22000, 1000], 'He': [10.89, 10.95, 0.02]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 5
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['vmac_rt'] == params['vmac_rt']
    assert fit.best_fit['teff'] == params['teff']
    assert fit.best_fit['He'] == params['abund']['He']


def test_synfit_windows():
    """
    Test synfit with one parameter and a windoow
    against a synthetic spectrum.
    """

    # Test with synthetic spectrum

    # Creates a fake spectrum
    params = dict(teff=20000, logg=4, vrot=16, abund={'He': 10.93}, vmac_rt=5,
                  wstart=4460, wend=4480, noplot=True, relative=1,
                  observ='test_spectrum.dat')

    syn = Synplot(params['teff'], params['logg'], wstart=params['wstart'],
                  wend=params['wend'], relative=params['relative'],
                  vrot=params['vrot'], abund=params['abund'],
                  vmac_rt=params['vmac_rt'])

    syn.run()
    syn.save_spec(params['observ'])

    # Test with one parameter
    params_copy = params.copy()
    del params_copy['vrot']
    params_copy['windows'] = [4465, 4475]

    fit = Synfit({'vrot': [10, 20, 2]},
                 **params_copy)
    fit.fit()

    # Remove synthetic spectrum
    os.remove(params['observ'])

    assert len(fit.best_fit.keys()) == 2
    assert fit.best_fit['vrot'] == params['vrot']
    assert fit.best_fit['chisquare'] == 0  # chi^2
