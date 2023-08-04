"""Unit tests for functions in clas DetermineJobs"""
import unittest
import numpy as np
from auto_extract.determinejobs import DetermineJobs
from auto_extract.keywords import JobKeywords
import stanza

class TestsDetermineJobs(unittest.TestCase):
    """Class containing functions to determine jobs.

    This class contains functions that are used to determine (sub)jobs of people based on the text
    in which the names are found. It contains the following functions:

    Test methods:
        - test_surrounding_words: tests the 'surrounding_words' function that dermines the words surrounding a given name in a
          text.
        - test_count_occurrence: tests the 'count_occurrence' function that counts for a list of serach words the occurences in
          a text.
        - test_determine_main_job: tests the 'determine_main_job' function that determines the main job from a set of sentences
          or surrounding sentences.
        - test_determine_sub_job: tests the 'determine_sub_job' function that determines the sub job based on a persons name,
          the previously determine main cat and a list of sentences.
        - test_relevant_sentences: tests the 'relevant_sentences' function that identifies all sentences containing a specific
          person and those directly surrounding them.
    """

    DetermineJobs = DetermineJobs()

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
        DetermineJobs(text = np.array(['Jane vice voorzitter', 'vice-voorzitter Jane', 'Jane, algemeen directeur.',
                        'Jane is de directeur', 'penningmeester Jane Doe Voorzitter Jane']))
        expected = np.array(['vicevoorzitter', 'vicevoorzitter', 'search4term', 'search4term',
                            'directeur', 'directeur', 'is', 'penningmeester', 'voorzitter',
                            'voorzitter'])
        search_names = ['Jane', 'Jane Doe']
        outp = DetermineJobs.surrounding_words(search_names)
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
        DetermineJobs(text = np.array(['bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                        'dr. j. doe werkt bij bedrijf.']))
        search_words = ['directeur', 'directrice']
        totalcount, totalcount_sentence = DetermineJobs.count_occurrence(search_words)
        self.assertEqual(totalcount, 2)
        self.assertEqual(totalcount_sentence, 1)

        # Test case 2
        DetermineJobs(text = np.array(['vice-voorzitter Jane']))
        search_words = ['voorzitter']
        totalcount, totalcount_sentence = DetermineJobs.count_occurrence(search_words)
        self.assertEqual(totalcount, 0)
        self.assertEqual(totalcount_sentence, 0)

        # Test case 3
        search_words = ['vice-voorzitter', 'vicevoorzitter', 'vice voorzitter']
        totalcount, totalcount_sentence = DetermineJobs.count_occurrence(search_words)
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
        
        # Starting definitions for sentences and surrounding sentences
        members = [jane doe, dr. j.]
        text = np.array(['deze tekst dient enkel om te testen rvt.',
                         'bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                         'dr. j. doe werkt bij bedrijf.',
                         'bedrijf heeft een rvt, raad van toezicht rvt, absoluut, ab, absurt.'])
        doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)
        DetermineJobs(main_jobs=[JobKeywords.directeur, JobKeywords.rvt, JobKeywords.bestuur], doc=doc,
                      members=members)
        '''sentences = np.array(['bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                            'dr. j. doe werkt bij bedrijf.'])
        surroundings = np.array(['deze tekst dient enkel om te testen rvt.',
                                'bedrijfsstructuur directeur jane doe, directeur van bedrijf.',
                                'dr. j. doe werkt bij bedrijf.',
                                'bedrijf heeft een rvt, raad van toezicht rvt, absoluut, ab, absurt.''''
                                ])
        # Test case 1
        check = determine_main_job(sentences, surroundings)
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
