"""The file contains functions used to test the functions in exract_related orgs.

Functions:
- test_collect_orgs
- test_decide_org
- test_match_anbis
- test_apply_matching
"""

import unittest
import os
import numpy as np
import pandas as pd
import stanza
from auto_extract.extract_related_orgs import collect_orgs
from auto_extract.extract_related_orgs import decide_org
from auto_extract.extract_related_orgs import apply_matching
from auto_extract.extract_related_orgs import match_anbis
from auto_extract.preprocessing import preprocess_pdf

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
    - test_decide_org
    - test_match_anbis
    - test_apply_matching
    """
    def test_collect_orgs(self):
        """Unit test for the collect_orgs function.
        
        The collect_orgs function collects organisations that are mentioned in a text using stanza NER with a number of 
        postprocessing steps. One test case is applied, that tests if the expected organisations are return from a test file.
        
        Raises:
            AssertionError: If any of the assert statement fails, indicating incorrect return values.
        """
        orgs = collect_orgs(infile, nlp)
        self.assertEqual(orgs, ['Bedrijf2', 'Bedrijf3'])


    def test_decide_org(self):
        org = 'Bedrijf'
        pco = ((50, 6), (50, 6))
        org_pp = np.array(['Bedrijf'])
        org_c = np.array(['Bedrijf'])
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final)
        pco = ((50, 3), (50, 3))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final is False)
        pco = ((70, 3), (70, 3))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(True)
        pco = ((100, 1), (100, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final == 'maybe')
        pco = ((0, 1), (100, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final == 'maybe')
        pco = ((100, 1), (0, 1))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final == 'no')
        pco = ((0, 0), (0, 0))
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final is False)
        pco = ((0, 1), (0, 1))
        org = 'Stichting Huppeldepup'
        org_pp = ['Stichting Huppeldepup']
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final == 'maybe')
        pco = ((0, 0), (0, 0))
        org = 'Stichting Huppeldepup'
        org_pp = ['Stichting Huppeldepup']
        final = decide_org(org, pco, org_pp, org_c, nlp)
        assert(final == 'maybe')


    def test_apply_matching(self):
        df = pd.DataFrame({'currentStatutoryName': ['Bedrijf1', 'Bedrijf2'],
                        'shortBusinessName': ['B1 b.v.', 'B2 b.v.']})
        m = 'Bedrijf2'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = 'Bedrijf2'
        assert(o_m == e_m)
        m = 'Bedrijf'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = None
        assert(o_m == e_m)
        df = pd.DataFrame({'currentStatutoryName': ['Bedrijf1', 'Bedrijf2'],
                        'shortBusinessName': ['Stichting B1 b.v.', 'B2 b.v.']})
        m = 'B1 b.v.'
        o_m = apply_matching(df, m, 'currentStatutoryName', 'shortBusinessName')
        e_m = 'Stichting B1 b.v.'
        assert(o_m == e_m)

    def test_match_anbis(self):
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
                            'currentStatutoryName':['Bedrijf1'],
                            'shortBusinessName':['Stichting B1 b.v.']})
        pd.testing.assert_frame_equal(df_out, e_out)
