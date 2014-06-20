"""Test suite for Synplot"""
import os
from s4.synthesis import Synplot


TEFF = 20000
LOGG = 4.0
PARAMS = dict(wstart=4000, wend=4500, noplot=True, relative=1)


def test_synplot_run():
    """Test if Synplot is calculating a spectrum"""
    Synplot(TEFF, LOGG, **PARAMS).run()

def test_synplot_savetxt():
    """Test if Synplot is saving a spectrum"""
    fname = '/tmp/test.spec'

    _ = Synplot(TEFF, LOGG, **PARAMS)
    _.savetxt(fname)

    assert os.path.isfile(fname)
