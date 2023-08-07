import numpy as np
from auto_extract.orgs_checks import check_single_orgs
from auto_extract.orgs_checks import collect_orgs
from auto_extract.orgs_checks import count_number_of_mentions
from auto_extract.orgs_checks import decide_org
from auto_extract.orgs_checks import keyword_check
from auto_extract.orgs_checks import part_of_other
from auto_extract.orgs_checks import percentage_considered_org
from auto_extract.orgs_checks import single_org_check
from auto_extract.orgs_checks import strip_function_of_entity


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


def test_collect_orgs(unittest.TestCase):
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


def test_strip_function_of_entity():
    org = "Lid van de Raad van Advies bij Bedrijfsnaam b.v."
    e_org = "Bedrijfsnaam b.v."
    o_org = strip_function_of_entity(org)
    assert(e_org == o_org)


def test_count_number_of_mentions():
    org = 'Bedrijf'
    n = count_number_of_mentions(doc, org)
    assert(n == 7)
    org = 'Bedrijf-'
    n = count_number_of_mentions(doc, org)
    assert(n == 0)