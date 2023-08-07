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
import unittest
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
    - test_keyword_check: tests the keyword_check function that determines if an org is likely to be or not be an organisation
        based on keywords
    - test_check_single_orgs: tests the check_single_orgs function that appends an org to an input list if it 
        passes the keyword check and is not part of other org
    - test_part_of_other: tests the function part_of_other that checks if a member of
        orgs is part of the org string.
    - test_single_org_check:
    - test_pco:
    - test_strip_function_of_entity:
    - test_count_number_of_mentions:
    """
    def test_keyword_check(self):
        """Unit test function for the keyword_check function.
        
        This function tests the keyword_check function that determines if an org is likely to be or not be an organisation
        based on keywords.

        This function comtains three test cases, each asserting the output for a different input organisation.

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        # Test case 1
        org = 'Huppeldepup B.V'
        final = False
        kwc = keyword_check(final, org)
        self.assertTrue(kwc)

        # Test case 2
        org = 'Ministerie'
        final = False
        kwc = keyword_check(final, org)
        self.assertFalse(kwc)

        # Test case 3
        org = 'Hogeschool'
        final = False
        kwc = keyword_check(final, org)
        self.assertFalse(kwc)

    def test_check_single_orgs(self):
        """Unit tes for the function check_single_orgs.
        
        This function tests the check_single_orgs function that appends an org to an input list if it 
        passes the keyword check and is not part of other org. Contains one test case.
        
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        org = 'Stichting Huppeldepup'
        true_orgs = []
        doc_c = 'Hij werkt bij Stichting Huppeldepup'
        to = check_single_orgs(org, true_orgs, doc_c)
        e_to = ['Stichting Huppeldepup']
        assert(to == e_to)


    def test_part_of_other(self):
        """Unit test for the function part_of_other.
        
        This function tests the function part_of_other that checks if a member of
        orgs is part of the org string. Contains one test case.
        
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        orgs = ['Bedrijf']
        org = 'Bedrijf bla'
        is_part = part_of_other(orgs, org, doc)
        assert(is_part)


    def test_single_org_check(self):
        """
        
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        org = 'Stichting Huppeldepup'
        is_org = single_org_check(org, nlp)
        assert(is_org)


    def test_pco(self):
        """
        
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.

        """
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
        """
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
"""
        org = "Lid van de Raad van Advies bij Bedrijfsnaam b.v."
        e_org = "Bedrijfsnaam b.v."
        o_org = strip_function_of_entity(org)
        assert(e_org == o_org)


    def test_count_number_of_mentions(self):
        """
        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
"""
        org = 'Bedrijf'
        n = count_number_of_mentions(doc, org)
        assert(n == 7)
        org = 'Bedrijf-'
        n = count_number_of_mentions(doc, org)
        assert(n == 0)