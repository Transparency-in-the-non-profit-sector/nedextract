"""The file contains functions used to test the functions in orgs_checks.

Functions:
- test_keyword_check
- test_check_single_orgs
- test_part_of_other
- test_individual_org_check
- test_pco
- test_strip_function_of_entity
- test_count_number_of_mentions
"""
import unittest
import numpy as np
import stanza
from auto_extract.orgs_checks import check_single_orgs
from auto_extract.orgs_checks import count_number_of_mentions
from auto_extract.orgs_checks import individual_org_check
from auto_extract.orgs_checks import keyword_check
from auto_extract.orgs_checks import part_of_other
from auto_extract.orgs_checks import percentage_considered_org
from auto_extract.orgs_checks import strip_function_of_entity


stanza.download('nl')
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
doc = nlp(text)

class TestsOrgs_Checks(unittest.TestCase):
    """Unit test class for functions used to extract names and functions of people mentioned in a pdf file.
    
    Test methods:
    - test_keyword_check: tests the keyword_check function that determines if an org is likely to be or not be an organisation
      based on keywords
    - test_check_single_orgs: tests the check_single_orgs function that appends an org to an input list if it 
      passes the keyword check and is not part of other org
    - test_part_of_other: tests the function part_of_other that checks if a member of
      orgs is part of the org string.
    - test_individual_org_check: tests the individual_org_check that checks if an potential ORG is considered and ORG
      if just that name is analysed by Stanza NER.
    - test_pco: tests the percentage_consired_org function that identifies the percentage of cases for which 
      a an organisation was identified by NER as organisation within the text
    - test_strip_function_of_entity: tests the strip_function_of_entity function that removes any persons work role
      of the name of a potential org.
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


    def test_individual_org_check(self):
        """Unit test for the function individual_org_check
        
        This function tests the individual_org_check that checks if an potential ORG is considered and ORG
        if just that name is analysed by Stanza NER. Contains one test case. 

        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        org = 'Stichting Huppeldepup'
        is_org = individual_org_check(org, nlp)
        assert(is_org)


    def test_pco(self):
        """Unit test for the percentage_considered_org function.

        Tests the percentage_considered_org function that identifies the percentage of cases for which 
        a an organisation was identified by NER as organisation within the text. Contains three test cases
        asserting the percentage of cases and total number of mentioned for different input terms using the 
        test doc.

        Raises:
            AssertionError: If any of the assertion statements fails, indicating an incorrect return value.
        """
        # Test case 1
        org = 'Bedrijf'
        orgs = np.array(['Bedrijf'])
        counts = np.array([7])
        pco = percentage_considered_org(doc, org, orgs, counts)
        assert(pco[0] == 100.)
        assert(pco[1] == 7)

        # Test case 2
        orgs = np.array(['Bedrij'])
        pco = percentage_considered_org(doc, org, orgs, counts)
        assert(pco[0] == 0.)
        assert(pco[1] == 7)

        # Test case 3
        counts = np.array([0])
        org = 'Bedrijfsk'
        orgs = np.array(['Bedrijfsk'])
        pco = percentage_considered_org(doc, org, orgs, counts)
        assert(pco[0] == -10.)
        assert(pco[1] == 0)


    def test_strip_function_of_entity(self):
        """Unit test for the strip_function_of_entity function.

        This function tests the strip_function_of_entity function that removes any persons work role
        of the name of a potential org.

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