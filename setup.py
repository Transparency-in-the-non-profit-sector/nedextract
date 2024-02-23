"""Setup."""
from setuptools import setup
import sys
import os

# Get the parent directory of the current file (setup.py)
parent_dir = os.path.abspath(os.path.dirname(__file__))

# Add the parent directory to the Python path
sys.path.insert(0, parent_dir)

# see setup.cfg
if __name__ == "__main__":
    setup(name="nedextract",
          python_requires='>=3.8')
