"""Tests for functions included in read_pdf."""
import os
import unittest
import numpy as np
import stanza
from nedextract.preprocessing import preprocess_pdf
from nedextract.read_pdf import PDFInformationExtractor


# Files containing unit ttest data
indir = os.path.join(os.getcwd(), 'tests')
infile1 = os.path.join(indir, 'test_report.pdf')
infile2 = os.path.join(indir, 'test_report3.pdf')

# Inout for test cases
people = ('A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nD.A. Rooden\n' +
          'Dirkje Rooden\nE. van Grijs\nEduard van Grijs\nF. de Blauw\nFerdinand de Blauw\n' +
          'G. Roze\nGerard Roze\nH. Doe\nHendrik Doe\nHendrik Groen\nIsaak Paars\nJ. Doe\n' +
          'Jan van Oranje\nJane Doe\nKarel\nLodewijk\nMaria\nMohammed El Idrissi\n' +
          'Mr. H. Hendrik Groen\nNico\nOtto\nPieter\nSarah\nSaïda Benali\nThomas\n')
bestuursmensen = ('Jane Doe\nDirkje Rooden\nEduard van Grijs\nFerdinand de Blauw\n' +
                  'Anna de Wit\nHendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\n' +
                  'Jan van Oranje\nKarel\nLodewijk\nMaria\nGerard Roze\n' +
                  'Hendrik Groen\nMohammed El Idrissi\nSaïda Benali\n')
posities = ('Anna de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
            'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
            'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
            'Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
            'Cornelis Geel - rvt - lid\nIsaak Paars - ledenraad - voorzitter\n' +
            'Jan van Oranje - ledenraad - penningmeester\nKarel - ledenraad - lid\n' +
            'Lodewijk - ledenraad - \nMaria - ledenraad - \n' +
            'Mohammed El Idrissi - controlecommissie - \n' +
            'Saïda Benali - controlecommissie - \nBernard Zwartjes - rvt - \n')

# Expected output for test cases
expected_output_people = ([os.path.basename(infile1),
                           'Bedrijf',
                           people,
                           'Sarah\nThomas\n',
                           bestuursmensen,
                           posities,
                           'Jane Doe', '', '', '', '',
                           'Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '',
                           'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '', '', '',
                           'Gerard Roze', 'Hendrik Groen', '', '', '',
                           'Mohammed El Idrissi', 'Saïda Benali', '', '', ''])

e_op1 = np.array([[os.path.basename(infile1), 'Bedrijf',
                   'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nD.A. Rooden\n' +
                   'Dirkje Rooden\nE. van Grijs\nEduard van Grijs\nF. de Blauw\nFerdinand de Blauw\n' +
                   'G. Roze\nGerard Roze\nH. Doe\nHendrik Doe\nHendrik Groen\nIsaak Paars\nJ. Doe\n' +
                   'Jan van Oranje\nJane Doe\nKarel\nLodewijk\nMaria\nMohammed El Idrissi\n' +
                   'Mr. H. Hendrik Groen\nNico\nOtto\nPieter\nSarah\nSaïda Benali\nThomas\n',
                   'Sarah\nThomas\n',
                   'Jane Doe\nDirkje Rooden\nEduard van Grijs\nFerdinand de Blauw\nAnna de Wit\n' +
                   'Hendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\nJan van Oranje\n' +
                   'Karel\nLodewijk\nMaria\nGerard Roze\nHendrik Groen\nMohammed El Idrissi\n' +
                   'Saïda Benali\n',
                   'Anna de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
                   'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
                   'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
                   'Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
                   'Cornelis Geel - rvt - lid\nIsaak Paars - ledenraad - voorzitter\n' +
                   'Jan van Oranje - ledenraad - penningmeester\nKarel - ledenraad - lid\n' +
                   'Lodewijk - ledenraad - \nMaria - ledenraad - \n' +
                   'Mohammed El Idrissi - controlecommissie - \nSaïda Benali - controlecommissie - \n' +
                   'Bernard Zwartjes - rvt - \n',
                   'Jane Doe', '', '', '', '',
                   'Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '', '', '',
                   '', '', '', '', '', '', '', '', '', '', '', '',
                   'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '', '', '',
                   '', '', '', '', '', '', '', '', '', '', '',
                   'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '', '', '',
                   '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                   'Gerard Roze', 'Hendrik Groen', '', '', '',
                   'Mohammed El Idrissi', 'Saïda Benali', '', '', '']])

e_op2 = np.array(([[os.path.basename(infile2), 'Bedrijf',
                    'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nH. Doe\nHendrik Doe\n' +
                    'J. Doe\nJane Doe\nQuirine de Bruin\nRudolph de Bruin\nSimon de Zwart\n' +
                    'Tinus de Zwart\nVictor Wit\nWillem Wit\nXantippe de Bruin\nYolanda\nZander\n',
                    '',
                    'Jane Doe\nAnna de Wit\nHendrik Doe\nBernard Zwartjes\nCornelis Geel\n',
                    'Anna de Wit - rvt - vice-voorzitter\nHendrik Doe - rvt - voorzitter\n' +
                    'Jane Doe - directeur - directeur\nBernard Zwartjes - rvt - \n' +
                    'Cornelis Geel - rvt - lid\n',
                    'Jane Doe', '', '', '', '',
                    'Anna de Wit', 'Hendrik Doe', 'Bernard Zwartjes', 'Cornelis Geel',
                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                   '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                    '', '', '', '', '', '', '', '', '', '', '', '', '']]))


class TestReadPDF(unittest.TestCase):
    """Unit test class for the PDFInformationExtractor.

    Test Methods:
        - test_extract_pdf: Tests the 'extract_pdf' function for information extraction from PDF files using the stanza
          pipeline.
        - test_output_people: Tests the 'output_people' function for gathering information about people and structuring the
          output.
        - test_ots: Tests the 'ots' function to convert a NumPy array of strings into a backspace-separated string.
        - test_atc: Tests the 'atc' function to split an array into specified columns for output.
        - test_stanza_NL: Tests the 'download_stanza_NL' function to download the Stanza data for the Dutch language.

    Each test method contains one or more test cases, and assertions are used to validate the output
    against expected results.
    """

    def test_extract_pdf(self):
        """Unit test function for the 'extract_pdf' method using multiple test cases.

        The tests use two predefined test pdf files.

        Test Cases:
        1. Extract all information ('all' tasks)
        2. Extract sector information only ('sectors' task)
        3. Extract names of people only for test file 1 ('people' task)
        4. Extract mentioned organizations only ('orgs' task)
        5. Extract names of people only for test file 2 ('people' task)

        Raises:
        AssertionError: If any of the test cases fail (if the actual output does not match the expected output).
        """
        # Test case 1
        tasks = ['people', 'orgs']
        extractor = PDFInformationExtractor(tasks, None, None, None)
        opd_p = np.array([]).reshape(0, 91)
        opd_g = np.array([]).reshape(0, 3)
        opd_o = np.array([]).reshape(0, 3)
        op, _, oo = extractor.extract_pdf(infile1, opd_p, opd_g, opd_o)
        e_oo = np.array([[os.path.basename(infile1), 'Bedrijf2', '1'],
                         [os.path.basename(infile1), 'Bedrijf3', '1']])
        self.assertTrue(np.all(e_op1 == op))
        self.assertTrue(np.all(e_oo == oo))

        # Test case 3
        opd_p = np.array([]).reshape(0, 91)
        opd_g = np.array([]).reshape(0, 3)
        opd_o = np.array([]).reshape(0, 3)
        tasks = ['people']
        extractor = PDFInformationExtractor(tasks, None, None, None)
        op, _, oo = extractor.extract_pdf(infile1, opd_p, opd_g, opd_o)
        self.assertTrue(np.all(e_op1 == op))
        self.assertTrue(np.all(oo == opd_o))

        # Test case 4
        opd_p = np.array([]).reshape(0, 91)
        opd_g = np.array([]).reshape(0, 3)
        opd_o = np.array([]).reshape(0, 3)
        tasks = ['orgs']
        extractor = PDFInformationExtractor(tasks, None, None, None)
        op, _, oo = extractor.extract_pdf(infile1, opd_p, opd_g, opd_o)
        self.assertTrue(np.all(op == opd_p))
        self.assertTrue(np.all(oo == e_oo))

        # Test case 5
        opd_p = np.array([]).reshape(0, 91)
        opd_g = np.array([]).reshape(0, 3)
        opd_o = np.array([]).reshape(0, 3)
        tasks = ['people']
        extractor = PDFInformationExtractor(tasks, None, None, None)
        op, _, oo = extractor.extract_pdf(infile2, opd_p, opd_g, opd_o)
        self.assertTrue(np.all(op == e_op2))

    def test_ouput_people(self):
        """Unit test function for the output_people method.

        This method tests the function which gathers information about people mentioned in a text (name and funciton)
        and structures the output. The tests use the predefined test pdf file 'infile1'.

        After extracting from the test file the text (using preprocess_pdf) and the doc (using the stanza pipeline)
        the test asserts that the output of the 'output_people' method matches the 'expected_output_people'.

        Raises:
            AssertionError: If the actual output of 'output_people' does not match the 'expected_output_people'.
        """
        extractor = PDFInformationExtractor(None, None, None, None)
        text = preprocess_pdf(infile1, ' ')
        doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)
        self.assertEqual(extractor.output_people(infile1, doc, 'Bedrijf'), expected_output_people)

    def test_ots(self):
        r"""Unit test function for the 'ots' method.

        This function tests the 'ots' function, which converts a NumPy array of strings
        into a single concatenated string with each element separated by a newline.

        The test creates a sample NumPy array ('test') containing two strings, 'test' and 'test2',
        and asserts that the output of the 'ots' function matches the expected string:
        "test\ntest2\n".

        Raises:
            AssertionError: If the output of the 'ots' function does not match the expected string.
        """
        test = np.array(['test', 'test2'])
        self.assertEqual(PDFInformationExtractor.ots(test), str('test\ntest2\n'))

    def test_atc(self):
        """Unit test function for the 'atc' method.

        This function tests the 'atc' function, which splits an array into [length] list variables.

        The test creates a sample NumPy array ('test') containing three strings, and asserts that for a given 'length' parameter 2
        that the output of the 'ats' function matches a list with the expected two strings.

        Raises:
            AssertionError: If the output of the 'ats' function does not match the expected string.
        """
        extractor = PDFInformationExtractor(None, None, None, None)
        test = np.array(['Jane', 'Doe', 'John Doe'])
        self.assertEqual(extractor.atc(test, 2), ['Jane', 'Doe\nJohn Doe\n'])

    def test_stanza_NL(self):
        """Unit test function for the 'download_stanza_NL' function.

        This function tests the 'download_stanza_NL' function by checking if the downloaded
        stanza data file exists. The function downloads the required Stanza
        (NLP library) data for the Dutch language.

        Raises:
            AssertionError: If the 'download_stanza_NL' function fails to download the data
                            or if the downloaded file does not exist.
        """
        self.assertTrue(os.path.exists(PDFInformationExtractor.download_stanza_NL()))


if __name__ == '__main__':
    unittest.main()
