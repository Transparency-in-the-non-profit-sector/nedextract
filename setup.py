"""Installation requirements and general info.

Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""

from setuptools import setup

# Read conda requirements from conda-requirements.txt
with open('conda-requirements.txt', 'r') as f:
    conda_requirements = [line.strip() for line in f if line.strip()]


# see setup.cfg
setup(name='run_auto_extract',
      version='0.0.1',
      description='automatically extract information from Dutch annual report PDF files',
      author='Laura S. Ootes',
      author_email='l.ootes@esciencecenter.nl',
      python_requires='>=3.8',
      packages=['auto_extract'],
      license='Apache Software License',
      url='https://github.com/Transparency-in-the-non-profit-sector/np-transparency'
      )
