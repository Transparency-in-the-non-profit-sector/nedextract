"""This file contains the class NameAnalysis."""
import itertools
import re
import numpy as np
from classes.keywords import Titles
from classes.keywords import Tussenvoegsels
from fuzzywuzzy import fuzz


class NameAnalysis:
    """This class contains functions used to analyse names.

    It contains the functions:
    - abbreviate
    - get_tsr
    - strip_names_from_title
    - sort_select_name
    - find_similar_names
    - find_duplicate_persons
    """

    def __init__(self, names: list):
        """Define class variables."""
        self.pnames = names

    @staticmethod
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

    @staticmethod
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
                tsr = np.append(tsr, fuzz.token_set_ratio(p_i, NameAnalysis.abbreviate(p_j, n_initials)))
            token_set_ratio = max(tsr)
            req_score = 95

        elif p_j.count('.') >= 1:
            tsr = np.array(0)
            for n_initials in range(1, p_j.count('.') + 1):
                tsr = np.append(tsr, fuzz.token_set_ratio(NameAnalysis.abbreviate(p_i, n_initials), p_j))
            token_set_ratio = max(tsr)
            req_score = 95

        # if name is normal
        else:
            req_score = 90
        return token_set_ratio, req_score

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def find_similar_names(persons: list):
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
            persons (List): A list of names to be grouped.

        Returns:
            List: A list of lists, where each inner list contains similar names grouped together.
        """
        outnames = []
        p, p_remove = NameAnalysis.strip_names_from_title(persons)
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
                    token_set_ratio, req_score = NameAnalysis.get_tsr(p[i], p[j])
                    # check if required score is exceeded
                    if token_set_ratio >= req_score:
                        same_name.extend([j_names])
                same_name = NameAnalysis.sort_select_name(same_name)
            outnames.append(same_name)
        outnames.sort(key=len, reverse=True)

        # remove duplicate lists of names
        for i in range(len(outnames)-1, -1, -1):
            if any(all(elem in names for elem in outnames[i]) for names in outnames[0:i]):
                outnames.pop(i)
        return outnames


    def find_duplicate_persons(self):
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
        persons = self.pnames
        outnames = NameAnalysis.find_similar_names(persons)

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
            outnames = NameAnalysis.find_similar_names(persons)

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
