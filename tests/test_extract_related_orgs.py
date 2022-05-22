import os
import numpy as np
import stanza
from auto_extract.extract_related_orgs import check_single_orgs
from auto_extract.extract_related_orgs import collect_orgs
from auto_extract.extract_related_orgs import decide_org
from auto_extract.extract_related_orgs import keyword_check
from auto_extract.extract_related_orgs import part_of_other
from auto_extract.extract_related_orgs import percentage_considered_org
from auto_extract.extract_related_orgs import single_org_check
from auto_extract.preprocessing import preprocess_pdf


stanza.download('nl')
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
doc = nlp(text)


def test_collect_orgs():
    orgs = collect_orgs(infile, nlp)
    assert(orgs == ['Bedrijf2', 'Bedrijf3'])


def test_decide_org():
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


def test_keyword_check():
    org = 'Huppeldepup B.V'
    final = False
    kwc = keyword_check(final, org)
    assert(kwc)
    org = 'Ministerie'
    final = False
    kwc = keyword_check(final, org)
    assert(kwc is False)
    org = 'Hogeschool'
    final = False
    kwc = keyword_check(final, org)
    assert(kwc is False)


def test_check_single_orgs():
    org = 'Stichting Huppeldepup'
    true_orgs = []
    doc_c = 'Hij werkt bij Stichting Huppeldepup'
    to = check_single_orgs(org, true_orgs, doc_c)
    e_to = ['Stichting Huppeldepup']
    assert(to == e_to)


def test_part_of_other():
    orgs = ['Bedrijf']
    org = 'Bedrijf bla'
    is_part = part_of_other(orgs, org, doc)
    assert(is_part)


def test_single_org_check():
    org = 'Stichting Huppeldepup'
    is_org = single_org_check(org, nlp)
    assert(is_org)


def test_pco():
    org = 'Bedrijf'
    orgs = np.array(['Bedrijf'])
    counts = np.array([7])
    pco = percentage_considered_org(doc, org, orgs, counts)
    assert(pco[0] == 100.)
    assert(pco[1] == 7)
    orgs = np.array(['Bedrij'])
    pco = percentage_considered_org(doc, org, orgs, counts)
    assert(pco[0] == 0.)
    assert(pco[1] == 7)
    counts = np.array([0])
    org = 'Bedrijfsk'
    orgs = np.array(['Bedrijfsk'])
    pco = percentage_considered_org(doc, org, orgs, counts)
    assert(pco[0] == -10.)
    assert(pco[1] == 0)
