"""Tests for run_auto_extract"""
import os
from auto_extract.run_auto_extract import main


def test_main():
    """
    Unit test function for the 'main' function.

    It checks two scenarios:
    1. Testing with a file argument (-f option), using test file: tests/test_report.pdf
    2. Testing with a directory argument (-d option), using test directory: tests

    Raises:
        AssertionError: If any of the assert statements fail, indicating incorrect return values.
    """
    
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    testarg = ['-f', infile]
    returnargs = main(testarg)
    assert returnargs.file == infile
    testarg = ['-d', indir]
    returnargs = main(testarg)
    assert returnargs.directory == indir
