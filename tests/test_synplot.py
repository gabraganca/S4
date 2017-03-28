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
