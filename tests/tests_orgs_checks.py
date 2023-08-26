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
import os
import unittest
import numpy as np
import stanza
from nedextract.preprocessing import preprocess_pdf
from nedextract.utils.orgs_checks import OrganisationExtraction


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
    - test_count_number_of_mentions: Tests the count_number_of_mentions function that the number of mentions of org in the text,
      taking into account word boundaries
    """

    def test_keyword_check(self):
        """Unit test function for the keyword_check function.

        This function tests the keyword_check function that determines if an org is likely to be or not be an organisation
        based on keywords.

        This function comtains three test cases, each asserting the output for a different input organisation.

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        extraction = OrganisationExtraction()

        # Test case 1
        extraction.org = 'Huppeldepup B.V'
        extraction.final = False
        kwc = extraction.keyword_check()
        self.assertTrue(kwc)

        # Test case 2
        extraction.org = 'Ministerie'
        extraction.final = False
        kwc = extraction.keyword_check()
        self.assertFalse(kwc)

        # Test case 3
        extraction.org = 'Hogeschool'
        extraction.final = False
        kwc = extraction.keyword_check()
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
        to = OrganisationExtraction(org=org, true_orgs=true_orgs, doc=doc_c).check_single_orgs()
        e_to = ['Stichting Huppeldepup']
        self.assertEqual(to, e_to)

    def test_part_of_other(self):
        """Unit test for the function part_of_other.

        This function tests the function part_of_other that checks if a member of
        orgs is part of the org string. Contains one test case.

        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        orgs = ['Bedrijf']
        org = 'Bedrijf bla'
        is_part = OrganisationExtraction().part_of_other(orgs=[orgs], org=org, doc=doc)
        self.assertTrue(is_part)

    def test_individual_org_check(self):
        """Unit test for the function individual_org_check.

        This function tests the individual_org_check that checks if an potential ORG is considered and ORG
        if just that name is analysed by Stanza NER. Contains one test case.

        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        org = 'Stichting Huppeldepup'
        is_org = OrganisationExtraction(org=org, nlp=nlp).individual_org_check()
        self.assertTrue(is_org)

    def test_pco(self):
        """Unit test for the percentage_considered_org function.

        Tests the percentage_considered_org function that identifies the percentage of cases for which
        a an organisation was identified by NER as organisation within the text. Contains three test cases
        asserting the percentage of cases and total number of mentioned for different input terms using the
        test doc.

        Raises:
            AssertionError: If any of the assertion statements fails, indicating an incorrect return value.
        """
        extraction = OrganisationExtraction(doc=doc)
        # Test case 1
        extraction.org = 'Bedrijf'
        extraction.orgs = (np.array(['Bedrijf']), np.array([7]))
        pco = extraction.percentage_considered_org()
        self.assertEqual(pco[0], 100.)
        self.assertEqual(pco[1], 7)

        # Test case 2
        extraction.orgs = (np.array(['Bedrij']), np.array([7]))
        pco = extraction.percentage_considered_org()
        self.assertEqual(pco[0], 0.)
        self.assertEqual(pco[1], 7)

        # Test case 3
        extraction.org = 'Bedrijfsk'
        extraction.orgs = (np.array(['Bedrijfsk']), np.array([0]))
        pco = extraction.percentage_considered_org()
        self.assertEqual(pco[0], -10.)
        self.assertEqual(pco[1], 0)

    def test_strip_function_of_entity(self):
        """Unit test for the strip_function_of_entity function.

        This function tests the strip_function_of_entity function that removes any persons work role
        of the name of a potential org.

        Raises:
            AssertionError: If the assert statement fails, indicating an incorrect return value.
        """
        org = "Lid van de Raad van Advies bij Bedrijfsnaam b.v."
        e_org = "Bedrijfsnaam b.v."
        o_org = OrganisationExtraction(org=org).strip_function_of_entity()
        self.assertEqual(e_org, o_org)

    def test_count_number_of_mentions(self):
        """Unit test for the count_number_of_mentions.

        Tests the count_number_of_mentions function that the number of mentions of org in the text,
        taking into account word boundaries. Contains two test cases, same org name, different word boundaries,
        applied to the test doc.

        Raises:
            AssertionError: If any of the assert statements fails, indicating an incorrect return value.
        """
        extraction = OrganisationExtraction(doc=doc)
        extraction.org = 'Bedrijf'
        n = extraction.count_number_of_mentions()
        self.assertEqual(n, 7)
        extraction.org = 'Bedrijf-'
        n = extraction.count_number_of_mentions()
        self.assertEqual(n, 0)
