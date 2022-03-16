#!/usr/bin/env python

# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

from setuptools import setup


# see setup.cfg
setup(name='run_auto_extract',
      version='0.0.1',
      description='automatically extract information from annual report PDF files',
      author='Laura S. Ootes',
      author_email='l.ootes@esciencecenter.nl',
      packages=['auto_extract'],
      install_requires=['numpy', 'pandas', 'stanza', 'fuzzywuzzy', 'pdftotext'],
      license='',
      url=''
      )
