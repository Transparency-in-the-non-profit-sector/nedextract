"""Functions to extract information about people mentioned in a Dutch text.

In general, the functions try to obtain for each name, what the function of that person is according to the text.
Various functions are defined that try to reduce the number of duplicate names and determine the correct function
of the persons based on various (con)textual challenges.

Functions:

- identify_potential_people
- extract_persons
- director_check
- check_rvt
- check_bestuur
- array_p_position
- append_p_position
"""

import re
import numpy as np
from nedextract.utils.determinejobs import DetermineJobs
from nedextract.utils.keywords import JobKeywords
from nedextract.utils.nameanalysis import NameAnalysis


def identify_potential_people(doc, all_persons: list):
    """Identify potential ambassadors and board members based on keywords in sentences.

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
    na = NameAnalysis(list(np.unique(all_persons)))
    peoples = na.find_duplicate_persons()
    for p in peoples:
        if any(item in pot_per for item in p):
            people.append(p)

    return people


def extract_persons(doc, all_persons: list):
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
               - Array of strings of people with significant positions and their main and sub positions, of the form
                 (['name - main pos - sub_ pot'])
               - Array of potential directors and their sub positions (directeur).
               - Array of potential 'Raad van Toezicht' (rvt) members and their sub positions.
               - Array of potential board members and their sub positions (bestuur).
               - Array of potential 'Ledenraad' members and their sub positions.
               - Array of potential 'Kascommissie' members and their sub positions.
               - Array of potential 'Controlecommissie' members and their sub positions.
    """
    # Define variables
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
        member = members[0]
        jobsdetermination = DetermineJobs(members=members, doc=doc,
                                          main_jobs=JobKeywords.main_jobs, p_position=p_position)
        m_ft_dbr = jobsdetermination.determine_main_job()
        jobsdetermination.main_jobs = m_ft_dbr[0]
        sub_cat = jobsdetermination.determine_sub_job()

        # Check for ambassadeur: ambassadeur unlikely if sub_cat is determined
        if m_ft_dbr[0] == 'ambassadeur':
            if sub_cat[0] != '':
                jobsdetermination.main_jobs = JobKeywords.main_jobs_no_amb
                m_ft_dbr[0] = jobsdetermination.determine_main_job()[0]
            else:
                p_position = append_p_position(p_position, m_ft_dbr[0], member)

        # Determine b_position array: Add people identified as directeur, bestuur or rvt member to respective 'potential' lists
        if m_ft_dbr[0] != 'ambassadeur':
            if m_ft_dbr[0] is None:
                continue
            b_position = np.append(b_position, member + ' - ' + m_ft_dbr[0] + ' - ' + sub_cat[0])
            if m_ft_dbr[0] == 'directeur':
                if sub_cat[0] == '':
                    jobsdetermination.main_jobs = JobKeywords.main_jobs_backup
                    m_ft_dbr[0] = jobsdetermination.determine_main_job()[0]
                else:
                    jobsdetermination.main_jobs = JobKeywords.main_jobs_backup_noamb
                    m_ft_dbr[0] = jobsdetermination.determine_main_job()[0]
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


def director_check(pot_director: np.array, b_position: np.array,
                   pot_rvt: np.array, pot_bestuur: np.array, p_position: list):
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
        pot_director (numpy.array): An array of potential directors and associated information.
        b_position (np.array): An array in which each element has the form 'name - main position - sub position'.
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
                pot_director[:, 2].max() > 5]) or
                all([pot_director[i, 2] <= 1, pot_director[:, 2].max() > 2]) or
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


def check_rvt(pot_rvt: np.array, b_position: np.array, p_position: list):
    """Determine whether potential rvt memebers can be considered true rvt memebers.

    This function determines whether potential rvt members ('pot_rvt') can be considered true rvt memebers,
    updating 'b_position' and 'p_position' accordingly.

    Steps:
    Loop through the pot_rvt array and make the following decisions:
    1. if there are more than 12 memebers in the array of potential rvt memebrs, remove the member from b_position
       if it has a frequency count <= 3.
    2. if there are more than 8 members in the array of potential rvt members, remove the member from if it has a frequency
       count of 1.
    3. Otherwise, add the pot_rvt member to p_position

    Args:
        pot_rvt (np.array of lists): An array of lists containing potential 'rvt' (Raad van Toezicht) members.
                        Each list contains the name of the person, the associated 'rvt' position,
                        and the count of 'rvt' positions held by that person.
        b_position (np.array): An array in which each element has the form 'name - main position - sub position'.
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


def check_bestuur(pot_bestuur: np.array, b_position: np.array, p_position: list):
    """Determine whether potential bestuur memebers can be considered true bestuur memebers.

    This function determines whether potential bestuur members ('pot_bestuur') can be considered true bestuur members,
    updating 'b_position' and 'p_position' accordingly.

    Steps:
    Loop through the pot_bestuur array and make the following decisions:
    1. if there are more than 12 members in the array of potential bestuur memebrs, remove the member from b_position
       if it has a frequency count <= 3.
    2. if there are more than 8 members in the array of potential bestuur members, remove the member from if it has a
       frequency count of 1.
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


def array_p_position(p_position: list, position: str):
    """Return an array made out of sublist of the list p_position.

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


def append_p_position(p_position: list, main: str, name: str):
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
