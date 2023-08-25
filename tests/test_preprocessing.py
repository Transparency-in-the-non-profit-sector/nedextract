"""This file contains the unit tests for the preprocessing functions of auto_extract."""
import os
import unittest
from nedextract.preprocessing import delete_downloaded_pdf
from nedextract.preprocessing import download_pdf
from nedextract.preprocessing import preprocess_pdf


class UnitTestsPreprocessing(unittest.TestCase):
    """Unit test class for testing functions used to preprocess text.

    Contains:
    - test_preprocess_pdf
    - test_download_pdf
    - test_delete_pdf
    """

    def test_preprocess_pdf(self):
        """Unit test for the function preprocess_pdf.

        The function tests the preprocess_pdf function that takes in a PDF file, reads the text content,
        and performs several text preprocessing steps to clean and format the text.
        """
        indir = os.path.join(os.getcwd(), 'tests')
        infile = os.path.join(indir, 'test_report.pdf')
        text = preprocess_pdf(infile, ' ')
        text = preprocess_pdf(infile, '. ')
        text = preprocess_pdf(infile, ', ')
        self.assertIsInstance(text, str)

    def test_download_pdf(self):
        """Unit test for the function download_pdf.

        This function tests the download_pdf dunction that downloads a pdf file from an url and safe it in the cwd.
        """
        url = ("https://github.com/Transparency-in-the-non-profit-sector/" +
               "np-transparency/blob/main/tests/test_report.pdf")
        filename = download_pdf(url)
        self.assertTrue(os.path.exists(filename))

    def test_delete_downloaded_pdf(self):
        """Unit test for the function delete_downloaded_pdf.

        This function tests the funciton delete_downloaded pdf that deletes the file that is downloaded with the function
        download_pdf and saved as downloaded.pdf from the cwd.
        """
        url = ("https://github.com/Transparency-in-the-non-profit-sector/" +
               "np-transparency/blob/main/tests/test_report.pdf")
        filename = download_pdf(url)
        delete_downloaded_pdf()
        filename = os.path.join(os.getcwd(), "downloaded.pdf")
        self.assertFalse(os.path.exists(filename))
