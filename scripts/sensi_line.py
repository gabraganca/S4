"""
The purpose of this sciprt is to make a nimated plot of how a stellar
parameter change on a spectral line or wavelength coverage.
"""

import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import s4

def main(v_param, values, wstart, wend, spath = None):
    """
    Parameters
    ---------

    v_param: str;
        Stelllar parameter to be changed.

    values: array;
        Array of values to plot the parameter.

    wstart: float;
        Beginning wavelength.

    wend: float;
        Ending wavelength.
    """

    # set basic stellar parameters params
    params = dict(wstart=wstart, wend=wend, relative=1)

    # check if v_param is teff or logg
    if v_param == 'teff':
        teff = values[0]
        logg = 4.0
    elif v_param == 'logg':
        teff = 20000
        logg = values[0]
    else:
        teff = 20000
        logg = 4.0
        params[v_param] = values[0]

    #print teff, logg, params
    #synthesize
    syn = s4.synthesis.Synplot(teff, logg, **params)
    syn.run()
    syn.plot()


if __name__ == '__main__':

    V_PARAM = sys.argv[1]
    VALUES = map(float, re.findall('\-?\d+(?:\.\d+)*', sys.argv[2]))
    WSTART = float(sys.argv[3])
    WEND = float(sys.argv[4])

    ### Test ###
   # print v_param, type(v_param)
   # print values, type(values)
   # print wstart, type(wstart)
   # print wend, type(wend)
    ### End Test ###

    main(V_PARAM, VALUES, WSTART, WEND)
