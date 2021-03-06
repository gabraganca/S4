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

.. image:: http://img.shields.io/travis/gabraganca/S4.svg
    :target: https://travis-ci.org/gabraganca/S4
    :alt: Travis CI build status
.. image:: https://coveralls.io/repos/github/gabraganca/S4/badge.svg?branch=master
    :target: https://coveralls.io/github/gabraganca/S4?branch=master

    

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

- `GNU Data Language <http://gnudatalanguage.sourceforge.net/downloads.php>`_
  greater than v0.9.6.

- `gfortran <https://gcc.gnu.org/fortran/>`_ is needed to compile
  ``Synspec`` and ``Rotins``

- `Numpy <http://www.numpy.org/>`_

- `Matplotlib <http://matplotlib.org/>`_

- `Scipy <http://www.scipy.org/>`_

- `Astropy <http://www.astropy.org/>`_

Citation
--------

If you use this software please cite as:

Bragança, Gustavo (2014): Stellar Spectral Synthesis Suite (S4). figshare.
http://dx.doi.org/10.6084/m9.figshare.1051627
