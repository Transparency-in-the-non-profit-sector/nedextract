import os
import numpy as np
import pandas as pd
import stanza
from auto_extract.extract_related_orgs import apply_matching
from auto_extract.extract_related_orgs import check_single_orgs
from auto_extract.extract_related_orgs import collect_orgs
from auto_extract.extract_related_orgs import count_number_of_mentions
from auto_extract.extract_related_orgs import decide_org
from auto_extract.extract_related_orgs import keyword_check
from auto_extract.extract_related_orgs import match_anbis
from auto_extract.extract_related_orgs import part_of_other
from auto_extract.extract_related_orgs import percentage_considered_org
from auto_extract.extract_related_orgs import single_org_check
from auto_extract.extract_related_orgs import strip_function_of_entity
from auto_extract.preprocessing import preprocess_pdf


stanza.download('nl')
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
doc = nlp(text)


def test_apply_matching():
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

def test_match_anbis():
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
