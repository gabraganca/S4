from distutils.core import setup

DESCRIPTION = "Stellar Spectral Synthesis Suite"
LONG_DESCRIPTION = open('README.rst').read()
NAME = "S4"
AUTHOR = "Gustavo de Almeida Braganca"
AUTHOR_EMAIL = "ga.braganca@gmail.com"
MAINTAINER = "Gustavo de Almeida Braganca"
MAINTAINER_EMAIL = "ga.braganca@gmail.com"
DOWNLOAD_URL = 'http://github.com/gabraganca/S4'
LICENSE = 'BSD'

import s4

setup(name=NAME,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=['s4',
                's4.spectra',
                's4.idlwrapper',
                's4.plot',
                's4'],
      classifiers=[
        'Development Status :: Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Astronomy'],
     )
