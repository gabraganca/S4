"""Test suite for Synplot"""
from __future__ import print_function
import os
import numpy as np
from s4.synthesis import Synplot


TEFF = 20000
LOGG = 4.0
PARAMS = dict(wstart=4000, wend=4500, noplot=True, relative=1)


def test_synplot_run():
    """Test if Synplot is calculating a spectrum"""
    try:
        syn = Synplot(TEFF, LOGG, **PARAMS)
        syn.run()
    except:
        # Print the output log of the Synplot command
        with open('run.log') as log:
            print(log.read())
        raise

    assert isinstance(syn.spectrum, np.ndarray)


def test_synplot_save():
    """Test if Synplot is saving a spectrum"""
    fname = '/tmp/test.spec'

    syn = Synplot(TEFF, LOGG, **PARAMS)
    syn.run()
    syn.save_spec(fname)

    assert os.path.isfile(fname)


def test_synplot_lineid_select():
    """Test Synplot line identification"""

    syn = Synplot(TEFF, LOGG, **PARAMS)
    syn.run()

    # All lines
    for line_strength in range(0, 500, 50):
        wave_list, text_list = syn.lineid_select(line_strength)
        assert len(wave_list) == len(text_list)
        assert all(isinstance(wave, float) for wave in wave_list)
        assert all(isinstance(text, str) for text in text_list)
        assert all([float(row.split()[-1]) >= line_strength
                    for row in text_list])


def test_synplot_apply_scale():
    """Test Synplot method `apply_scale`"""

    scale = 2

    syn = Synplot(TEFF, LOGG, **PARAMS)
    syn.parameters['scale'] = scale
    syn.run()

    flux = syn.spectrum[:, 1].copy()

    syn.apply_scale()
    new_flux = syn.spectrum[:, 1]

    assert np.array_equal(flux*scale, new_flux)
