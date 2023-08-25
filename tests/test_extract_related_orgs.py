"""The file contains functions used to test the functions in exract_related orgs.

Functions:
- test_collect_orgs
- test_decide_org
- test_match_anbis
- test_apply_matching
"""

import os
import unittest
import numpy as np
import pandas as pd
import stanza
from nedextract.extract_related_orgs import apply_matching
from nedextract.extract_related_orgs import collect_orgs
from nedextract.extract_related_orgs import decide_org
from nedextract.extract_related_orgs import match_anbis
from nedextract.preprocessing import preprocess_pdf


# Define test text
stanza.download('nl')
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
doc = nlp(text)


class TestExtractRelatedOrgas(unittest.TestCase):
    """Unit test class for functions used to extract orgaisations mentioned in a pdf file.

    Test methods:
    - test_collect_orgs: tests the function collect organisations that collects organisations that are mentioned in text
    - test_decide_org: tests the function decide_orgs that defines a decision tree to determine if a mentioned organisations
      is likely a true organisation
    - test_match_anbis: Tests the match anbis function that tries to match found organisations with info about known anbis
    - test_apply_matching: tests the apply_matching function that tries to match a name with values in
      one of two provided columns in a dataframe
    """

    def test_collect_orgs(self):
        """Unit test for the collect_orgs function.

        Function that tests the collect_orgs function that collects organisations that are mentioned in a text using stanza NER
        with a number of postprocessing steps. One test case is applied, that tests if the expected organisations are
        returned from a test file.

        Raises:
            AssertionError: If any of the assert statement fails, indicating incorrect return values.
        """
        orgs = collect_orgs(infile, nlp)
        self.assertEqual(orgs, ['Bedrijf2', 'Bedrijf3'])

    def test_decide_org(self):
        """Unit test for the function decide_org.

        Function that tests the function decide_orgs that defines a decision tree to determine if a mentioned organisations
        is likely a true organisation.

        Nine assertion tests are defined that test for various test names, if the expected result is returned
        for different percentage the organisation was found as org, and the total number of times the organisaiont was
        found in the text.

        Returns:
            AssertionError: If any of tests does not returns the expected retult.
        """
        # initalisations
        org = 'Bedrijf'
        org_pp = np.array(['Bedrijf'])
        org_c = np.array(['Bedrijf'])

        # Test case 1
        pco = ((50, 6), (50, 6))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertTrue(final)

        # Test case 2
        pco = ((50, 3), (50, 3))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertFalse(final)

        # Test case 3
        pco = ((70, 3), (70, 3))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertTrue(final)

        # Test case 4
        pco = ((100, 1), (100, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertEqual(final, 'maybe')

        # Test case 5
        pco = ((0, 1), (100, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertEqual(final, 'maybe')

        # Test case 6
        pco = ((100, 1), (0, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertEqual(final, 'no')

        # Test case 7
        pco = ((0, 0), (0, 0))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertFalse(final)

        # Test case 8
        pco = ((0, 1), (0, 1))
        org = 'Stichting Huppeldepup'
        org_pp = ['Stichting Huppeldepup']
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertEqual(final, 'maybe')

        # Test case 9
        pco = ((0, 0), (0, 0))
        org = 'Stichting Huppeldepup'
        org_pp = ['Stichting Huppeldepup']
        org_c = np.array(['Bedrijf'])
        final = decide_org(org, pco, org_pp, org_c, nlp)
        self.assertFalse(final)

    def test_match_anbis(self):
        """Unit test for the match_anbis function.

        Tests the match_anbis function that tries to match found organisations with info about known anbis.
        There is one test case that uses a test_anbis.csv file and a test.pdf file (from which a pd dataframe is created)
        and asserts whether the returned DataFrame matches the expected df.

        Returns:
            AssertionError: If the returned df does not match the expected df.
        """
        anbis_file = os.path.join(os.path.join(os.getcwd(), 'tests'), 'test_anbis.csv')
        df_in = pd.DataFrame({'Input_file': ['test.pdf'],
                              'mentioned_organization': ['B1 b.v.'],
                              'n_mentions': [1]})
        df_out = match_anbis(df_in, anbis_file)
        e_out = pd.DataFrame({'Input_file': ['test.pdf'],
                              'mentioned_organization': ['B1 b.v.'],
                              'n_mentions': [1],
                              'matched_anbi': ['Stichting B1 b.v.'],
                              'rsin': ['11'],
                              'currentStatutoryName': ['Bedrijf1'],
                              'shortBusinessName': ['Stichting B1 b.v.']})
        pd.testing.assert_frame_equal(df_out, e_out)

    def test_apply_matching(self):
        """Unit test for the apply_matching function.

        This function tests the apply_matching function that tries to match a name with values in
        one of two provided columns in a dataframe.

        There are three test cases using two different dataframes, expecting tree outcomes; a direct match,
        a False match, and a match requirering 'stichting' to be added to the name.
        """
        # Test case 1
        df = pd.DataFrame({'currentStatutoryName': ['Bedrijf1', 'Bedrijf2'],
                           'shortBusinessName': ['B1 b.v.', 'B2 b.v.']})
        m = 'Bedrijf2'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = 'Bedrijf2'

        # Test case 2
        self.assertEqual(o_m, e_m)
        m = 'Bedrijf'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = None
        self.assertEqual(o_m, e_m)

        # Test case 3
        df = pd.DataFrame({'currentStatutoryName': ['Bedrijf1', 'Bedrijf2'],
                           'shortBusinessName': ['Stichting B1 b.v.', 'B2 b.v.']})
        m = 'B1 b.v.'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = 'Stichting B1 b.v.'
        self.assertEqual(o_m, e_m)
