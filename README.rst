Stellar Spectral Synthesis Suite
================================

Introduction
------------

A Stellar Spectral Synthesis Suite (S4, for short). This is a suit that holds
python modules that are aimed to spectral synthesis reduction of observed
spectra.

The spectral synthesis are done with Tlusty/Synspec (Hubeny & Lanz et al.)

SAGUI
-----

SAGUI stands for stellar spectral **S**\ynthesis **A**\chieves a **G**\raphical
**U**\ser **I**\nterface. It is a Qt GUI to syntesize spectra using Synspec.

Sagui is a family of New World monkey very common on Brazil.

To use it, simply type *sagui* on your console.

Sensi_line
----------

This make a animated plot of a synthetic spectrum varying by a given parameter. 
For example, let's suppose that you wan to see how the the Helium line at 4026 
angstrons vary with effective temperature from 20000 K up to 25000 K with steps 
of 2500K. You simply have to type on your console:

::

    sensi_line teff '[20000, 22500, 25000]' 4460 4480
    
First you should call the script with the following parameters: the parameter you 
rant to vary, an array of values for that parameter, the beginning and ending 
wavelength.

Dependencies
------------

- ITT's IDL. There is also an option to run with GDL, but the Synplot version
  shipped with S4 do not support GDL.

- Numpy

- Matplotlib

- Scipy

- `Lineid_plot <https://github.com/phn/lineid_plot>`_

- `Periodic <http://pythonhosted.org/periodic/>`_
