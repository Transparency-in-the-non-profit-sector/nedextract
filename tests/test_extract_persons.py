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
        - test_identify_potential_people: tests the 'identify_potential_people' function that analyses text to find names of
          people that may have one of the predifined jobs.
        - test_relevant_sentences: tests the 'relevant_sentences' function that identifies all sentences containing a specific
          person and those directly surrounding them.
        - test_append_p_position: tests the 'append_p_position' function that append a person's name to their main position in
          the list of positions.
        - test_array_p_position: tests the 'array_p_position' function that returns an array of names taken from a sublist of
          the list p_position.
        - test_extract_persons: tests the 'extract_persons' function that extracts ambassadors and board members from a text using a rule-based method.
        - test_director_check: tests the director_check function that performs checks for potential directors and update their 
          positions if necessary
        - test_check_rvt: tests the check_rvt function that determines whether potential rvt members can be considered try=ue rvt memebers.
        - test_check_bestuur: tests the check_bestuur function that determines whether potential bestuur members can be considered true bestuur memebers.
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
        self.assertEqual(abbreviate(name, 2), 'J Doe ')
        self.assertEqual(abbreviate(name2, 2), 'J de Wit ')
        self.assertEqual(abbreviate(name3, 2), 'J P de Wit ')
        self.assertEqual(abbreviate(name4, 2), 'J P van der Wit ')
        self.assertEqual(abbreviate(name4, 3), 'J P van der Wit ')


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
        self.assertEqual(tsr1, 100)
        self.assertEqual(rs1, 90)
        # Test cse 2
        tsr2, rs2 = get_tsr('Jane Doe', 'Jane')
        self.assertEqual(tsr2, 100)
        self.assertEqual(rs2, 100)
        # Test case 3
        tsr3, rs3 = get_tsr('J. Doe', 'J.P. Doe')
        self.assertEqual(tsr3, 100)
        self.assertEqual(rs3, 90)
        # Test case 4
        tsr4, rs4 = get_tsr('J. Doe', 'Jane Doe')
        self.assertEqual(tsr4, 100)
        self.assertEqual(rs4, 95)
        # Test case 5
        tsr5, rs5 = get_tsr('Jane Doe', 'J. Doe')
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
        out, out_r = strip_names_from_title(inp)
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
        persons = ['Dr. Jane Doe', 'Jane Doe', 'J. Doe', 'Jane Elaine Doe',
                'J.E. Doe', 'Jane White', 'William Doe', 'Jane']
        outnames = find_duplicate_persons(persons)
        expected = [['Jane Elaine Doe', 'Dr. Jane Doe', 'Jane Doe', 'J.E. Doe', 'J. Doe'],
                    ['Jane White'], ['William Doe']]
        self.assertTrue(isinstance(outnames, list))
        self.assertEqual(outnames, expected)


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
        self.assertTrue(isinstance(outp, np.ndarray))
        self.assertTrue(np.array_equal(outp, expected))


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
        self.assertEqual(totalcount, 2)
        self.assertEqual(totalcount_sentence, 1)

        # Test case 2
        text = np.array(['vice-voorzitter Jane'])
        search_words = ['voorzitter']
        totalcount, totalcount_sentence = count_occurrence(text, search_words)
        self.assertEqual(totalcount, 0)
        self.assertEqual(totalcount_sentence, 0)

        # Test case 3
        search_words = ['vice-voorzitter', 'vicevoorzitter', 'vice voorzitter']
        totalcount, totalcount_sentence = count_occurrence(text, search_words)
        self.assertEqual(totalcount, 1)
        self.assertEqual(totalcount_sentence, 1)


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
        self.assertEqual(check[0], 'directeur')
        self.assertEqual(check[1], 2)
        self.assertEqual(check[2], 1)

        # Test case 2
        sentences = np.array(['rvt, directeur'])
        check = determine_main_job(jobs, sentences, surroundings)
        self.assertEqual(check[0], 'rvt')

        # Test case 3
        surroundings = np.array(['deze tekst dient enkel om te testen.',
                                'bedrijfsstructuur directeur jane doe, van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een, raad van toezicht, absoluut, ab, absurt.'])
        check = determine_main_job(jobs, sentences, surroundings)
        self.assertEqual(check[0], 'directeur')

        # Test case 4
        sentences = np.array(['directeur rvt directeur'])
        surroundings = np.array(['directeur', 'rvt'])
        check = determine_main_job(jobs, sentences, surroundings)
        self.assertEqual(check[0], 'directeur')

        # Test case 5
        sentences = np.array(['directeur rvt'])
        surroundings = np.array(['directeur rvt directeur'])
        check = determine_main_job(jobs, sentences, surroundings)
        self.assertEqual(check[0], 'directeur')

        # Test case 6
        check = determine_main_job(jobs, sentences, sentences)
        self.assertEqual(check[0], 'directeur')

        # Test case 7
        sentences = np.array([' '])
        surroundings = np.array(['directeur rvt'])
        check = determine_main_job(jobs, sentences, surroundings)
        self.assertEqual(check[0], 'directeur')

        # Test case 8
        sentences = np.array(['niets'])
        check = determine_main_job(jobs, sentences, sentences)
        self.assertTrue(check[0] is None)


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
        self.assertEqual(check[0], 'directeur')
        self.assertEqual(check[1], '')

        # Test case 2
        sentences = np.array(['Jane Doe is niet directeur van bedrijf. J. Doe not voorzitter'])
        check = determine_sub_job(members, sentences, main_cat)
        self.assertEqual(check[0], '')

        # Test case 3
        check = determine_sub_job(members, np.array(['Jane Doe']), main_cat)
        self.assertEqual(check[0], '')

        # Test case 4
        check = determine_sub_job(members, np.array(['Jane Doe voorzitter']), main_cat)
        self.assertEqual(check[0], 'voorzitter')

        # Test case 5
        check = determine_sub_job(members, np.array(['Jane Doe voorzitter']), 'rvt')
        self.assertEqual(check[0], 'voorzitter')


    def test_identify_potential_people(self):
        """Unit test for the function 'identify_potential_people'
        
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


    def test_relevant_sentences(self):
        """Unit test for the 'relevant_sentences' function.
        
        This function tests the 'relevant_sentences' function that identifies all sentences containing a specific
        person and those directly surrounding them.

        There is one test case that asserts the output instance and checks the expected output

        Raises:
            AssertionError: If the returned parameters are not a numpy array or
            if the return values do not match the expected return values.
        """
        # Test case
        sentences, surroundings = relevant_sentences(doc, ['Jane Doe', 'J. Doe'])
        self.assertTrue(isinstance(sentences, np.ndarray))
        self.assertTrue(isinstance(surroundings, np.ndarray))

        expected_s = np.array(['bedrijfsstructuur jane doe, directeur van bedrijf.',
                            'dr. j. doe werkt bij bedrijf.'])
        expected_sur = np.array(['deze tekst dient enkel om te testen.',
                                'bedrijfsstructuur jane doe, directeur van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een raad van toezicht rvt.'])
        self.assertTrue(np.array_equal(expected_s, sentences))
        self.assertTrue(np.array_equal(expected_sur, surroundings))


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
        pot_director = np.array([['Jane Doe', 'voorzitter', 2 , 'rvt', 'voorzitter', 1, 1],
                                 ['Pietje de Wit', 'voorzitter', 3, 'ambassadeur', 'voorzitter', 1, 1],
                                 ['Louwie kats', 'directeur', 3, 'bestuur', '', 5, 8],
                                 ['Bert de hond', 'lid', 6, 'rvt', 'lid', 3, 5],
                                 ['Willem Visser', 'lid', 5, 'ledenraad', 'lid', 1, 2,],
                                 ['Dirkje El Morabit', 'directeur', 6, 'rvt', '', 2, 1]
                                 ], dtype=object)
        
        b_position = np.array(['Anna Zwart - rvt - vicevoorzitter',
                                'Hanna Groen - bestuur - penningmeester',
                                'Jane Doe - directeur - voorzitter',
                                'Pietje de Wit - directeur - voorzitter',
                                'Louwie kats - directeur - directeur',
                                'Bert de hond - directeur - lid',
                                'Willem Visser - directeur - lid',
                                'Dirkje El Morabit - directeur - directeur'
                               ])
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
        
        Tests the function 'check_bestuur' that determines whether potential bestuur memebers can be considered true bestuur memebers.
        
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
