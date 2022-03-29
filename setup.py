#!/usr/bin/env python

# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

from setuptools import setup
import os
import platform


# see setup.cfg
setup(name='run_auto_extract',
      version='0.0.1',
      description='automatically extract information from Dutch annual report PDF files',
      author='Laura S. Ootes',
      author_email='l.ootes@esciencecenter.nl',
      packages=['auto_extract'],
      install_requires=['fuzzywuzzy==0.18.0',
                        'numpy>=1.21.5',
                        'pandas>=1.3.5',
                        'python-Levenshtein==0.12.2',
                        'openpyxl==3.0.9',
                        'pdftotext==2.2.2',
                        'scikit-learn==1.0.2',
                        'stanza==1.3.0'],
      license='Apache Software License',
      url='https://github.com/Transparency-in-the-non-profit-sector/np-transparency'
      )

if platform.system() in ['Windows']:
    conda_dir = os.getenv('CONDA_PREFIX')
    anaconda_poppler_include_dir = os.path.join(conda_dir, 'Library\include')
    anaconda_poppler_library_dir = os.path.join(conda_dir, 'Library\lib')
    include_dirs = [anaconda_poppler_include_dir]
    library_dirs = [anaconda_poppler_library_dir]
