"""This file contains the class DetermineJobs with functions to determine job positions."""
import re
import numpy as np
from classes.keywords import JobKeywords


class DetermineJobs:
    """Class containing functions to determine jobs.

    This class contains functions that are used to determine (sub)jobs of people based on the text
    in which the names are found. It contains the following functions:

    - determine_main_job
    - determine_sub_job
    - surrounding_words
    - count_occurrence
    - relevant_sentences
    """

    def __init__(self, main_jobs=None, main_job=None, members=None, doc=None, p_position=None, position=None): #pylint: disable=too-many-arguments'
        """Define class variables."""
        self.main_job = main_job
        self.main_jobs = main_jobs
        self.members = members
        self.doc = doc
        self.p_position = p_position
        self.position = position
        self.sentences = None
        self.surroundings = None

    @staticmethod
    def surrounding_words(text: np.array, search_names: list):
        """Determine words surrounding an name in a text.

        For a given 'text' and search words ('search_name'), this function returns an array of words that are
        found before and after the 'search_name'.
        
        Args:
            text (np.array): text to search through
            search_names (list): name to look for in the text
        
        Returns:
            surrounding_words (np.array): array of words that are
            found before and after the 'search_name'.
        """
        # function definitions
        surrounding_words = np.array([])
        text = np.array2string(text, separator=' ')
        searchnames = sorted(search_names, key=len, reverse=True)

        # preprocess text
        for search_name in searchnames:
            text = text.lower().replace(search_name.lower(), 'search4term')
        text = re.sub('[^0-9a-zA-Z ]+', ' ', text)
        text = text.replace('vice voorzitter', 'vicevoorzitter')
        text = text.replace('algemeen', '')
        text = text.replace('adjunct', '')
        text = text.replace('interim', '')
        text_split = text.split()

        # obtain surrounding words
        for i, word in enumerate(text_split):
            if word == 'search4term':
                if i != 0:
                    surrounding_words = np.append(surrounding_words, text_split[i-1])
                if i != len(text_split) - 1:
                    surrounding_words = np.append(surrounding_words, text_split[i+1])
        return surrounding_words


    @staticmethod
    def count_occurrence(text: np.array, search_words: list):
        """Return the summed total of occurrences of search words in text.
        
        This function counts the total number of occurrences of each word in the 'search_words'
        list within the provided 'text', and the number of sentences in which any of the search words is found.
        The function takes care of word boundaries to avoid
        partial matches.

        Args:
            text (np.array): A list of sentences or paragraphs as strings.
            search_words (list of str): A list of words to be searched for in the 'text'.

        Returns:
            tuple: A tuple containing two values: the total count of occurrences of search words
            in the entire 'text' and the number of sentences in 'text' that contain at least one
            of the search words.
        """
        # Preprocess text
        fulltext = np.array2string(text, separator=' ')
        fulltext = re.sub(r"[\[\]']", '', fulltext)
        fulltext = fulltext.replace('vice voorzitter', 'vicevoorzitter')
        fulltext = fulltext.replace('vice-voorzitter', 'vicevoorzitter')

        # Define varibales to be returned
        totalcount = 0
        totalcount_sentence = 0

        # Determine totalcount
        for item in search_words:
            escape_item = re.escape(item)
            totalcount += sum(1 for _ in re.finditer(r'\b' + escape_item + r'\b', fulltext))
        
        # Determine totalcount_sentence
        for sentence in text:
            sentence = sentence.replace('vice voorzitter', 'vicevoorzitter')
            sentence = sentence.replace('vice-voorzitter', 'vicevoorzitter')
            count = 0
            for item in search_words:
                escape_item = re.escape(item)
                count = count + sum(1 for _ in re.finditer(r'\b' + escape_item + r'\b', sentence))
            if count > 0:
                totalcount_sentence += 1
        return totalcount, totalcount_sentence


    def determine_main_job(self, sentences: list = None, surroundings: list = None):
        """Determine main job category based on sentence and overall frequency.

        This function determines the primary job category by analyzing the occurrence frequency of
        each job category in both the direct sentences and the surrounding sentences. The process
        follows these steps:

        1. Calculate the sentence frequency (fs) and total frequency (ft) for each job category
        based on the direct sentences.
        2. Calculate the sentence frequency (fss) and total frequency (fts) for each job category
        based on the surrounding sentences.
        3. Determine the main job using the following rules in order of:
        1. The most occuring category in the direct text based on sentence frequency (fs, i.e. number of
            sentences in which category+name is found)
        2. If none can be identified, or there is a tie: try based on sentence frequency from surrounding
            sentences (fss).
        3. If none can be identified: try based on overall frequency in main text
        4. If none can be identified: try based on overall frequency in surrounding text
        5. If none can be identified, select first element (main jobs) from the list of condition 1, since the main jobs list
            is ordered in 'most likely with few number of occureences'
        6. If none can be identified, select first element (main jobs) from the list of condition 2, since the main jobs list
            is ordered in 'most likely with few number of occureences'
        7. If still none can be identified, set main jobs to None
        4. Determine the term frequency of selected main job directeur based on direct sentences
        5. Determine the term frequency of selected main job bestuur and rvt based on surrounding sentences

        Args:
            main_jobs (list): A list containing sub-lists of words for each main job category.
            sentences (list): A list of sentences in which to search for job categories.
            surroundings (list): A list of sentences surrounding the main text.
        
        Returns:
            list: A list containing four elements in the following order:
                - The determined main job category (str) or None if no category is found.
                - The total frequency of the category 'directeur' in the direct sentences (int).
                - The total frequency of the category 'bestuur' in the surrounding sentences (int).
                - The total frequency of the category 'rvt' in the surrounding sentences (int).
        """
        # Define sentence (fs, fss) and total frequencies (ft, fts) for direct sentences and surrounding sentences
        self.relevant_sentences()
        if sentences is None: sentences = self.sentences
        if surroundings is None: surroundings = self.surroundings

        fs = np.empty(len(self.main_jobs))
        fss = np.empty(len(self.main_jobs))
        ft = np.empty(len(self.main_jobs))
        fts = np.empty(len(self.main_jobs))

        main_job = np.array([mj[0] for mj in self.main_jobs])

        # Determine ft,fs, fts, and ftss for each job
        for m, m_j in enumerate(self.main_jobs):
            ft[m], fs[m] = DetermineJobs.count_occurrence(sentences, m_j)
            fts[m], fss[m] = DetermineJobs.count_occurrence(surroundings, m_j)
        
        # Select based on most occuring category in the direct text using sentence frequency, no tie
        if (max(fs) > 0 and len(np.where(fs == max(fs))[0]) == 1):
            main_cat = main_job[np.where(fs == max(fs))[0]][0]

        # Select based on sentence frequency from surrounding sentences, no tie
        elif (max(fss) > 0 and len(np.where(fss == max(fss))[0]) == 1):
            main_cat = main_job[np.where(fss == max(fss))[0]][0]

        # Select based on overall frequency in main text, no tie
        elif (max(ft) > 0 and len(np.where(ft == max(ft))[0]) == 1):
            main_cat = main_job[np.where(ft == max(ft))[0]][0]

        # Select based on overall frequency in surrounding text, no tie
        elif (max(fts) > 0 and len(np.where(fts == max(fts))[0]) == 1):
            main_cat = main_job[np.where(fts == max(fts))[0]][0]

        # Selection based on most occuring category in the direct text based on sentence frequency gives a tie, therefor
        # select first element of tied fs list
        elif max(fs) > 0:
            main_cat = main_job[np.where(fs == max(fs))[0]][0]

        # Selection based on most occuring category in the surrounding text based on frequency gives a tie, therefore select first
        # element of tied fss list
        elif max(fss) > 0:
            main_cat = main_job[np.where(fss == max(fss))[0]][0]

        # do not select a main category
        else:
            main_cat = None
        
        # define term frequency of selected main job directeur based on direct sentences
        ft_director = ft[np.where(main_job == 'directeur')]

        # define term frequency of selected main job bestuur/rvt based on surrounding sentences
        fts_bestuur = fts[np.where(main_job == 'bestuur')]
        fts_rvt = fts[np.where(main_job == 'rvt')]

        return [main_cat, ft_director, fts_bestuur, fts_rvt]


    def determine_sub_job(self, sentences: list = None):
        """Determine the sub job category based on the words mentioned in the provided 'sentences' and main category ('main_cat').

        This function determines the sub job category by analyzing the occurrence frequency of each
        sub job category in the surrounding words of the given 'members' (different writings of a persons' name).
        The process follows these steps:

        1. Get the surrounding words of the given members from the sentences.
        2. Calculate the occurrence frequency of each sub job category in the surrounding words.
        3. If there are sub job categories with a frequency greater than 0, select the one with the
        highest frequency.
        4. If there is a tie among multiple sub job categories with the highest frequency, choose
        the first one in the list (JobKeywords.sub_jobs).
        5. Determine the primary sub_cat and backup_sub_cat based on the main_cat, if any was found.
        6. The sub cat for main cat director is only defined if the sub cat is not director. If it is,
        there is no backup sub cat

        Args:
            members (list): A list of names to find the surrounding words for.
            sentences (list): A list of sentences containing the text to search for sub job categories.
            main_cat (str): The previously determined main job category.

        Returns:
            list: A list containing two elements in the following order:
                - The determined sub job category (str) or an empty string if no category is found.
                - The backup sub job category (str) or an empty string if no category is found.
        """
        self.relevant_sentences()
        if sentences is None: sentences = self.sentences
        
        # Define c_sub_jobs
        c_sub_job = np.array([])

        # Determine the surrounding words and use these to determine the count of each sub job 
        surrounding_w = DetermineJobs.surrounding_words(sentences, self.members)
        if surrounding_w.size > 0:
            for sj in JobKeywords.sub_jobs:
                c_sub_job = np.append(c_sub_job, DetermineJobs.count_occurrence(surrounding_w, sj)[0])
        else:
            c_sub_job = np.append(c_sub_job, 0)
        
        # Determine sub_cat and backup_sub_cat
        if max(c_sub_job) > 0 and len(np.where(c_sub_job == max(c_sub_job))[0]) == 1:
            sub_cat = backup_sub_cat = JobKeywords.sub_job[np.where(c_sub_job == max(c_sub_job))[0]][0]
            if self.main_job == 'directeur' and sub_cat == 'directeur':
                backup_sub_cat = ''
        else:
            sub_cat = backup_sub_cat = ''
        
        return [sub_cat, backup_sub_cat]


    def relevant_sentences(self):
        """Identify all sentences containing a specific person and those directly surrounding them.

        This function takes a stanza Document object 'doc' and a list of 'members', which are different write of the same name
        of a specific person to search for. The function extracts all 'sentences' that contain any of the 'members' and those
        directly surrounding ('surroundings') them in the document.

        Args:
            doc (stanza.Document): A stanza Document object containing the parsed text.
            members (list): A list of names (str) representing a specific person to search for.

        Returns:
            tuple: A tuple containing two numpy arrays:
                - sentences: An array containing all sentences that contain any of the 'members'.
                - surroundings: An array containing sentences directly surrounding the 'sentences' that
                containing the 'members'.
        """
        # Definitions
        prevsentence = ''
        sentences = np.array([])
        surroundings = np.array([])
        need_next_sentence = False

        # Determine sentences and surroundings
        for sentence in self.doc.sentences:
            if any(member in sentence.text for member in self.members):
                sentences = np.append(sentences, sentence.text.lower())
                if prevsentence not in list(surroundings):
                    surroundings = np.append(surroundings, prevsentence)
                if sentence not in list(surroundings):
                    surroundings = np.append(surroundings, sentence.text.lower())
                need_next_sentence = True
            elif need_next_sentence:
                if sentence.text.lower() not in surroundings:
                    surroundings = np.append(surroundings, sentence.text.lower())
                need_next_sentence = False
            prevsentence = sentence.text.lower()
        self.sentences = sentences
        self.surroundings = surroundings
