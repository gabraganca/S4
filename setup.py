"""
Install package.
"""

from distutils.core import setup
from distutils.spawn import find_executable
import subprocess as sp
from glob import glob
import os
from pwd import getpwnam

VERSION = '0.3.dev'

# Compiling Synspec and Rotin3 if compiler ios available
if glob('s4/synthesis/synplot/synspec49') == []:
    if find_executable('gfortran'):
        print 'gfortran available.\nCompiling Synspec49.'
        command = ['gfortran', '-g', '-fno-automatic', '-static', '-o']
        sp.check_call(command +                                    \
                      ['s4/synthesis/synplot/synspec49',           \
                       's4/synthesis/synplot/synspec49.f'])
        print 'Compiling Rotin3'
        sp.check_call(command +                                    \
                      ['s4/synthesis/synplot/rotin3',              \
                       's4/synthesis/synplot/rotin3.f'])
    else:
        print 'gfortran is not available. ' +\
              'Synspec and Rotin will not be compiled.'

#Make list of data files
atdata = glob('s4/synthesis/atdata/*')
bstar2006 = glob('s4/synthesis/bstar2006/*')
synplot = glob('s4/synthesis/synplot/*')
extra_resc = glob('extra_resc/*')
#path to data_files
home = os.getenv('HOME')
path = home+'/.s4'
user = home.split('/')[-1]



DESCRIPTION = "Stellar Spectral Synthesis Suite"
LONG_DESCRIPTION = open('README.rst').read()
NAME = "S4"
VERSION = 'v1.0-dev'
AUTHOR = "Gustavo de Almeida Braganca"
AUTHOR_EMAIL = "ga.braganca@gmail.com"
MAINTAINER = "Gustavo de Almeida Braganca"
MAINTAINER_EMAIL = "ga.braganca@gmail.com"
DOWNLOAD_URL = 'http://github.com/gabraganca/S4'
LICENSE = 'BSD'


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=['s4',
                's4.spectools',
                's4.plottools',
                's4.synthesis',
                's4.fitting',
                's4.utils',
                's4.io',
                's4'],
      data_files=[(path+'/synthesis/atdata', atdata),
                  (path+'/synthesis/bstar2006', bstar2006),
                  (path+'/synthesis/synplot', synplot),
                  (path+'/synthesis/synplot', synplot),
                  (path+'/extra_resc', extra_resc)],
      classifiers=[
        'Development Status :: Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Astronomy'],
    )

#Change ownership of data _files from root to user, recursevely
for root, dirs, files in os.walk(path):
    for momo in dirs:
        os.chown(os.path.join(root, momo), getpwnam(user).pw_uid,            \
                 getpwnam(user).pw_gid)
    for momo in files:
        os.chown(os.path.join(root, momo), getpwnam(user).pw_uid,            \
                  getpwnam(user).pw_gid)
