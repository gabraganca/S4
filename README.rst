Stellar Spectral Synthesis Suite
================================

Introduction
------------

The Stellar Spectral Synthesis Suite (``S4``, for short) is a suite of routines
aimed to perform high-quality spectral synthetic fitting of massive stars
observed spectra.

The spectral synthesis are done with
`Synspec <http://nova.astro.umd.edu/Synspec49/synspec.html>`_ based on
atmospheric models calculated with `Tlusty <http://nova.astro.umd.edu/>`_
(Hubeny & Lanz et al.).

How to get it?
--------------

You can get the latest stable version
`here <https://github.com/gabraganca/S4/releases>`_. Unpack it, go into the
directory and then run the below commands. I recommend having
`pip <https://pypi.python.org/pypi/pip>`_ installed.
It makes installation and uninstallation a lot easier.

::

    python setup.py build
    pip install .

If you have any problems, check if all dependencies are installed. The
dependencies can be seen below.

Also, if you want the bleeding edge version, you can clone the repository, and
then run the above commands inside the ``S4`` directory. If you are unfamiliar
to `git <http://git-scm.com/>`_, just type:

::

     git clone git@github.com:gabraganca/S4.git


Dependencies
------------

- ITT's IDL. There is also an option to run with GDL, but the Synplot version
  shipped with S4 do not support GDL.

- ``Intel Fortran Compiler`` or ``f77`` are needed to compile
  ``Synspec`` and ``Rotins``

- `Numpy <http://www.numpy.org/>`_

- `Matplotlib <http://matplotlib.org/>`_

- `Scipy <http://www.scipy.org/>`_

- `Lineid_plot <https://github.com/phn/lineid_plot>`_


SAGUI
-----

SAGUI stands for stellar spectral **S**\ynthesis **A**\chieves a **G**\raphical
**U**\ser **I**\nterface. It is a Qt GUI to syntesize spectra using Synspec.

`Sagui <http://en.wikipedia.org/wiki/Callitrichinae>`_ is a family of New World
monkey very common on Brazil.

To use it, simply type *sagui* on your console.


Sensi_line
----------

This make a animated plot of a synthetic spectrum varying by a given parameter.
For example, let's suppose that you wan to see how the the Helium line at 4026
angstrons vary with effective temperature from 20000 K up to 25000 K with steps
of 2500K. You simply have to type on your console:

::

    sensi_line teff '[20000, 22500, 25000]' 4460 4480

First you should call the script with the following parameters: the parameter
you want to vary, an array of values for that parameter, the beginning and
ending wavelength.
