"""Unit tests for functions in class NameAnalysis."""
import unittest
from nedextract.utils.nameanalysis import NameAnalysis


# input names for NameAnalysis class
pnames = ['Dr. Jane Doe', 'Jane Doe', 'J. Doe', 'Jane Elaine Doe',
          'J.E. Doe', 'Jane White', 'William Doe', 'Jane']
NameAnalysis = NameAnalysis(pnames)


class TestExtractPersons(unittest.TestCase):
    """Unit test class for functions used to extract names and functions of people mentioned in a pdf file.

    Test methods:
        - test_abbreviate: tests the 'abbreviate' function to abbreviate names
        - test_get_tsr: tests the 'get_tsr' function that determines the token set ratio for two names and the required score
        - test_strip_names_from_title: tests the 'strip_names_from_title' function that removes titles from names.
        - test_find_duplicate_persons: tests the 'find_duplicate_persons' function that tests if names in a list are very
          similar.
        - test_surrounding_words: tests the 'surrounding_words' function that dermines the words surrounding a given name in a
          text.
        - test_count_occurrence: tests the 'count_occurrence' function that counts for a list of serach words the occurences in
          a text.
    """

    def test_abbreviate(self):
        """Unit test function for the 'abbreviate' function.

        This function tests the 'abbreviate' function, which abbreviates the first 'n_ab' terms in a 'name',
        excluding tussenvoegsels, and as long as it is not the last term in a name.

        Test cases:
        1. Case where 'name' is 'Jane Doe' and 'n_ab' is 2. The expected output is 'J Doe '.
        2. Case where 'name' is 'Jan de Wit' and 'n_ab' is 2. The expected output is 'J de Wit '.
        3. Case where 'name' is 'Jan Piet de Wit' and 'n_ab' is 2. The expected output is 'J P de Wit '.
        4. Case where 'name' is 'Jan Piet van der Wit' and 'n_ab' is 2. The expected output is 'J P van der Wit '.
        5. Case where 'name' is 'Jan Piet van der Wit' and 'n_ab' is 3. The expected output is 'J P van der Wit '.

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        name = 'Jane Doe'
        name2 = 'Jan de Wit'
        name3 = 'Jan Piet de Wit'
        name4 = 'Jan Piet van der Wit'
        self.assertEqual(NameAnalysis.abbreviate(name, 2), 'J Doe ')
        self.assertEqual(NameAnalysis.abbreviate(name2, 2), 'J de Wit ')
        self.assertEqual(NameAnalysis.abbreviate(name3, 2), 'J P de Wit ')
        self.assertEqual(NameAnalysis.abbreviate(name4, 2), 'J P van der Wit ')
        self.assertEqual(NameAnalysis.abbreviate(name4, 3), 'J P van der Wit ')

    def test_get_tsr(self):
        """Unit test function for the 'get_tsr' function.

        This function tests the get_tsr function that determines the token set ratio
        for two input names and the required score that is determed based on the `form` of the to test names

        There are five test cases specified, each expecting a matching tsr score, but different
        required scores.

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        # Test case 1
        tsr1, rs1 = NameAnalysis.get_tsr('Jane Doe', 'Jane Doe')
        self.assertEqual(tsr1, 100)
        self.assertEqual(rs1, 90)
        # Test cse 2
        tsr2, rs2 = NameAnalysis.get_tsr('Jane Doe', 'Jane')
        self.assertEqual(tsr2, 100)
        self.assertEqual(rs2, 100)
        # Test case 3
        tsr3, rs3 = NameAnalysis.get_tsr('J. Doe', 'J.P. Doe')
        self.assertEqual(tsr3, 100)
        self.assertEqual(rs3, 90)
        # Test case 4
        tsr4, rs4 = NameAnalysis.get_tsr('J. Doe', 'Jane Doe')
        self.assertEqual(tsr4, 100)
        self.assertEqual(rs4, 95)
        # Test case 5
        tsr5, rs5 = NameAnalysis.get_tsr('Jane Doe', 'J. Doe')
        self.assertEqual(tsr5, 100)
        self.assertEqual(rs5, 95)

    def test_strip_names_from_title(self):
        """Unit test for the 'strip_names_from_titles' funciton.

        This function tests the 'strip_names_from_title' function that removes titles from a list of names.
        If the stripping procedure leaves the remainder of a name to consist of only one letter,
        this original name is added to a list of names to be removed.

        There is one test case input list, that contains three different case names with different forms of
        expected outputs.

        Raises:
            AssertionError: If any of the assert statements fail, indicating incorrect return values.
        """
        inp = ['Prof. Dr. Jane Doe', 'John Doe, PhD', 'Dr. J.']
        expected, expected_removed = ['  jane doe', 'john doe, '], ['Dr. J.']
        out, out_r = NameAnalysis.strip_names_from_title(inp)
        self.assertEqual(out, expected)
        self.assertEqual(out_r, expected_removed)

    def test_find_duplicate_persons(self):
        """Unit test for the 'find_duplicate_names' function.

        This function tests the 'find_duplicate_names' function that tests if some of the names
        in a list are very similar.

        There is one test case, consisting of one list of names that is expected to return three cases of found
        name similarities.

        Raises:
            AssertionError: If the returned variable is not a list, or if it does not matchc the expected
            return values.
        """
        outnames = NameAnalysis.find_duplicate_persons()
        expected = [['Jane Elaine Doe', 'Dr. Jane Doe', 'Jane Doe', 'J.E. Doe', 'J. Doe'],
                    ['Jane White'], ['William Doe']]
        self.assertTrue(isinstance(outnames, list))
        self.assertEqual(outnames, expected)
