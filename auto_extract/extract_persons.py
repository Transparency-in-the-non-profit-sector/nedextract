"""Class and functions to extract information about people mentioned in a text.

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


class JobKeywords:
    """Class that stores lists of words and categories for main and sub jobs/company positions.

    This class provides lists of keywords and categories associated with main and sub jobs.
    The keywords are used for matching job titles and determining job categories in various contexts.
    """

    # words and categories for main jobs
    directeur = ['directeur', 'directrice', 'directie', 'bestuurder', 'directeuren',
                 'directeur-bestuurder']
    bestuur = ['bestuur', 'db', 'ab', 'rvb', 'bestuurslid', 'bestuursleden', 'hoofdbestuur',
               'bestuursvoorzitter']
    rvt = ['rvt', 'raad van toezicht', 'raad v. toezicht', 'auditcommissie', 'audit commissie']
    ledenraad = ['ledenraad', 'ledenraadsvoorzitter', 'ledenraadpresidium']
    kascommissie = ['kascommissie']
    controlecommissie = ['controlecommissie']
    ambassadeur = ['ambassadeur', 'ambassadeurs']
    main_job_all = (directeur + rvt + bestuur + ledenraad + kascommissie + controlecommissie
                    + ambassadeur)
    main_jobs = [directeur, bestuur, rvt, ledenraad, kascommissie, controlecommissie, ambassadeur]
    main_job = [mj[0] for mj in main_jobs]
    main_jobs_no_amb = [directeur, bestuur, rvt, ledenraad, kascommissie, controlecommissie]
    main_jobs_backup = [bestuur, rvt, ledenraad, kascommissie, controlecommissie, ambassadeur]
    main_jobs_backup_noamb = [bestuur, rvt, ledenraad, kascommissie, controlecommissie]

    # words and categories for sub jobs
    vicevoorzitter = ['vice-voorzitter', 'vicevoorzitter', 'vice voorzitter']
    voorzitter = ['voorzitter']
    penningmeester = ['penningmeester']
    secretaris = ['secretaris', 'secretariaat']
    commissaris = ['commissaris', 'commissariaat']
    lid = ['lid', 'leden', 'bestuurslid', 'bestuursleden']
    adviseur = ['adviseur', 'adviseurs']
    sub_job_all = (directeur + vicevoorzitter + voorzitter + penningmeester + secretaris +
                   commissaris + lid + adviseur)
    sub_jobs = [directeur, vicevoorzitter, voorzitter, penningmeester, secretaris, commissaris,
                lid, adviseur]
    sub_job = np.array([sj[0] for sj in sub_jobs])

class Tussenvoegsels:
    """This class stores a list of prefixes commonly found in the Netherlands.

    List of tussenvoegsels is taken from:
    https://publicaties.rvig.nl/dsresource?objectid=c5f84baf-ba01-41ef-a6a0-97cebec1c2d3&type=pdf
    One-letter tussenvoegsels have been omitted. 
    """

    # Common infixes found in the Netherlands
    tussenvoegsels = ["'s", "'m", "'t", "aan", "af", "al", "am", "auf", "ben", "bij", "bin",
                      "boven", "da", "dal", "dal'", "dalla", "das", "de", "deca", "degli", "dei",
                      "del", "della", "dem", "den", "der", "des", "di", "die", "do", "don", "dos",
                      "du", "el", "gen", "het", "im", "in", "la", "las", "le", "les", "lo", "los",
                      "of", "onder", "op", "over", "te", "ten", "ter", "tho", "thoe", "thor", "to",
                      "toe", "tot", "uijt", "uit", "unter", "van", "ver", "vom", "von", "voor",
                      "vor", "zu", "zum", "zur"]

class Titles:
    """Class that stores a list of common (abbreviated) titles.
    
    The lists contains titles and abbreviated titles ofter used in combination with their name.
    """

    titles = ['prof.', 'dr.', 'mr.', 'ir.', 'drs.', 'bacc.', 'kand.', 'dr.h.c.', 'ing.', 'bc.',
              'phd', 'phd.', 'dhr.', 'mevr.', 'mw.', 'ds.', 'mgr.', 'mevrouw', 'meneer', 'jhr.']


def abbreviate(name: str, n_ab: int):
    """Function to abbreviate names
    
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
    """Sort names in a list
    
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
    """ Function to find duplicate names.

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
    """return the summed total of occurrences of search words in text."""
    fulltext = np.array2string(text, separator=' ')
    fulltext = re.sub(r"[\[\]']", '', fulltext)
    fulltext = fulltext.replace('vice voorzitter', 'vicevoorzitter')
    fulltext = fulltext.replace('vice-voorzitter', 'vicevoorzitter')
    totalcount = 0
    totalcount_sentence = 0
    for item in search_words:
        escape_item = re.escape(item)
        totalcount += sum(1 for _ in re.finditer(r'\b' + escape_item + r'\b', fulltext))
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
    """Determine main job category based on:
    The most occuring category in the direct text based on sentence frequency (fs, i.e. number of
    sentences in which category+name is found)
    If none can be identified, or there is a tie: try based on sentence frequency from surrounding
    sentences (fss).
    If none can be identified: try based on overall frequency in main text
    If non can be identified: try based on overall frequency in surrounding text
    If still none can be identified, eliminate name from board"""
    fs = np.empty(len(main_jobs))  # sentence frequency direct sentences
    fss = np.empty(len(main_jobs))  # sentence frequency incl. surrounding sentences
    ft = np.empty(len(main_jobs))  # total frequency direct sentences
    fts = np.empty(len(main_jobs))  # total frequency incl. surrounding sentences
    main_job = np.array([mj[0] for mj in main_jobs])
    for m, m_j in enumerate(main_jobs):
        ft[m], fs[m] = count_occurrence(sentences, m_j)
        fts[m], fss[m] = count_occurrence(surroundings, m_j)
    if (max(fs) > 0 and len(np.where(fs == max(fs))[0]) == 1):
        main_cat = main_job[np.where(fs == max(fs))[0]][0]
    elif (max(fss) > 0 and len(np.where(fss == max(fss))[0]) == 1):
        main_cat = main_job[np.where(fss == max(fss))[0]][0]
    elif (max(ft) > 0 and len(np.where(ft == max(ft))[0]) == 1):
        main_cat = main_job[np.where(ft == max(ft))[0]][0]
    elif (max(fts) > 0 and len(np.where(fts == max(fts))[0]) == 1):
        main_cat = main_job[np.where(fts == max(fts))[0]][0]
    elif max(fs) > 0:
        main_cat = main_job[np.where(fs == max(fs))[0]][0]
    elif max(fss) > 0:
        main_cat = main_job[np.where(fss == max(fss))[0]][0]
    else:
        main_cat = None
    ft_director = ft[np.where(main_job == 'directeur')]
    fts_bestuur = fts[np.where(main_job == 'bestuur')]
    fts_rvt = fts[np.where(main_job == 'rvt')]
    return [main_cat, ft_director, fts_bestuur, fts_rvt]


def determine_sub_job(members, sentences, main_cat):
    c_sub_job = np.array([])
    surrounding_w = surrounding_words(sentences, members)
    if surrounding_w.size > 0:
        for sj in JobKeywords.sub_jobs:
            c_sub_job = np.append(c_sub_job, count_occurrence(surrounding_w, sj)[0])
    else:
        c_sub_job = np.append(c_sub_job, 0)
    if max(c_sub_job) > 0 and len(np.where(c_sub_job == max(c_sub_job))[0]) == 1:
        sub_cat = backup_sub_cat = JobKeywords.sub_job[np.where(c_sub_job == max(c_sub_job))[0]][0]
        if main_cat == 'directeur' and sub_cat != 'directeur':
            sub_cat = ''
        elif main_cat == 'directeur' and sub_cat == 'directeur':
            backup_sub_cat = ''
    else:
        sub_cat = backup_sub_cat = ''
    return [sub_cat, backup_sub_cat]


def identify_potential_people(doc, all_persons):
    '''identify potential ambassadors and board members based on keywords in sentences'''
    pot_per = np.array([])  # people with potential significant position
    people = []  # list of all writing forms of names of people in pot_per
    for sentence in doc.sentences:
        stripped_sentence = sentence.text.lower().replace(',', ' ').replace('.', ' ')
        if any(re.search(r"\b" + item + r"\b", stripped_sentence)
               for item in (JobKeywords.main_job_all + JobKeywords.sub_job_all)):
            pot_per = np.append(pot_per,
                                [f'{ent.text}' for ent in sentence.ents if ent.type == "PER"])
    for pp in pot_per:
        # Remove search words identified as persons
        if pp.lower() in (JobKeywords.main_job_all + JobKeywords.sub_job_all):
            pot_per = pot_per[pot_per != pp]
        # Remove photographers identified as pot_per
        if re.search(r"©[ ]?" + pp + r"\b", doc.text):
            pot_per = pot_per[pot_per != pp]
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
    '''identify all sentences containing a specific person and those directly surrounding them'''
    prevsentence = ''
    sentences = np.array([])
    surroundings = np.array([])
    need_next_sentence = False
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
    for pos in p_position:
        if pos[0] == main:
            pos.extend([name])
    return p_position


def extract_persons(doc, all_persons):
    ''' Determine from a text which persons (identified with stanza) are ambassadors or
    board members, using a rule based method. Identify potential ambassadors and board members
    based on key words occuring in sentences in which a name is mentioned. Next, for board members,
    a main and sub position are identified (if possible). The rules for main position are based on
    the frequency of key words occuring in sentences in which names are mentioned, or the sentences
    surrounding those in which names are mentioned.
    Sub positions are determined based on the frequency of key words directly next to the name.
    #
    For the position of director, an additional filter is applied: if more than 2 persons are
    identified as director, persons are not considered a director if:
    - they are mentioned in director context < 2 (ft), while the max mentioning is > 2
    - the subposition (obtained from words directly surrounding name) is not director.'''
    b_position = np.array([])   # people with significant positions + main and sub position
    # potential directors: name, sub_cat, ft_director, main_cat, backup_sub_cat,fts_bestuur,fts_rvt
    pot_director = []
    pot_rvt = []  # list of potential rvt members
    pot_bestuur = []  # list of potential board member
    p_position = [[p[0]] for p in JobKeywords.main_jobs]

    people = identify_potential_people(doc, all_persons)

    # Determine most likely position of board members
    # Collect all sentences containing a particular board member name +
    # the sentences before and after the occurrences
    for members in people:
        # Determine relevant sentences
        sentences, surroundings = relevant_sentences(doc, members)
        # Determine main job category
        m_ft_dbr = determine_main_job(JobKeywords.main_jobs, sentences, surroundings)
        # Determine sub job category based on positions mentioned directely before or after name
        sub_cat = determine_sub_job(members, sentences, m_ft_dbr[0])
        # Add final results
        member = members[0]

        if m_ft_dbr[0] == 'ambassadeur':
            # ambassadeur unlikely if sub_cat is determined
            if sub_cat[0] != '':
                m_ft_dbr[0] = determine_main_job(JobKeywords.main_jobs_no_amb, sentences,
                                                 surroundings)[0]
            else:
                p_position = append_p_position(p_position, m_ft_dbr[0], member)
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

    # **** Additional checks
    pot_director = np.array(pot_director, dtype=object)
    if len(pot_director) > 1:
        (b_position, pot_rvt, pot_bestuur, p_position) = director_check(pot_director,
                                                                        b_position,
                                                                        pot_rvt,
                                                                        pot_bestuur,
                                                                        p_position)
    elif len(pot_director) == 1:
        p_position = append_p_position(p_position, 'directeur', pot_director[0][0])
    # If there are more than 10 people in rvt or bestuur, remove them if they have an fts <= 3
    # and do not have an sub position assigned
    pot_rvt = np.array(pot_rvt, dtype=object)
    b_position, p_position = check_rvt(pot_rvt, b_position, p_position)

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
    '''returns an array made out of sublist of the list p_position. The sublist must start with
    the term position'''
    return np.array([i[1:] for i in p_position if i[0] == position][0])


def director_check(pot_director, b_position, pot_rvt, pot_bestuur, p_position):
    '''If there are >= 2 potential directors, a potential director is not considered a director if:
    - they are mentioned in director context < 2 (ft), while the max mentioning is > 2
    - or if the subposition (obtained from words directly surrounding name) is not director.
    In this case, use the second highest scoring main category instead'''
    for i in range(len(pot_director)):
        if (all([len(pot_director) > 5, pot_director[i, 2] <= 3,
                int(max(pot_director[:, 2])) > 5]) or
                all([pot_director[i, 2] <= 1, int(max(pot_director[:, 2])) > 2]) or
                (pot_director[i, 1] != 'directeur')):
            b_position = b_position[b_position != (pot_director[i, 0] + ' - directeur - ' +
                                                   pot_director[i, 1])]
            # Use backup
            if str(pot_director[i, 3]) == 'rvt':
                pot_rvt.append([pot_director[i, 0], pot_director[i, 1], pot_director[i, 6]])
            elif str(pot_director[i, 3]) == 'bestuur':
                pot_bestuur.append([pot_director[i, 0], pot_director[i, 1],
                                    pot_director[i, 5]])
            elif str(pot_director[i, 3]) in JobKeywords.main_job:
                p_position = append_p_position(p_position, str(pot_director[i, 3]),
                                               pot_director[i, 0])
            if pot_director[i, 3] != 'ambassadeur' and pot_director[i, 3] is not None:
                if str(pot_director[i, 1]) != 'directeur':
                    subf = str(pot_director[i, 1])
                else:
                    subf = ''
                b_position = np.append(b_position, (str(pot_director[i, 0]) + ' - ' +
                                       str(pot_director[i, 3]) + ' - ' + subf))
        else:
            p_position = append_p_position(p_position, 'directeur', pot_director[i, 0])
    return b_position, pot_rvt, pot_bestuur, p_position


def check_rvt(pot_rvt, b_position, p_position):
    for rvt in enumerate(pot_rvt):
        if len(pot_rvt) >= 12 and rvt[1][2] <= 3:
            b_position = b_position[b_position != rvt[1][0] + ' - rvt - ' + rvt[1][1]]
        elif len(pot_rvt) >= 8 and rvt[1][2] == 1:
            b_position = b_position[b_position != rvt[1][0] + ' - rvt - ' + rvt[1][1]]
        else:
            p_position = append_p_position(p_position, 'rvt', rvt[1][0])
    return b_position, p_position


def check_bestuur(pot_bestuur, b_position, p_position):
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
