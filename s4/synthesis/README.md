SYNPLOT
=======

Introduction
-------

A IDL wrapper to [Synspec](http://nova.astro.umd.edu/Synspec49/synspec.html),
a general spectrum synthesis program. It was written by [Dr. I. Hubeny](mailto:hubeny@as.arizona.edu)
and [Dr. T. Lanz](mailto:thierry.lanz@oca.eu).

**This is the version available on the website and do not represente the latest
development.** This version is availabe here so S4 developers have something to
work on.

Requirements
------------
* [IDL](http://www.exelisvis.com/ProductsServices/IDL.aspx);
* gfortran.

When installing, two fortran files will be compiled using gfortran:

    $ gfortran -g -fno-automatic -static -o synspec49 synspec49.f
    $ gfortran -g -fno-automatic -static -o rotin3 rotin3.f

References
----------
***NLTE line blanketed model atmospheres of hot stars. I. Hybrid Complete Linearization/Accelerated Lambda Iteration Method***, 1995, Hubeny, I., & Lanz, T., Astrophysical Journal, 439, 875 ([Abstract](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?1995ApJ...439..875H&db_key=AST)) ([Full article](http://adsabs.harvard.edu/cgi-bin/nph-article_query?1995ApJ...439..875H&db_key=AST), [PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/1995ApJ...439..875H.pdf))

***A Grid of Non-LTE Line-blanketed Model Atmospheres of O-type Stars***, 2003, Lanz, T., & Hubeny, I., Astrophysical Journal Supplement Series, 146, 417 ([Abstract](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?2003ApJS..146..417L&db_key=AST)) ([PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/2003ApJS146.pdf))

***Model Photospheres with Accelerated Lambda Iteration***, 2003, Hubeny, I., & Lanz, T., in Stellar Atmosphere Modeling, Eds. I. Hubeny et al., ASP Conf. Ser., 288, 51 ([PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/atmos02_hubeny.pdf))

***Atomic Data in Non-LTE Model Stellar Atmospheres***, 2003, Lanz, T., & Hubeny, I., in Stellar Atmosphere Modeling, Eds. I. Hubeny et al., ASP Conf. Ser., 288, 117 ([PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/atmos02_lanz.pdf))

***A computer program for calculating non-LTE model stellar atmospheres***, 1988, Hubeny, I., Computer Physics Comm., 52, 103 ([Abstract](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?1988CoPhC..52..103H&db_key=AST))

***NLTE model stellar atmospheres with line blanketing near the series limits***, 1994, Hubeny, I., Hummer, D.G., & Lanz, T., Astronomy & Astrophysics, 282, 151 ([Abstract](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?1994A&A...282..151H&db_key=AST)) ([Full article](http://adsabs.harvard.edu/cgi-bin/nph-article_query?1994A&A...282..151H&db_key=AST), [PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/1994A+A...282..151H.pdf))

***Accelerated complete-linearization method for calculating NLTE model stellar atmospheres***, 1992, Hubeny, I., & Lanz, T., Astronomy & Astrophysics, 262, 501 ([Abstract](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?1992A&A...262..501H&db_key=AST)) ([Full article](http://adsabs.harvard.edu/cgi-bin/nph-article_query?1992A&A...262..501H&db_key=AST), [PDF](http://nova.astro.umd.edu/Tlusty2002/pdf/1992A+A...262..501H.pdf))

