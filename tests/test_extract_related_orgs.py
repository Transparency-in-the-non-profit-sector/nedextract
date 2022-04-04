import os
import numpy as np
import stanza
from auto_extract.extract_related_orgs import classify_org_type
from auto_extract.extract_related_orgs import classify_relation_type
from auto_extract.extract_related_orgs import count_orgs
from auto_extract.extract_related_orgs import extract_orgs
from auto_extract.preprocessing import preprocess_pdf


indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)
organizations = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "ORG"])


def test_count_orgs():
    text = ('De naam Bedrijf komt 4 keer voor in deze tekst. Bedrijf is een bedrijf.' +
            'Er werken mensen bij Bedrijf, Bedrijf.')
    org = 'Bedrijf'
    assert(count_orgs(text, org) == 4)


def test_classify_relation_type():
    assert(classify_relation_type() == 'none')


def test_classify_org_type():
    assert(classify_org_type() == 'none')


def test_extract_orgs():
    expected = np.array(['Bedrijf - 11 - none - none', 'Bedrijf2 - 1 - none - none'])
    result = extract_orgs(text, ['Bedrijf', 'Bedrijf2'])
    assert(isinstance(result, np.ndarray))
    assert(np.array_equal(expected, result))
