"""Installation requirements and general info.

Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""

from setuptools import setup

# Read conda requirements from conda-requirements.txt
with open('conda-requirements.txt', 'r', encoding="utf-8") as f:
    conda_requirements = [line.strip() for line in f if line.strip()]


# see setup.cfg
setup(name='nedextract',
      version='0.0.1',
      description='automatically extract information from Dutch annual report PDF files',
      author='Laura S. Ootes',
      author_email='l.ootes@esciencecenter.nl',
      python_requires='>=3.8',
      packages=['nedextract'],
      install_requires=['fuzzywuzzy==0.18.0',
                        'numpy>=1.23',
                        'pandas>=1.3.5',
                        'openpyxl==3.0.9',
                        'scikit-learn',
                        'stanza>=1.3.0',
                        'xlsxwriter',
                        'certifi',
                        'pdftotext==2.2.2'],
      license='Apache Software License',
      url='https://github.com/Transparency-in-the-non-profit-sector/np-transparency'
      )
