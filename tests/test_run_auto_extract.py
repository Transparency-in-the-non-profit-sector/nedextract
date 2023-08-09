"""Tests for run_auto_extract."""
import os
import unittest
from auto_extract.run_auto_extract import main


class TestRunAutoExtract(unittest.TestCase):
    """Class containing the unit test for the main function of run_auto_extract."""

    def test_main(self):
        """Unit test function for the 'main' function.

        It checks two scenarios:
        1. Testing with a file argument (-f option), using test file: tests/test_report.pdf
        2. Testing with a directory argument (-d option), using test directory: tests

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        indir = os.path.join(os.getcwd(), 'tests')
        infile = os.path.join(indir, 'test_report.pdf')

        # Test case 1
        testarg = ['-f', infile]
        returnargs = main(testarg)
        self.assertEqual(returnargs.file, infile)

        # Test case 2
        testarg = ['-d', indir]
        returnargs = main(testarg)
        self.assertEqual(returnargs.directory, indir)


if __name__ == '__main__':
    unittest.main()
