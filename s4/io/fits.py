"""
In this module we have the methods regarding Input/Output.
"""
import numpy as np
from astropy.io import fits as pyfits


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

    # Load spectrum
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
