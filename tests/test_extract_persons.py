"""This module contains unit tests for the functions in extract_persons"""
import unittest
import os
import numpy as np
import stanza
from auto_extract.extract_persons import abbreviate
from auto_extract.extract_persons import append_p_position
from auto_extract.extract_persons import array_p_position
from auto_extract.extract_persons import check_bestuur
from auto_extract.extract_persons import check_rvt
from auto_extract.extract_persons import count_occurrence
from auto_extract.extract_persons import determine_main_job
from auto_extract.extract_persons import determine_sub_job
from auto_extract.extract_persons import director_check
from auto_extract.extract_persons import extract_persons
from auto_extract.extract_persons import find_duplicate_persons
from auto_extract.extract_persons import get_tsr
from auto_extract.extract_persons import identify_potential_people
from auto_extract.extract_persons import relevant_sentences
from auto_extract.extract_persons import strip_names_from_title
from auto_extract.extract_persons import surrounding_words
from auto_extract.preprocessing import preprocess_pdf


# Download stanza
stanza.download('nl')

# Definitions for test case 1
indir = os.path.join(os.getcwd(), 'tests')
infile = os.path.join(indir, 'test_report.pdf')
text = preprocess_pdf(infile, ' ')
doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)

# Definitions for test case 2
all_persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
infile2 = os.path.join(indir, 'test_report2.pdf')
text2 = preprocess_pdf(infile2, ' ')
doc2 = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text2)
all_persons2 = np.unique([f'{ent.text}' for ent in doc2.ents if ent.type == "PER"])

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
        - test_determine_main_job: tests the 'determine_main_job' function that determines the main job from a set of sentences
          or surrounding sentences.
        - test_determine_sub_job: tests the 'determine_sub_job' function that determines the sub job based on a persons name,
          the previously determine main cat and a list of sentences.
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
        assert(abbreviate(name, 2) == 'J Doe ')
        assert(abbreviate(name2, 2) == 'J de Wit ')
        assert(abbreviate(name3, 2) == 'J P de Wit ')
        assert(abbreviate(name4, 2) == 'J P van der Wit ')
        assert(abbreviate(name4, 3) == 'J P van der Wit ')


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
        tsr1, rs1 = get_tsr('Jane Doe', 'Jane Doe')
        assert(tsr1 == 100)
        assert(rs1 == 90)
        # Test cse 2
        tsr2, rs2 = get_tsr('Jane Doe', 'Jane')
        assert(tsr2 == 100)
        assert(rs2 == 100)
        # Test case 3
        tsr3, rs3 = get_tsr('J. Doe', 'J.P. Doe')
        assert(tsr3 == 100)
        assert(rs3 == 90)
        # Test case 4
        tsr4, rs4 = get_tsr('J. Doe', 'Jane Doe')
        assert(tsr4 == 100)
        assert(rs4 == 95)
        # Test case 5
        tsr5, rs5 = get_tsr('Jane Doe', 'J. Doe')
        assert(tsr5 == 100)
        assert(rs5 == 95)


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
        out, out_r = strip_names_from_title(inp)
        assert(out == expected)
        assert(out_r == expected_removed)


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
        persons = ['Dr. Jane Doe', 'Jane Doe', 'J. Doe', 'Jane Elaine Doe',
                'J.E. Doe', 'Jane White', 'William Doe', 'Jane']
        outnames = find_duplicate_persons(persons)
        expected = [['Jane Elaine Doe', 'Dr. Jane Doe', 'Jane Doe', 'J.E. Doe', 'J. Doe'],
                    ['Jane White'], ['William Doe']]
        assert(isinstance(outnames, list))
        assert(outnames == expected)


    def test_surrounding_words(self):
        """Unit test for the surrounding_words function.

        This function tests the 'surrounding_words' function that dermines the words surrounding
        a given name in a text.

        There is one test case, consisting of one array of five elements and one search name that is expected to
        return an array of ten results found.

        Raises:
            AssertionError: If the returned variable is not an array, or if the return values do
            not match the expected return values.
        """
        text = np.array(['Jane vice voorzitter', 'vice-voorzitter Jane', 'Jane, algemeen directeur.',
                        'Jane is de directeur', 'penningmeester Jane Doe Voorzitter Jane'])
        expected = np.array(['vicevoorzitter', 'vicevoorzitter', 'search4term', 'search4term',
                            'directeur', 'directeur', 'is', 'penningmeester', 'voorzitter',
                            'voorzitter'])
        search_names = ['Jane', 'Jane Doe']
        outp = surrounding_words(text, search_names)
        assert(isinstance(outp, np.ndarray))
        assert(np.array_equal(outp, expected))


    def test_count_occurrence(self):
        """Unit test for the 'count_occurrence" function.

        The function tests the 'count_occurrence' function that counts for a list of 
        serach words the occurences for each of them in a text and the number of sentences that
        contain any of the search words.

        There are three test cases, each with different test texts and different search words

        Raises:
            AssertionError: If the return values do not match the expected return values.
        """
        # Test case 1
        text = np.array(['bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                        'dr. j. doe werkt bij bedrijf.'])
        search_words = ['directeur', 'directrice']
        totalcount, totalcount_sentence = count_occurrence(text, search_words)
        assert(totalcount == 2)
        assert(totalcount_sentence == 1)

        # Test case 2
        text = np.array(['vice-voorzitter Jane'])
        search_words = ['voorzitter']
        totalcount, totalcount_sentence = count_occurrence(text, search_words)
        assert(totalcount == 0)
        assert(totalcount_sentence == 0)

        # Test case 3
        search_words = ['vice-voorzitter', 'vicevoorzitter', 'vice voorzitter']
        totalcount, totalcount_sentence = count_occurrence(text, search_words)
        assert(totalcount == 1)
        assert(totalcount_sentence == 1)


    def test_determine_main_job(self):
        """Unit test for the 'determine_main_job' function.

        The function tests the 'determine_main_job' function that determines the main job from a set of sentences
        or surrounding sentences.

        After an initial set of definitons for the parameters sentences, surroundings, there are 8 test cases, for each of
        which the input sentences and/or input surrounding sentences are updated

        Raises:
            AssertionError: If the return values do not match the expected return values for any of the test cases.
        """
        # Definitions of jobs
        directeur = ['directeur', 'directrice', 'directie', 'bestuurder']
        rvt = ['rvt', 'raad van toezicht', 'raad v. toezicht', 'auditcommissie', 'audit commissie']
        bestuur = ['bestuur', 'db', 'ab', 'rvb', 'bestuurslid', 'bestuursleden', 'hoofdbestuur',
                'bestuursvoorzitter']
        jobs = [directeur, rvt, bestuur]

        # Starting definitions for sentences and surrounding sentences
        sentences = np.array(['bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                            'dr. j. doe werkt bij bedrijf.'])
        surroundings = np.array(['deze tekst dient enkel om te testen rvt.',
                                'bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een rvt, raad van toezicht rvt, absoluut, ab, absurt.'
                                ])
        # Test case 1
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'directeur')
        assert(check[1] == 2)
        assert(check[2] == 1)

        # Test case 2
        sentences = np.array(['rvt, directeur'])
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'rvt')

        # Test case 3
        surroundings = np.array(['deze tekst dient enkel om te testen.',
                                'bedrijfsstructuur directeur jane doe, van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een, raad van toezicht, absoluut, ab, absurt.'])
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'directeur')

        # Test case 4
        sentences = np.array(['directeur rvt directeur'])
        surroundings = np.array(['directeur', 'rvt'])
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'directeur')

        # Test case 5
        sentences = np.array(['directeur rvt'])
        surroundings = np.array(['directeur rvt directeur'])
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'directeur')

        # Test case 6
        check = determine_main_job(jobs, sentences, sentences)
        assert(check[0] == 'directeur')

        # Test case 7
        sentences = np.array([' '])
        surroundings = np.array(['directeur rvt'])
        check = determine_main_job(jobs, sentences, surroundings)
        assert(check[0] == 'directeur')

        # Test case 8
        sentences = np.array(['niets'])
        check = determine_main_job(jobs, sentences, sentences)
        assert(check[0] is None)


    def test_determine_sub_job(self):
        """Unit test for the 'determine_sub_job' function.
        
        This function tests the 'determine_sub_job' function that determines the sub job based on a a list of different
        writings of a persons name (members), the previously determine main cat and a list of sentences.

        There are five test cases. For a given list of members (names), each test checks a case with either different
        given sentences and/or main jobs

        Raises:
            AssertionError: If the return values do not match the expected return values for any of the test cases.
        """
        members = ['Jane Doe', 'J. Doe']

        # Test case 1
        sentences = np.array(['directeur Jane Doe directeur. J. Doe voorzitter'])
        main_cat = 'directeur'
        check = determine_sub_job(members, sentences, main_cat)
        assert(check[0] == 'directeur')
        assert(check[1] == '')

        # Test case 2
        sentences = np.array(['Jane Doe is niet directeur van bedrijf. J. Doe not voorzitter'])
        check = determine_sub_job(members, sentences, main_cat)
        assert(check[0] == '')

        # Test case 3
        check = determine_sub_job(members, np.array(['Jane Doe']), main_cat)
        assert(check[0] == '')

        # Test case 4
        check = determine_sub_job(members, np.array(['Jane Doe voorzitter']), main_cat)
        assert(check[0] == '')

        # Test case 5
        check = determine_sub_job(members, np.array(['Jane Doe voorzitter']), 'voorzitter')
        assert(check[0] == 'voorzitter')


    def test_identify_potential_people(self):
        people = identify_potential_people(doc, all_persons)
        expected = [['Anna de Wit', 'A.B. de Wit'], ['Bernard Zwartjes'],
                    ['Cornelis Geel'], ['Dirkje Rood'], ['E. van Grijs', 'Eduard van Grijs'],
                    ['F. de Blauw', 'Ferdinand de Blauw'], ['G. Roze', 'Gerard Roze'],
                    ['H. Doe', 'Hendrik Doe'], ['Hendrik Groen', 'Mr. H. Groen'],
                    ['J. Doe', 'Jane Doe'], ['Isaak Paars'], ['Jan van Oranje'], ['Karel'],
                    ['Lodewijk'], ['Maria']]
        assert(isinstance(people, list))
        assert(people.sort() == expected.sort())


    def test_relevant_sentences():
        sentences, surroundings = relevant_sentences(doc, ['Jane Doe', 'J. Doe'])
        assert(isinstance(sentences, np.ndarray))
        assert(isinstance(surroundings, np.ndarray))
        expected_s = np.array(['bedrijfsstructuur jane doe, directeur van bedrijf.',
                            'dr. j. doe werkt bij bedrijf.'])
        expected_sur = np.array(['deze tekst dient enkel om te testen.',
                                'bedrijfsstructuur jane doe, directeur van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een raad van toezicht rvt.'])
        assert(np.array_equal(expected_s, sentences))
        assert(np.array_equal(expected_sur, surroundings))


    def test_append_p_position():
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad'], ['kascommissie'],
                    ['controlecommissie'], ['ambassadeur']]
        main = 'rvt'
        name = 'Jane Doe'
        expected = [['directeur'], ['bestuur'], ['rvt', 'Jane Doe'], ['ledenraad'], ['kascommissie'],
                    ['controlecommissie'], ['ambassadeur']]
        result = append_p_position(p_position, main, name)
        assert(result == expected)


    def test_extract_persons():
        e_a = np.array(['Sarah', 'Thomas'])
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
        e_r = np.array(['Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes'])
        e_b = np.array(['Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw'])
        e_l = np.array(['Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria'])
        e_k = np.array(['Gerard Roze', 'Hendrik Groen'])
        e_c = np.array(['Mohammed El Idrissi', 'Saïda Benali'])
        a, b_p, d, r, b, l, k, c = extract_persons(doc, all_persons)
        assert(np.array_equal(e_a, a))
        assert(np.array_equal(e_bp, b_p))
        assert(np.array_equal(np.array(['Jane Doe']), d))
        assert(np.array_equal(e_r, r))
        assert(np.array_equal(e_b, b))
        assert(np.array_equal(e_l, l))
        assert(np.array_equal(e_k, k))
        assert(np.array_equal(e_c, c))
        d = extract_persons(doc2, all_persons2)[2]
        assert(np.array_equal(np.array(['Jane Doe']), d))


    def test_array_p_position():
        p_position = [['directeur'], ['bestuur'], ['rvt', 'Jane Doe', 'J. Doe'], ['ledenraad']]
        expected = np.array(['Jane Doe', 'J. Doe'])
        result = array_p_position(p_position, 'rvt')
        assert(np.array_equal(expected, result))


    def test_director_check():
        # pot_director = name, sub_cat, ft_director, main_cat, backup_sub_cat, fts_bestuur, fts_rvt
        pot_director = np.array([['Jane Doe', 'directeur', 3, 'rvt', 3, 1, 1],
                                ['Piet de Wit', 'voorzitter', 3, 'rvt', 1, 1, 1]], dtype=object)
        b_position = np.array(['Jane Doe - directeur - directeur',
                            'Piet de Wit - directeur - voorzitter'])
        pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3]]
        pot_bestuur = [['Hanna Groen', 'penningmeester', 2]]
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad']]
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
        e_b = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - rvt - voorzitter'])
        e_pot_rvt = [['Anna Zwart', 'vicevoorzitter', 3], ['Piet de Wit', 'voorzitter', 1]]
        e_pot_b = pot_bestuur
        e_p_p = [['directeur', 'Jane Doe'], ['bestuur'], ['rvt'], ['ledenraad']]
        assert(np.array_equal(a, e_b))
        assert(b == e_pot_rvt)
        assert(c == e_pot_b)
        assert(d == e_p_p)
        pot_director = np.array([['Jane Doe', 'directeur', 3, 'rvt', 3, 1, 1],
                                ['Piet de Wit', 'voorzitter', 3, 'bestuur', 1, 1, 1]], dtype=object)
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
        assert(c == [['Hanna Groen', 'penningmeester', 2], ['Piet de Wit', 'voorzitter', 1]])
        assert(np.array_equal(a, np.array(['Jane Doe - directeur - directeur',
                                        'Piet de Wit - bestuur - voorzitter'])))
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad']]
        pot_director = np.array([['Jane Doe', 'directeur', 3, 'rvt', 3, 1, 1],
                                ['Piet de Wit', 'voorzitter', 3, 'ledenraad', 1, 1, 1]], dtype=object)
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
        assert(d == [['directeur', 'Jane Doe'], ['bestuur'], ['rvt'], ['ledenraad', 'Piet de Wit']])
        assert(np.array_equal(a, np.array(['Jane Doe - directeur - directeur',
                                        'Piet de Wit - ledenraad - voorzitter'])))
        b_position = np.array(['Jane Doe - directeur - directeur',
                            'Piet de Wit - directeur - '])
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad'], ['ambassadeur']]
        pot_director = np.array([['Jane Doe', 'directeur', 3, 'rvt', 3, 1, 1],
                                ['Piet de Wit', '', 3, 'ambassadeur', 1, 1, 1]], dtype=object)
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
        assert(np.array_equal(a, np.array(['Jane Doe - directeur - directeur'])))
        assert(d == [['directeur', 'Jane Doe'], ['bestuur'], ['rvt'], ['ledenraad'],
                    ['ambassadeur', 'Piet de Wit']])
        p_position = [['directeur'], ['bestuur'], ['rvt'], ['ledenraad'], ['ambassadeur']]
        pot_director = np.array([['Jane Doe', 'directeur', 3, 'rvt', 3, 1, 1],
                                ['Piet de Wit', '', 3, '', 1, 1, 1]], dtype=object)
        a, b, c, d = director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
        assert(d == p_position)


    def test_check_rvt():
        pot_rvt = [['Piet de Wit', 'voorzitter', 4]]
        b_position = np.array(['Jane Doe - directeur - directeur', 'Piet de Wit - rvt - voorzitter'])
        p_position = [['directeur', 'Jane Doe'], ['rvt']]
        check_b, check_p = check_rvt(pot_rvt, b_position, p_position)
        exp_p = [['directeur', 'Jane Doe'], ['rvt', 'Piet de Wit']]
        assert(np.array_equal(check_b, b_position))
        assert(check_p == exp_p)
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
        assert(check_p == exp_p)
        assert(np.array_equal(check_b, exp_b))


    def test_check_bestuur():
        pot_bestuur = [['Piet de Wit', 'voorzitter', 4]]
        b_position = np.array(['Jane Doe - directeur - directeur',
                            'Piet de Wit - bestuur - voorzitter'])
        p_position = [['directeur', 'Jane Doe'], ['bestuur']]
        check_b, check_p = check_bestuur(pot_bestuur, b_position, p_position)
        exp_p = [['directeur', 'Jane Doe'], ['bestuur', 'Piet de Wit']]
        assert(np.array_equal(check_b, b_position))
        assert(check_p == exp_p)
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
        assert(check_p == exp_p)
        assert(np.array_equal(check_b, exp_b))
