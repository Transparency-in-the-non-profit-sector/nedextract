"""Tests for run_nedextract."""
import glob
import numpy as np
import os
from os.path import exists
import pandas as pd
import time
import unittest
from nedextract.run_nedextract import run
from nedextract.run_nedextract import output_to_df
from nedextract.run_nedextract import write_output


# Input data used for tests
indir = os.path.join(os.getcwd(), 'tests')
file = 'test_report.pdf'
infile1 = os.path.join(indir, file)
url = 'https://github.com/Transparency-in-the-non-profit-sector/nedextract/blob/main/tests/test_report.pdf'


# Expected dataframe for the test case of a sector task
e_df_g = pd.DataFrame({'Input_file': [file], 'Organization': ['Bedrijf'], 'Main_sector': ['Natuur en milieu']})


class TestRunAutoExtract(unittest.TestCase):
    """Class containing the unit test for the function in run_nedextract.

    Test_methods:
        - test_run: tests the run function tha runs the full pipeline of nedextract.
        - test_output to df: tests the output_to_df function that converts numpy arrays
        to pandas dataframes with correct column names.
        - test_write_output
    """

    def test_run(self):
        """
        Unit test function for the 'run' function.

        This function tests the run function tha runs the full pipeline of nedextract.

        It checks two scenarios:
        1. Testing with a file argument, using test file: tests/test_report.pdf
        2. Testing with a directory argument, using test directory: tests

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        # Test case 1
        df1, _, _ = run(file=infile1)
        self.assertTrue(isinstance(df1, pd.DataFrame))

        # Test case 2
        df1, _, _ = run(directory=indir)
        self.assertTrue(isinstance(df1, pd.DataFrame))

    def test_output_to_df(self):
        """
        Unit test function for the 'output_to_df' function.

        This function tests the output_to_df function that converts numpy arrays
        to pandas dataframes with correct column names.

        Test case:
        1. asser if the numpy arrays for a sector class equal the expeected returned dataframe

        Returns:
            AssertionError: If the assertEqual statements fails, indicating incorrect return values.
        """
        e_og = np.array([[os.path.basename(file), 'Bedrijf', 'Natuur en milieu']])
        _, df_g, _ = output_to_df(opd_g=e_og)

        self.assertEqual(True, df_g.equals(e_df_g))

    def test_write_output(self):
        """Unit test for the write_output function.

        This function tests the write_output function that writes for each given task
        a pandas dataframe to an output file.

        Testcase: check if an excel file exists once when the write output function is called
        for the sector task.

        Returns:
            AssertionError: If the expected outputfile does not exist, indicating that the file was not created
        """
        write_output(tasks='sectors', dfg=e_df_g)
        outtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        # omit time, only check date
        testtime = str(outtime)[0:9]

        writefile = os.path.join(os.path.join(os.path.join('..', os.getcwd()), 'Output'),
                                 'output' + str(testtime) + '*_general.xlsx')

        self.assertTrue(exists(glob.glob(writefile)[0]))

        # remove created file
        os.remove(glob.glob(writefile)[0])


if __name__ == '__main__':
    unittest.main()
