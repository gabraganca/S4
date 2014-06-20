"""
In this module we have the methods regarding Input/Output.
"""
import os
import numpy as np
from astropy.io import fits as pyfits


def loadtxt_fast(filename, dtype=np.int, skiprows=0, delimiter=' '):
    """
    Function to load text files. Faster than numpy.loadtxt

    Obtained from http://cyrille.rossant.net/numpy-performance-tricks/

    Parameters
    ----------

    filename: str;
        Name of the file to be loaded.

    dtype: dtype;
        Data type.

    skiprows: int (optional);
        Number of rows to skip. The default is 0.

    delimiter: str (optional);
        The delimiter. The default is ' '.

    Returns
    -------

    A numpy.ndarray with the data.
    """
    def iter_func():
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            skip = 0
            for line in infile:
                line = line.strip().split(delimiter)
                for item in line:
                    yield dtype(item)
            loadtxt_fast.rowlength = len(line)
    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, loadtxt_fast.rowlength))
    return data


def get_wstart(ref, wave_ref, wave_per_pixel):
    """
    Obtain the starting wavelength of a spectrum.

    Parameters
    ----------

    ref: int,
        Reference pixel.

    wave_ref: float,
        Coordinate at reference pixel.

    wave_per_pixel: float,
        Coordinate increase per pixel.

    Returns
    -------

    wstart: float,
        Starting wavelength.
    """

    return wave_ref - ((ref-1) * wave_per_pixel)


def get_wavelength(start_wave, wave_per_pixel, size):
    """
    Obtain an array of wavelengths according to input values.

    Parameters
    ----------

    start_wave: float,
        Starting wavelength.

    wave_per_pixel: float,
        Wavelength per pixel.

    size: int,
        Size of array.

    Returns
    -------

    wave_array: numpy.ndarray,
        Wavelength array
    """

    return np.array([start_wave + i*wave_per_pixel for i in range(size)])


def load_spectrum(fname):
    """
    Loads the spectrum in FITS format to a numpy.darray.

    Parameters
    ----------

    fname: str,
        File name of the FITS spectrum.

    Returns
    -------

    spectrum: ndarray,
        Spectrum array with wavelength and flux.
    """

    #Get real path of spectrum
    fname = os.path.realpath(fname)

    # Load spectrum
    if fname.split('.')[1] == 'fits':
        spec_FITS = pyfits.open(fname)
        #Load flux
        flux = spec_FITS[0].data

        #Obtain parameters for wavelength determination from header
        ref_pixel = spec_FITS[0].header['CRPIX1']        # Reference pixel
        coord_ref_pixel = spec_FITS[0].header['CRVAL1']  # Wavelength at ref. pixel
        wave_pixel = spec_FITS[0].header['CDELT1']       # Wavelength per pixel

        #Get starting wavelength
        wstart = get_wstart(ref_pixel, coord_ref_pixel, wave_pixel)

        #Obtain array of wavelength
        wave = get_wavelength(wstart, wave_pixel, len(flux))

        return np.dstack((wave, flux))[0]
    else:
        return loadtxt_fast(fname, np.float)
