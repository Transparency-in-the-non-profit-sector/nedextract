"""The file contains functions used to test the functions in orgs_checks.

Functions:
- test_keyword_check
- test_check_single_orgs
- test_part_of_other
- test_single_org_check
- test_pco
- test_strip_function_of_entity
- test_count_number_of_mentions
"""

import numpy as np
from auto_extract.orgs_checks import check_single_orgs
from auto_extract.orgs_checks import count_number_of_mentions
from auto_extract.orgs_checks import keyword_check
from auto_extract.orgs_checks import part_of_other
from auto_extract.orgs_checks import percentage_considered_org
from auto_extract.orgs_checks import single_org_check
from auto_extract.orgs_checks import strip_function_of_entity


class TestsOrgs_Checks(unittest.TestCase):
    """Unit test class for functions used to extract names and functions of people mentioned in a pdf file.
    
    Test methods:
    - test_keyword_check: 
    - test_check_single_orgs
    - test_part_of_other
    - test_single_org_check
    - test_pco
    - test_strip_function_of_entity
    - test_count_number_of_mentions
    """


    def test_keyword_check(self):
        """Unit test function for the """
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

    def test_check_single_orgs(self):
        org = 'Stichting Huppeldepup'
        true_orgs = []
        doc_c = 'Hij werkt bij Stichting Huppeldepup'
        to = check_single_orgs(org, true_orgs, doc_c)
        e_to = ['Stichting Huppeldepup']
        assert(to == e_to)


    def test_part_of_other(self):
        orgs = ['Bedrijf']
        org = 'Bedrijf bla'
        is_part = part_of_other(orgs, org, doc)
        assert(is_part)


    def test_single_org_check(self):
        org = 'Stichting Huppeldepup'
        is_org = single_org_check(org, nlp)
        assert(is_org)


    def test_pco(self):
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


    def test_strip_function_of_entity(self):
        org = "Lid van de Raad van Advies bij Bedrijfsnaam b.v."
        e_org = "Bedrijfsnaam b.v."
        o_org = strip_function_of_entity(org)
        assert(e_org == o_org)


    def test_count_number_of_mentions(self):
        org = 'Bedrijf'
        n = count_number_of_mentions(doc, org)
        assert(n == 7)
        org = 'Bedrijf-'
        n = count_number_of_mentions(doc, org)
        assert(n == 0)