"""Functions to extract information about people mentioned in a Dutch text.

In general, the functions try to obtain for each name, what the function of that person is according to the text.
Various functions are defined that try to reduce the number of duplicate names and determine the correct function
of the persons based on various (con)textual challenges.

Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""

import itertools
import re
import numpy as np
from fuzzywuzzy import fuzz
from keywords import JobKeywords
from keywords import Titles
from keywords import Tussenvoegsels


def abbreviate(name: str, n_ab: int):
    """Function to abbreviate names.
    
    This function abbreviates the first 'n_ab' terms in a 'name', except if they are tussenvoegsels, and as long
    as it is not the last term in a name. 

    Args:
        name (str): name to be abbreviated
        n_ab (int): number of terms in the name to try to abbreviate
    
    Returns:
        abbreviation (str): The abbreviated name based on the specified number of terms.
    """
    splitname = name.split()
    abbreviation = ''
    for i, n in enumerate(splitname):
        if i < len(splitname)-1 and i <= n_ab and n not in Tussenvoegsels.tussenvoegsels:
            abbreviation = abbreviation + n[0] + ' '
        else:
            abbreviation = abbreviation + n + ' '
    return abbreviation


def get_tsr(p_i: str, p_j: str):
    """Determine the token set ratio for two names and the required score.
    
    This function determines the token set ratio for two names p_i and p_j, and the required score,
    depending on what kind of names they are.
    
    Note: The required scores for different name cases is chosen based on experience.

    Args:
        p_i (str): the first name
        p_j (str): the second name

    Returns:
        token_set_ratio, req_score (tuple): A tuple containing the token set ratio (TSR) as an integer, and the
               required score (req_score) as an integer.
    """
    token_set_ratio = fuzz.token_set_ratio(p_i, p_j)

    # if the second name is only one word
    if len(p_j.split()) == 1:
        req_score = 100
    # if both names contain initials
    elif (p_i.count('.') >= 1 and p_j.count('.') >= 1):
        req_score = 90
    # if one name contains initials, try to abbreviate the other one with up to
    # the same number of initials and then compare
    elif p_i.count('.') >= 1:
        tsr = np.array(0)
        for n_initials in range(1, p_i.count('.') + 1):
            tsr = np.append(tsr, fuzz.token_set_ratio(p_i, abbreviate(p_j, n_initials)))
        token_set_ratio = max(tsr)
        req_score = 95
    elif p_j.count('.') >= 1:
        tsr = np.array(0)
        for n_initials in range(1, p_j.count('.') + 1):
            tsr = np.append(tsr, fuzz.token_set_ratio(abbreviate(p_i, n_initials), p_j))
        token_set_ratio = max(tsr)
        req_score = 95
    # if name is normal
    else:
        req_score = 90
    return token_set_ratio, req_score


def strip_names_from_title(persons: list):
    """Strip titles from person names.
    
    This function check if a names contains a title, and remvoes it.
    It takes the following steps:
    1. Define empty lists 'p', and 'p_remove'.
    2. For each name in a list of names ('persons'), check if the lowecsed name contains a title
        and perform the following steps.
       - If it does contain a title, remove the title.
       - If the (remaining) name is longer than 1 letter, add it to the list 'p'
       - If it does not, add it to the list p_remove

    Args:
        persons (list): a list of names (str)
    
    Returns:
        p (list), p_remove (list): one containing the names stripped of titles,
        and one for names that only consist of 1 letter after stripping
    """
    p = []
    p_remove = []

    for per in persons:
        name = per.lower()
        for title in Titles.titles:
            if title in name:
                name = name.replace(title, '')
        if len(re.sub('[^a-zA-Z]', '', name)) > 1:
            p.extend([name])
        else:
            p_remove.extend([per])
    return p, p_remove


def sort_select_name(names: list):
    """Sort names in a list.
    
    This function sort the names in a list: it set the longest name that does not contain points,
    but does contain spaces, as first element.
    It takes the following steps:

    1. sort the 'names' according to their length.
    2. Determine the maximum length of a name in the 'names' list
    3. Loop through the list and looks for the longest name that has no periods (e.g., initials)
       and has at least one space..
    4. If such a name is found, this name will be moved to the first position in the list
    
    Args:
        names (list): a list of names (str)
    
    Returns:
        names (list): the input list in sorted order
    """
    ideal = 0
    names.sort(key=len, reverse=True)
    maxlen = len(names[0])
    for i, n in enumerate(names):
        if n.count('.') >= 1 and len(names) > i+1:
            if len(names[i+1]) > maxlen/2. and names[i+1].count(' ') >= 1:
                ideal = i + 1
        else:
            break
    names.insert(0, names.pop(ideal))
    return names


def find_similar_names(persons):
    """Find similar names and group them together.

    This function takes a list of persons' names as input and returns a list of lists,
    where each inner list contains names that are likely to refer to the same person.

    The function uses the following steps:
    1. Use the 'strip_names_from_title' function to remove titles from the names.
    2. Filters out the removed names from the original list.
    3. Iterates through the filtered list of input names to find matches and group similar names together. 
       Names consisting of one term, are not matched.
       - For each set input name, calculate the token set ratio (TSR) and the required score by calling 'get_tsr'.
       - If the TSR meets or exceeds the required score, the names are considered similar and grouped together.
       - Sort the list of similar names using the 'sort_select_name' function.
    4. Duplicate lists of names are removed to avoid redundant grouping.

    Args:
        persons (List[str]): A list of names to be grouped.

    Returns:
        List[List[str]]: A list of lists, where each inner list contains similar names grouped together.
    """
    outnames = []
    p, p_remove = strip_names_from_title(persons)
    persons = [n for n in persons if n not in p_remove]
    # loop through list of input names to find matches
    for i, sn in enumerate(persons):
        same_name = [sn]
        # if a name consists of one term only, do not try to find matches (This prevents James
        # from being matched with both James Brown and James White, which would imply James
        # Brown and James White are also the same person. The remainder of the loop will make
        # sure James Brown and James will be matched, as well as James White and James.)
        if (len(p[i].split()) == 1):
            outnames.append(same_name)
            continue
        for j, j_names in enumerate(persons):
            if i != j:
                token_set_ratio, req_score = get_tsr(p[i], p[j])
                # check if required score is exceeded
                if token_set_ratio >= req_score:
                    same_name.extend([j_names])
            same_name = sort_select_name(same_name)
        outnames.append(same_name)
    outnames.sort(key=len, reverse=True)

    # remove duplicate lists of names
    for i in range(len(outnames)-1, -1, -1):
        if any(all(elem in names for elem in outnames[i]) for names in outnames[0:i]):
            outnames.pop(i)
    return outnames


def find_duplicate_persons(persons):
    """Function to find duplicate names.

    From a list of names, find which names represent different writings of the same name,
    e.g. James Brown and J. Brown. Returns a list consisting of sublists, in which each sublist
    contains all versions of the same name. The token_set_ratio from the fuzzywuzzy package is
    used to determine how close to names are. Names are stripped from any titles, and when
    comparing two names where one contains initials (i.e. James Brown versus J. Brown), the first
    name is abbreviated to try to determine the initials.
    
    Args:
        persons (list[str]): list of names.
    
    Returns:
        outlist (list[list[str]]): list consisting of sublists, in which each sublist
        contains all versions of the same name.
    """
    outnames = find_similar_names(persons)

    # check if the longest item in a list is in multiple sublists
    # which might mess things up, so in that case remove and restart
    was_true = False
    for sublist in outnames:
        longest_name = max(sublist, key=len)
        if list(itertools.chain.from_iterable(outnames)).count(longest_name) > 1:
            was_true = True
            try:
                persons.remove(longest_name)
            except ValueError:
                pass
    if was_true:
        outnames = find_similar_names(persons)

    # remove items that appear in multiple sublists
    outlist = []
    for j, o_names in enumerate(outnames):
        x = o_names
        for restlist in (outnames[:j] + outnames[j+1:]):
            if any(elem in o_names for elem in restlist):
                x = [k for k in o_names if k not in restlist]
        outlist.append(x)

    # remove duplicate lists of names again
    for i in range(len(outlist)-1, -1, -1):
        if any(all(elem in names for elem in outlist[i]) for names in outlist[0:i]):
            outlist.pop(i)

    return outlist


def surrounding_words(text, search_names):
    """Determine words surrounding an name in a text.

    For a given 'text' and search words ('search_name'), this function returns an array of words that are
    found before and after the 'search_name'.
    
    Args:
        text (str): text to search through
        search_name (str): name to look for in the text
    
    Returns:
        surrounding_words (np.array): array of words that are
        found before and after the 'search_name'.
    """
    surrounding_words = np.array([])
    text = np.array2string(text, separator=' ')
    searchnames = sorted(search_names, key=len, reverse=True)

    for search_name in searchnames:
        text = text.lower().replace(search_name.lower(), 'search4term')
    text = re.sub('[^0-9a-zA-Z ]+', ' ', text)
    text = text.replace('vice voorzitter', 'vicevoorzitter')
    text = text.replace('algemeen', '')
    text = text.replace('adjunct', '')
    text = text.replace('interim', '')
    text_split = text.split()

    for i, word in enumerate(text_split):
        if word == 'search4term':
            if i != 0:
                surrounding_words = np.append(surrounding_words, text_split[i-1])
            if i != len(text_split) - 1:
                surrounding_words = np.append(surrounding_words, text_split[i+1])
    return surrounding_words


def count_occurrence(text, search_words):
    """Return the summed total of occurrences of search words in text.
    
    This function counts the total number of occurrences of each word in the 'search_words'
    list within the provided 'text', and the number of sentences in which any of the search words is found.
    The function takes care of word boundaries to avoid
    partial matches.

    Args:
        text (list of str): A list of sentences or paragraphs as strings.
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


def determine_main_job(main_jobs, sentences, surroundings):
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
    fs = np.empty(len(main_jobs))
    fss = np.empty(len(main_jobs))
    ft = np.empty(len(main_jobs))
    fts = np.empty(len(main_jobs))

    main_job = np.array([mj[0] for mj in main_jobs])

    # Determine ft,fs, fts, and ftss for each job
    for m, m_j in enumerate(main_jobs):
        ft[m], fs[m] = count_occurrence(sentences, m_j)
        fts[m], fss[m] = count_occurrence(surroundings, m_j)
    
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


def determine_sub_job(members, sentences, main_cat):
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
    # Define c_sub_job
    c_sub_job = np.array([])

    # Determine the surrounding words and use these to determine the count of each sub job 
    surrounding_w = surrounding_words(sentences, members)
    if surrounding_w.size > 0:
        for sj in JobKeywords.sub_jobs:
            c_sub_job = np.append(c_sub_job, count_occurrence(surrounding_w, sj)[0])
    else:
        c_sub_job = np.append(c_sub_job, 0)
    
    # Determine sub_cat and backup_sub_cat
    if max(c_sub_job) > 0 and len(np.where(c_sub_job == max(c_sub_job))[0]) == 1:
        sub_cat = backup_sub_cat = JobKeywords.sub_job[np.where(c_sub_job == max(c_sub_job))[0]][0]
        if main_cat == 'directeur' and sub_cat == 'directeur':
            backup_sub_cat = ''
    else:
        sub_cat = backup_sub_cat = ''
    
    return [sub_cat, backup_sub_cat]


def identify_potential_people(doc, all_persons):
    """identify potential ambassadors and board members based on keywords in sentences.
    
    This function analyzes the given 'doc' containing (stanza) processed sentences and identifies
    potential people who may hold ambassadors or board member positions,
    based on the presence of keywords associated with job categories in the sentences.

    Args:
        doc (stanza.Document): A processed stanza.Document object containing sentences.
        all_persons (list): A list of all extracted person names.

    Returns:
        list: A list of lists, each containing different writing forms of names of people who
              potentially hold significant positions. The outer list represents groups of
              potentially significant people, and the inner lists contain various ways of
              writing the names of the same individual.
    """
    pot_per = np.array([])  # people with potential significant position
    people = []  # list of all writing forms of names of people in pot_per

    # Identify people with potential predefined jobs
    for sentence in doc.sentences:
        stripped_sentence = sentence.text.lower().replace(',', ' ').replace('.', ' ')
        if any(re.search(r"\b" + item + r"\b", stripped_sentence)
               for item in (JobKeywords.main_job_all + JobKeywords.sub_job_all)):
            pot_per = np.append(pot_per,
                                [f'{ent.text}' for ent in sentence.ents if ent.type == "PER"])
    
    # postprocessing of identified pot_per
    for pp in pot_per:
        # Remove search words identified as persons
        if pp.lower() in (JobKeywords.main_job_all + JobKeywords.sub_job_all):
            pot_per = pot_per[pot_per != pp]
        # Remove photographers identified as pot_per
        if re.search(r"©[ ]?" + pp + r"\b", doc.text):
            pot_per = pot_per[pot_per != pp]
        # check if length of name is not one
        if len(pp) == 1:
            pot_per = pot_per[pot_per != pp]
    
    # Find duplicates (i.e. J Brown and James Brown) and concatenate all ways of writing
    # the name of one persons that is potentially of interest
    peoples = find_duplicate_persons(list(np.unique(all_persons)))
    for p in peoples:
        if any(item in pot_per for item in p):
            people.append(p)
    
    return people


def relevant_sentences(doc, members):
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
    for sentence in doc.sentences:
        if any(member in sentence.text for member in members):
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
    return sentences, surroundings


def append_p_position(p_position, main, name):
    """Append a person's name to their main position in the list of positions.

    Args:
        p_position (list): A list of sublists representing various position categories, where each sublist
                           starts with the main position's name.
        main (str): The main position name (e.g., 'directeur', 'bestuur', etc.) to which the 'name' should
                    be appended.
        name (str): The name to append to the main position in the 'p_position'.

    Returns:
        list: The updated list 'p_position' with the persons 'name' appended to the appropriate main position.
    """
    for pos in p_position:
        if pos[0] == main:
            pos.extend([name])
    return p_position


def extract_persons(doc, all_persons):
    """Extract ambassadors and board members from a text using a rule-based method.

    This function determines potential ambassadors and board members in a text based on the
    occurrence of specific keywords in (surrounding) sentences where names are mentioned. For board members,
    it identifies the main and sub positions. The main job category is determined based on
    the frequency of keywords in relevant sentences and the surrounding context. Sub job categories
    are determined based on keywords directly adjacent to the person's name. For the position of director,
    additional checks are applied.
    
    The following steps are taken:
    1. Identify names of people with potenitally siginiticant functions
    2. For each name:
     - collect relevant sentences and surrounding sentences
     - determine main job category
     - detemine sub job catergory
     - select 'main' name of a person from a list of found synonyms
     - additional check for persons identified as ambassador
     - set b_position and add people with main cat diredcteur, bestuur or rvt to a list of corresponding potential memebrs. 
    3. For the position of director, an additional filter is applied. They are not considered directors if:
        - the subposition (obtained from words directly surrounding name) is not director.
        - there are two or more potential directors and they do not pass the check director check in the director_check function
        In both cases a 'backup' main cat is determined.
    4. Process the arrays of potential rvt and bestuur members to determine if they are likely true rvt and bestuur members
       respectively


    Args:
        doc (object): A document object containing the text to analyze.
        all_persons (list): A list of unique names identified in the text using a named entity recognition tool.

    Returns:
        tuple: A tuple containing the following arrays:
               - Array of potential ambassadors (ambassadeur).
               - Array of strings of people with significant positions and their main and sub positions, of the form (['name - main pos - sub_ pot'])
               - Array of potential directors and their sub positions (directeur).
               - Array of potential 'Raad van Toezicht' (rvt) members and their sub positions.
               - Array of potential board members and their sub positions (bestuur).
               - Array of potential 'Ledenraad' members and their sub positions.
               - Array of potential 'Kascommissie' members and their sub positions.
               - Array of potential 'Controlecommissie' members and their sub positions.
    """
    ## Define variables
    b_position = np.array([])   # to be filled with strings of the form 'name - main pos - sub_ pot'
    # list of potential directors: name, sub_cat, ft_director, main_cat, backup_sub_cat,fts_bestuur,fts_rvt
    pot_director = []
    pot_rvt = []  # list of potential rvt members
    pot_bestuur = []  # list of potential board member
    # list with sublist of people per position [[position, name, name, ...], [...]]
    p_position = [[p[0]] for p in JobKeywords.main_jobs]

    # identify people to be analysed
    people = identify_potential_people(doc, all_persons)

    for members in people:
        # Determine relevant sentences, main and sub job category, and select main name from synonyms
        sentences, surroundings = relevant_sentences(doc, members)
        m_ft_dbr = determine_main_job(JobKeywords.main_jobs, sentences, surroundings)
        sub_cat = determine_sub_job(members, sentences, m_ft_dbr[0])
        member = members[0]

        # Check for ambassadeur: ambassadeur unlikely if sub_cat is determined
        if m_ft_dbr[0] == 'ambassadeur':
            if sub_cat[0] != '':
                m_ft_dbr[0] = determine_main_job(JobKeywords.main_jobs_no_amb, sentences,
                                                 surroundings)[0]
            else:
                p_position = append_p_position(p_position, m_ft_dbr[0], member)

        # Determine b_position array
        # Add people identified as directeur, bestuur or rvt member to respective 'potential' lists 
        if m_ft_dbr[0] != 'ambassadeur':
            if m_ft_dbr[0] is None:
                continue
            b_position = np.append(b_position, member + ' - ' + m_ft_dbr[0] + ' - ' + sub_cat[0])
            if m_ft_dbr[0] == 'directeur':
                if sub_cat[0] == '':
                    m_ft_dbr[0] = determine_main_job(JobKeywords.main_jobs_backup, sentences,
                                                     surroundings)[0]
                else:
                    m_ft_dbr[0] = determine_main_job(JobKeywords.main_jobs_backup_noamb, sentences,
                                                     surroundings)[0]
                pot_director.append([member, sub_cat[0], m_ft_dbr[1], m_ft_dbr[0], sub_cat[1],
                                     m_ft_dbr[2], m_ft_dbr[3]])
            elif m_ft_dbr[0] == 'rvt':
                pot_rvt.append([member, sub_cat[0], m_ft_dbr[3]])
            elif m_ft_dbr[0] == 'bestuur':
                pot_bestuur.append([member, sub_cat[0], m_ft_dbr[2]])
            elif m_ft_dbr[0] in JobKeywords.main_job[:-1]:
                p_position = append_p_position(p_position, m_ft_dbr[0], member)

    # Additional checks for potential directeur position
    pot_director = np.array(pot_director, dtype=object)
    if len(pot_director) > 1:
        (b_position, pot_rvt, pot_bestuur, p_position) = \
            director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position)
    elif len(pot_director) == 1:
        p_position = append_p_position(p_position, 'directeur', pot_director[0][0])
    
    # Determine if people initially identified as rvt memeber are likely true rvt members
    pot_rvt = np.array(pot_rvt, dtype=object)
    b_position, p_position = check_rvt(pot_rvt, b_position, p_position)
    # Determine if people initially identified as bestuur memeber are likely true bestuur members
    pot_bestuur = np.array(pot_bestuur, dtype=object)
    b_position, p_position = check_bestuur(pot_bestuur, b_position, p_position)

    return (array_p_position(p_position, 'ambassadeur'),
            b_position,
            array_p_position(p_position, 'directeur'),
            array_p_position(p_position, 'rvt'),
            array_p_position(p_position, 'bestuur'),
            array_p_position(p_position, 'ledenraad'),
            array_p_position(p_position, 'kascommissie'),
            array_p_position(p_position, 'controlecommissie'))


def array_p_position(p_position, position):
    """Returns an array made out of sublist of the list p_position.
    
    This function returns an array made out of sublist of the list p_position. The sublist must start with
    the term position.

    Args:
        p_position (list): A list of sublists, each of which contains a main job category and 
        names of people for that job if any
        position (str): a main job position for which the associated names should be extracted.
    
    Returns:
        numpy.ndarray: An array containing the names associated with the specified 'position'. If no sublist
                       with the given 'position' is found, an empty array is returned.
    """
    return np.array([i[1:] for i in p_position if i[0] == position][0])


def director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position):
    """Check potential directors and update their positions if necessary.

    A potential director is not considered a director if either:
        - there are five or more potential directors, and they are mentioned in director context <= 3 times (ft),
        while the maximum mentioning is > 5.
        - They are mentioned in director context <= 1 time (ft), while the maximum mentioning is > 2.
        - The subposition (obtained from words directly surrounding the name) is not 'directeur'.
    
    In that case:
        1. remove person from b_position
        2. use the backup main category and update pot_rvt/pot_bestuur/p_position accordingly
        3. if the new main cat is not ambassador, set the sub category to the one already found.
           Unless this was 'director', then use the backup sub position.
        4. update b_position with the new main and sub category
    
    Otherwise, add the pot_director to p_position.

    Args:
        pot_director (numpy.ndarray): An array of potential directors and associated information.
        b_position (np.ndarray): An array in which each element has the form 'name - main position - sub position'.
        pot_rvt (np.array of lists): An array of lists containing potential 'rvt' (Raad van Toezicht) members.
                        Each list contains the name of the person, the associated 'rvt' position,
                        and the count of 'rvt' positions held by that person.
        pot_bestuur (np.array of lists): An array of lists containing potential bestuur members.
                        Each list contains the name of the person, the associated bestuur position,
                        and the count of bestuur positions held by that person.
        p_position (list): List of position categories and associated names.

    Returns:
        tuple: A tuple containing the following updated arrays/lists:
               - Array of people with significant positions + main and sub positions.
               - List of potential 'Raad van Toezicht' (rvt) members and their sub positions.
               - List of potential board members and their sub positions.
               - List of position categories and associated names.
    """
    # Loop through potential directors
    for i in range(len(pot_director)):
        if (all([len(pot_director) > 5, pot_director[i, 2] <= 3,
                int(max(pot_director[:, 2])) > 5]) or
                all([pot_director[i, 2] <= 1, int(max(pot_director[:, 2])) > 2]) or
                (pot_director[i, 1] != 'directeur')):
            # if condition is met remove from b_position
            b_position = b_position[b_position != (pot_director[i, 0] + ' - directeur - ' +
                                                   pot_director[i, 1])]
            # Use backup main cat instad of directeur function and update pot_rvt/pot_bestuur/p_position accordingly
            if str(pot_director[i, 3]) == 'rvt':
                pot_rvt.append([pot_director[i, 0], 
                                pot_director[i, 4], 
                                pot_director[i, 6]])
            elif str(pot_director[i, 3]) == 'bestuur':
                pot_bestuur.append([pot_director[i, 0], 
                                    pot_director[i, 4],
                                    pot_director[i, 5]])
            elif str(pot_director[i, 3]) in JobKeywords.main_job:
                p_position = append_p_position(p_position, str(pot_director[i, 3]),
                                               pot_director[i, 0])
            
            # Specifiy subposition, but not if the main is abassadeur or None
            if pot_director[i, 3] != 'ambassadeur' and pot_director[i, 3] is not None:
                subf = str(pot_director[i, 4])
                # Update b_position according to backup
                b_position = np.append(b_position, (str(pot_director[i, 0]) + ' - ' +
                                       str(pot_director[i, 3]) + ' - ' + subf))
        else:
            # if condition is not met add directeur to p_position
            p_position = append_p_position(p_position, 'directeur', pot_director[i, 0])
    return b_position, pot_rvt, pot_bestuur, p_position


def check_rvt(pot_rvt, b_position, p_position):
    """Determine whether potential rvt memebers can be considered true rvt memebers.

    This function determines whether potential rvt members ('pot_rvt') can be considered true rvt memebers,
    updating 'b_position' and 'p_position' accordingly.

    Steps:
    Loop through the pot_rvt array and make the following decisions:
    1. if there are more than 12 memebers in the array of potential rvt memebrs, remove the member from b_position 
       if it has a frequency count <= 3.
    2. if there are more than 8 members in the array of potential rvt members, remove the member from if it has a frequency count of 1.
    3. Otherwise, add the pot_rvt member to p_position
    
    Args:
        pot_rvt (np.array of lists): An array of lists containing potential 'rvt' (Raad van Toezicht) members.
                        Each list contains the name of the person, the associated 'rvt' position,
                        and the count of 'rvt' positions held by that person.
        b_position (np.ndarray): An array in which each element has the form 'name - main position - sub position'.
        p_position (list of lists): A list of sublists, each of which contains a main job category and 
        names of people for that job if any.

    Returns:
        tuple: A tuple containing two elements:
               - Updated b_positions (numpy.ndarray) after removing certain 'rvt' members based on
                 the specified conditions.
               - Updated p_position categories and associated names after adding any 'rvt' positions
                 that meet the conditions.
    """
    for rvt in enumerate(pot_rvt):
        if len(pot_rvt) >= 12 and rvt[1][2] <= 3:
            b_position = b_position[b_position != rvt[1][0] + ' - rvt - ' + rvt[1][1]]
        elif len(pot_rvt) >= 8 and rvt[1][2] == 1:
            b_position = b_position[b_position != rvt[1][0] + ' - rvt - ' + rvt[1][1]]
        else:
            p_position = append_p_position(p_position, 'rvt', rvt[1][0])
    return b_position, p_position


def check_bestuur(pot_bestuur, b_position, p_position):
    """Determine whether potential bestuur memebers can be considered true bestuur memebers.

    This function determines whether potential bestuur members ('pot_bestuur') can be considered true bestuur members,
    updating 'b_position' and 'p_position' accordingly.

    Steps:
    Loop through the pot_bestuur array and make the following decisions:
    1. if there are more than 12 members in the array of potential bestuur memebrs, remove the member from b_position 
       if it has a frequency count <= 3.
    2. if there are more than 8 members in the array of potential bestuur members, remove the member from if it has a frequency count of 1.
    3. Otherwise, add the pot_bestuur member to p_position
    
    Args:
        pot_bestuur (np.array of lists): An array of lists containing potential bestuur members.
                        Each list contains the name of the person, the associated bestuur position,
                        and the count of bestuur positions held by that person.
        b_position (np.ndarray): An array in which each element has the form 'name - main position - sub position'.
        p_position (list of lists): A list of sublists, each of which contains a main job category and 
        names of people for that job if any.

    Returns:
        tuple: A tuple containing two elements:
               - Updated b_positions (numpy.ndarray) after removing certain bestuur members based on
                 the specified conditions.
               - Updated p_position categories and associated names after adding any bestuur positions
                 that meet the conditions.
    """
    for bestuur in enumerate(pot_bestuur):
        if len(pot_bestuur) >= 12 and bestuur[1][2] <= 3:
            b_position = b_position[b_position != (bestuur[1][0] + ' - bestuur - ' +
                                                   bestuur[1][1])]
        elif len(pot_bestuur) >= 8 and bestuur[1][2] == 1:
            b_position = b_position[b_position != (bestuur[1][0] + ' - bestuur - ' +
                                                   bestuur[1][1])]
        else:
            p_position = append_p_position(p_position, 'bestuur', bestuur[1][0])
    return b_position, p_position
