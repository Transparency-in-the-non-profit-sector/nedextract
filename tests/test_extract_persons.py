"""This module contains unit tests for the functions in extract_persons."""
import os
import unittest
import numpy as np
import stanza
from nedextract.extract_persons import append_p_position
from nedextract.extract_persons import array_p_position
from nedextract.extract_persons import check_bestuur
from nedextract.extract_persons import check_rvt
from nedextract.extract_persons import director_check
from nedextract.extract_persons import extract_persons
from nedextract.extract_persons import identify_potential_people
from nedextract.preprocessing import preprocess_pdf


# Download stanza
stanza.download('nl')

# Definitions for test case 1
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)

# expected value for test_extract_persons test case 1
e_bp = np.array(['Anna de Wit - rvt - vice-voorzitter',
                 'Dirkje Rooden - bestuur - lid',
                 'Eduard van Grijs - bestuur - ',
                 'Ferdinand de Blauw - bestuur - ',
                 'Gerard Roze - kascommissie - voorzitter',
                 'Hendrik Doe - rvt - voorzitter',
                 'Hendrik Groen - kascommissie - ',
                 'Jane Doe - directeur - directeur',
                 'Cornelis Geel - rvt - lid',
                 'Isaak Paars - ledenraad - voorzitter',
                 'Jan van Oranje - ledenraad - penningmeester',
                 'Karel - ledenraad - lid',
                 'Lodewijk - ledenraad - ',
                 'Maria - ledenraad - ',
                 'Mohammed El Idrissi - controlecommissie - ',
                 'Saïda Benali - controlecommissie - ',
                 'Bernard Zwartjes - rvt - '])

# Definitions for test case 2
all_persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
infile2 = os.path.join(indir, 'test_report2.pdf')
text2 = preprocess_pdf(infile2, ' ')
doc2 = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text2)
all_persons2 = np.unique([f'{ent.text}' for ent in doc2.ents if ent.type == "PER"])


class TestExtractPersons(unittest.TestCase):
    """Unit test class for functions used to extract names and functions of people mentioned in a pdf file.

    Test methods:
        - test_identify_potential_people: tests the 'identify_potential_people' function that analyses text to find names of
          people that may have one of the predifined jobs.
        - test_extract_persons: tests the 'extract_persons' function that extracts ambassadors and board members from a text
          using a rule-based method.
        - test_director_check: tests the director_check function that performs checks for potential directors and update their
          positions if necessary
        - test_check_rvt: tests the check_rvt function that determines whether potential rvt members can be considered
          try=ue rvt memebers.
        - test_check_bestuur: tests the check_bestuur function that determines whether potential bestuur members can be
          considered true bestuur memebers.
        - test_append_p_position: tests the 'append_p_position' function that append a person's name to their main position in
          the list of positions.
        - test_array_p_position: tests the 'array_p_position' function that returns an array of names taken from a sublist of
          the list p_position.
    """

    def test_identify_potential_people(self):
        """Unit test for the function 'identify_potential_people'.

        This function tests the 'identify_potential_people' function hat analyses text to find names of
        people that may have one of the predifined jobs.

        Raises:
            AssertionError: if the returned parameter is not a list, or if it does not match the expected value

        """
        people = identify_potential_people(doc, all_persons)
        expected = [['Anna de Wit', 'A.B. de Wit'], ['Bernard Zwartjes'],
                    ['Cornelis Geel'], ['Dirkje Rood'], ['E. van Grijs', 'Eduard van Grijs'],
                    ['F. de Blauw', 'Ferdinand de Blauw'], ['G. Roze', 'Gerard Roze'],
                    ['H. Doe', 'Hendrik Doe'], ['Hendrik Groen', 'Mr. H. Groen'],
                    ['J. Doe', 'Jane Doe'], ['Isaak Paars'], ['Jan van Oranje'], ['Karel'],
                    ['Lodewijk'], ['Maria']]
        self.assertTrue(isinstance(people, list))
        self.assertEqual(people.sort(), expected.sort())

    def test_extract_persons(self):
        """Unit test for the function 'extract_persons'.

        This function tests the 'extract_persons' function that extracts ambassadors and board members from a text
        using a rule-based method.

        There are 2 tests. The first test uses the first test pdf document, and each of the eight checks asserts if
        one of the 8 returned function categories, contain the expected names.
        The second test uses a test docuemnt 2 to check if the additonal director conditions work as expected
        """
        # Test case 1
        e_a = np.array(['Sarah', 'Thomas'])
        e_r = np.array(['Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes'])
        e_b = np.array(['Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw'])
        e_l = np.array(['Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria'])
        e_k = np.array(['Gerard Roze', 'Hendrik Groen'])
        e_c = np.array(['Mohammed El Idrissi', 'Saïda Benali'])
        a, b_p, d, r, b, l, k, c = extract_persons(doc, all_persons)
        self.assertTrue(np.array_equal(e_a, a))
        self.assertTrue(np.array_equal(e_bp, b_p))
        self.assertTrue(np.array_equal(np.array(['Jane Doe']), d))
        self.assertTrue(np.array_equal(e_r, r))
        self.assertTrue(np.array_equal(e_b, b))
        self.assertTrue(np.array_equal(e_l, l))
        self.assertTrue(np.array_equal(e_k, k))
        self.assertTrue(np.array_equal(e_c, c))

        # Test case 2
        d = extract_persons(doc2, all_persons2)[2]
        self.assertTrue(np.array_equal(np.array(['Jane Doe']), d))

    def test_director_check(self):
        """Unit test for the function 'director_check'.

        This function tests the director_check function that performs checks for potential directors and update their
        positions if necessary.

        There are 8 test cases:
        1-6. 6 pot_director
            - ft=2, max ft pot_director = 6, backup main is rvt, subf is voorzitter.
            - ft=3, backup main = ambassador, sub = penningmeester
            - ft=3, backup main = bestuur, sub = directeur
            - ft=6, backup main = rvt, sub=''
            - ft=5, backup main = ledenraad, sub=lid
            - ft=6, backup main = rvt, subf = directeur
        7-8. 2 pot_director
            - ft=1, backup main = rvt, subf = directeur
            - ft=3, backup main = bestuur, subf = voorzitter

        pot_director has the form:
        pot_director = name, sub_cat, ft_director, backup_main_cat, backup_sub_cat, fts_bestuur, fts_rvt

        """
        # Test cases 1-4
        pot_director = np.array([['Jane Doe', 'voorzitter', 2, 'rvt', 'voorzitter', 1, 1],
                                 ['Pietje de Wit', 'voorzitter', 3, 'ambassadeur', 'voorzitter', 1, 1],
                                 ['Louwie kats', 'directeur', 3, 'bestuur', '', 5, 8],
                                 ['Bert de hond', 'lid', 6, 'rvt', 'lid', 3, 5],
                                 ['Willem Visser', 'lid', 5, 'ledenraad', 'lid', 1, 2],
                                 ['Dirkje El Morabit', 'directeur', 6, 'rvt', '', 2, 1]
                                 ], dtype=object)

        b_position = np.array(['Anna Zwart - rvt - vicevoorzitter',
                               'Hanna Groen - bestuur - penningmeester',
                               'Jane Doe - directeur - voorzitter',
                               'Pietje de Wit - directeur - voorzitter',
                               'Louwie kats - directeur - directeur',
                               'Bert de hond - directeur - lid',
                               'Willem Visser - directeur - lid',
                               'Dirkje El Morabit - directeur - directeur'])
        pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3]]
        pot_bestuur = [['Hanna Groen', 'penningmeester', 2]]
        p_position = [['directeur'], ['bestuur', 'Hanna Groen'], ['rvt', 'Anna Zwart'], ['ledenraad'], ['ambassadeur']]
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)

        e_b = np.array(['Anna Zwart - rvt - vicevoorzitter',
                        'Hanna Groen - bestuur - penningmeester',
                        'Dirkje El Morabit - directeur - directeur',
                        'Jane Doe - rvt - voorzitter',
                        'Louwie kats - bestuur - ',
                        'Bert de hond - rvt - lid',
                        'Willem Visser - ledenraad - lid'
                        ])
        e_pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3], ['Jane Doe', 'voorzitter', 1], ['Bert de hond', 'lid', 5]]
        e_pot_b = [['Hanna Groen', 'penningmeester', 2], ['Louwie kats', '', 5]]
        e_p_p = [['directeur', 'Dirkje El Morabit'], ['bestuur', 'Hanna Groen'],
                 ['rvt', 'Anna Zwart'], ['ledenraad', 'Willem Visser'], ['ambassadeur', 'Pietje de Wit']]

        self.assertTrue(np.array_equal(a, e_b))
        self.assertEqual(b, e_pot_rvt)
        self.assertEqual(c, e_pot_b)
        self.assertEqual(d, e_p_p)

        # Test case 5-8
        pot_director = np.array([['Jane Doe', 'directeur', 1, 'rvt', '', 1, 1],
                                 ['Piet de Wit', 'voorzitter', 3, 'bestuur', 'voorzitter', 1, 1]], dtype=object)
        b_position = np.array(['Anna Zwart - rvt - vicevoorzitter',
                               'Hanna Groen - bestuur - penningmeester',
                               'Jane Doe - directeur - directeur',
                               'Piet de Wit - directeur - voorzitter'])
        pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3]]
        pot_bestuur = [['Hanna Groen', 'penningmeester', 2]]
        p_position = [['directeur'], ['bestuur', 'Hanna Groen'], ['rvt', 'Anna Zwart'], ['ledenraad'], ['ambassadeur']]
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)

        e_b = np.array(['Anna Zwart - rvt - vicevoorzitter',
                        'Hanna Groen - bestuur - penningmeester',
                        'Jane Doe - rvt - ',
                        'Piet de Wit - bestuur - voorzitter'])
        e_pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3], ['Jane Doe', '', 1]]
        e_pot_b = [['Hanna Groen', 'penningmeester', 2], ['Piet de Wit', 'voorzitter', 1]]
        e_p_p = [['directeur'], ['bestuur', 'Hanna Groen'], ['rvt', 'Anna Zwart'], ['ledenraad'], ['ambassadeur']]

        self.assertTrue(np.array_equal(a, e_b))
        self.assertEqual(b, e_pot_rvt)
        self.assertEqual(c, e_pot_b)
        self.assertEqual(d, e_p_p)

    def test_check_rvt(self):
        """Unit testfor the function 'check_rvt'.

        Tests the function 'check_rvt' that determines whether potential rvt memebers can be considered true rvt memebers.

        There are two test cases, one in which no function conditions should be encountered, and one in which various
        function conditions should be encountered.

        Raises:
            AssertionError: If the returned values doe not match the expected return value.
        """
        # Test case 1
        pot_rvt = np.array([['Piet de Wit', 'voorzitter', 4]], dtype=object)
        b_position = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - rvt - voorzitter'])
        p_position = [['directeur', 'Jane Doe'], ['rvt']]
        check_b, check_p = check_rvt(pot_rvt, b_position, p_position)
        exp_p = [['directeur', 'Jane Doe'], ['rvt', 'Piet de Wit']]
        self.assertTrue(np.array_equal(check_b, b_position))
        self.assertEqual(check_p, exp_p)

        # Test case 2
        pot_rvt = [['Piet de Wit', 'voorzitter', 4], ['Ab', 'vicevoorzitter', 2], ['Co', '', 3],
                   ['Bo', '', 4], ['Do', '', 5], ['Ed', '', 2], ['Jo', '', 3], ['Fi', '', 2],
                   ['Lo', '', 5], ['Mo', '', 2], ['Ap', '', 5], ['Ab', '', 1], ['Ma', '', 1]]
        b_position = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - rvt - voorzitter',
                               'Ab - rvt - vicevoorzitter', 'Co - rvt - ', 'Bo - rvt - ',
                               'Do - rvt - ', 'Ed - rvt - ', 'Jo - rvt - ', 'Fi - rvt - ',
                               'Lo - rvt - ', 'Mo - rvt - ', 'Ap - rvt - ', 'Ab - rvt - ',
                               'Ma - rvt - '])
        p_position = [['directeur', 'Jane Doe'], ['rvt']]
        exp_b = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - rvt - voorzitter',
                          'Bo - rvt - ', 'Do - rvt - ', 'Lo - rvt - ', 'Ap - rvt - '])
        exp_p = [['directeur', 'Jane Doe'], ['rvt', 'Piet de Wit', 'Bo', 'Do', 'Lo', 'Ap']]
        check_b, check_p = check_rvt(pot_rvt, b_position, p_position)
        self.assertEqual(check_p, exp_p)
        self.assertTrue(np.array_equal(check_b, exp_b))

    def test_check_bestuur(self):
        """Unit testfor the function 'check_bestuur'.

        Tests the function 'check_bestuur' that determines whether potential bestuur memebers can be considered true bestuur
        memebers.

        There are two test cases, one in which no function conditions should be encountered, and one in which various
        function conditions should be encountered.

        Raises:
            AssertionError: If the returned values doe not match the expected return value.
        """
        # Test case 1
        pot_bestuur = [['Piet de Wit', 'voorzitter', 4]]
        b_position = np.array(['Jane Doe - directeur - directeur',
                               'Piet de Wit - bestuur - voorzitter'])
        p_position = [['directeur', 'Jane Doe'], ['bestuur']]
        check_b, check_p = check_bestuur(pot_bestuur, b_position, p_position)
        exp_p = [['directeur', 'Jane Doe'], ['bestuur', 'Piet de Wit']]
        self.assertTrue(np.array_equal(check_b, b_position))
        self.assertEqual(check_p, exp_p)

        # Test case 2
        pot_bestuur = [['Piet de Wit', 'voorzitter', 4], ['Ab', 'vicevoorzitter', 2], ['Co', '', 3],
                       ['Bo', '', 4], ['Do', '', 5], ['Ed', '', 2], ['Jo', '', 3], ['Fi', '', 2],
                       ['Lo', '', 5], ['Mo', '', 2], ['Ap', '', 5], ['Ab', '', 1], ['Ma', '', 1]]
        b_position = np.array(['Jane Doe - directeur - directeur',
                               'Piet de Wit - bestuur - voorzitter',
                               'Ab - bestuur - vicevoorzitter', 'Co - bestuur - ', 'Bo - bestuur - ',
                               'Do - bestuur - ', 'Ed - bestuur - ', 'Jo - bestuur - ',
                               'Fi - bestuur - ', 'Lo - bestuur - ', 'Mo - bestuur - ',
                               'Ap - bestuur - ', 'Ab - bestuur - ', 'Ma - bestuur - '])
        p_position = [['directeur', 'Jane Doe'], ['bestuur']]
        exp_b = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - bestuur - voorzitter',
                          'Bo - bestuur - ', 'Do - bestuur - ', 'Lo - bestuur - ', 'Ap - bestuur - '])
        exp_p = [['directeur', 'Jane Doe'], ['bestuur', 'Piet de Wit', 'Bo', 'Do', 'Lo', 'Ap']]
        check_b, check_p = check_bestuur(pot_bestuur, b_position, p_position)
        self.assertEqual(check_p, exp_p)
        self.assertTrue(np.array_equal(check_b, exp_b))

    def test_append_p_position(self):
        """Unit test for the 'append_p_position' function.

        This function tests the 'append_p_position' function that append a person's name to their main position in
          the list of positions.

        There is one test case

        Raises:
            AssertionError: If the returned parameter does not match the expected return value.
        """
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad'], ['kascommissie'],
                      ['controlecommissie'], ['ambassadeur']]
        main = 'rvt'
        name = 'Jane Doe'
        expected = [['directeur'], ['bestuur'], ['rvt', 'Jane Doe'], ['ledenraad'], ['kascommissie'],
                    ['controlecommissie'], ['ambassadeur']]
        result = append_p_position(p_position, main, name)
        self.assertEqual(result, expected)

    def test_array_p_position(self):
        """Unit test for the function 'array_p_position'.

        This function tests the 'array_p_position' function that returns an array of names taken from a sublist of
        the list p_position.

        Raises:
            AssertionError: If the returned parameter does not match the expected return value.
        """
        p_position = [['directeur'], ['bestuur'], ['rvt', 'Jane Doe', 'J. Doe'], ['ledenraad']]
        expected = np.array(['Jane Doe', 'J. Doe'])
        result = array_p_position(p_position, 'rvt')
        self.assertTrue(np.array_equal(expected, result))
