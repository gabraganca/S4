"""Test suite for Synplot"""
import os
from s4.synthesis import Synplot


TEFF = 20000
LOGG = 4.0
PARAMS = dict(wstart=4000, wend=4500, noplot=True, relative=1)


def test_synplot_run():
    """Test if Synplot is calculating a spectrum"""
    try:
        Synplot(TEFF, LOGG, **PARAMS).run()
    except:
        # Print the output log of the Synplot command
        with open('run.log') as f:
            print (f.read())
        raise

def test_synplot_save():
    """Test if Synplot is saving a spectrum"""
    fname = '/tmp/test.spec'

    _ = Synplot(TEFF, LOGG, **PARAMS)
    _.save_spec(fname)

    assert os.path.isfile(fname)
