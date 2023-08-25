"""This file contains functions that are used by exxtract_related_orgs to determine wether the found orgs are true orgs."""
import re
import numpy as np
from nedextract.utils.keywords import Org_Keywords


class OrganisationExtraction:
    """This class contains functions used to perform checks on potential organisations.

    It contains the functions:
    - keyword_check
    - check_single_orgs
    - individual_org_check
    - percentage_considered_org
    - strip_function_of_entity
    - count_number_of_mentions
    - part_of_other
    """
    
    def __init__(self, nlp = None, doc = None, org: str = None, #pylint: disable=too-many-arguments'
                 orgs: np.array = None, counts: np.array = None, 
                 true_orgs: list = None, final = None): 
        """Define class variables."""
        self.nlp = nlp
        self.doc = doc
        self.org = org
        self.true_orgs = true_orgs
        self.orgs = orgs
        self.counts = counts
        self.decision = final

    def keyword_check(self, final: bool = None, org: str = None):
        """Check if org is likely to be or not be an organisation based on keywords.
        
        This function contains a decision tree that determines if it is likely that a candidate organisation is a
        true orginasation, taking into account the presence of 'organisational' keywords.

        Args:
            final (bool): The current decision status.
            org (str): The orginasation name to be checked for keyword presence.

        Returns:
            bool: The updated decision status based on keyword presence.
        """
        # Set initial values if not defined in function args
        if not final:
            final = self.decision
        if not org:
            org = self.org
        
        # decision is true if org contains a keyword, unless org is only a keyword
        for kw in Org_Keywords.true_keys:
            if len(re.findall(kw, org.lower())) > 0:
                final = True
                if len(org) == len(kw):
                    final = False

        # potential decision update: true if org contains a keyword as standalone word, unless it is the only word
        for kw in Org_Keywords.true_keys_cap:
            if len(re.findall((r"\b" + kw + r"\b"), org)) > 0:
                final = True
                if len(org) == len(kw):
                    final = False

        # decision is still false if the org contains a 'false' keyword, a keyword indicating that the name is not an org
        if final is True:
            for kw in Org_Keywords.false_keys:
                if len(re.findall(kw, org.lower())) > 0:
                    final = False
            if org.lower() in Org_Keywords.false_keys_s:
                final = False
        return final


    def check_single_orgs(self):
        """Append org to true list if it passes the keyword check and is not part of other org.
        
        This function appends an org to true_orgs list if part_of_other
        is false or true respectively, and it is not blocked by the keyword check.
        
        Args:
            org (str): The orgination name to be checked for keyword presence.
            true_orgs: list of organisations that are already found to be likely true
            doc: the stanza processes text

        Returns:
            true_orgs: The updated true_orgs list.
        """
        true_orgs = self.true_orgs
        org = self.org
        final = True
        keyword = self.keyword_check(final, org)
        poo = OrganisationExtraction.part_of_other(true_orgs, org, self.doc)

        if poo is False and keyword is True:
            true_orgs.append(org)
        return true_orgs


    @staticmethod
    def part_of_other(orgs: list, org: str, doc):
        """Check if a member of orgs is part of the org string.

        This function checks if an orginasations 'o' in the list orgs is part of the input 'org'. 
        If it is and the matching 'o' has enough characters, is common enough in the analysed test,
        and it is not the cases that the only difference is the presence of a keyword org, return True
        
        Args:
            orgs: list of organisations
            org (str): The orgination name to be checked for keyword presence.
            doc: stanza processed text in which to look for organisations.
    
        Returns:
            is_part (bool): returns true if a member of orgs in a part of org.
        """
        oe = OrganisationExtraction()
        is_part = False

        for o in orgs:
            if org != o and o in org and len(o) > 5:
                n_orgs = len(re.findall(r"\b" + o + r"\b", doc.text))
                if n_orgs > 5:
                    kw_final = False
                    kw_o = oe.keyword_check(final=kw_final, org=o)
                    kw_org = oe.keyword_check(final=kw_final, org=org)
                    if not (kw_o is False and kw_org is True):
                        is_part = True
        return is_part


    def individual_org_check(self):
        """Check if org term individually is considered an NER ORG.
        
        Check if an potential ORG is considered and ORG if just that name is analysed by Stanza NER.
        (Without the context of any sentences)
        
        Args:
            org (str): The orgination name to be checked for keyword presence.
            nlp (stanza.pipeline): the stanza pipeline used to analyse texts

        Returns: 
            is_org(bool): true if the test passes
        """
        org = self.org
        doc_o = self.nlp(org)
        o_t = [f'{ent.text}' for ent in doc_o.ents if ent.type == "ORG"]
        is_org = bool(len(o_t) == 1 and org in o_t)
        return is_org


    def percentage_considered_org(self):
        """Determine the percenatge of mention cases for which the org was considered an NER ORG.

        This function identifies all mentions of the org within the text. Then calculate in what percentage of the
        total number of mentions, the org is identified as org by NER.
        
        Args:
            doc: stanza processed text in which to look for organisations.
            org (str): The orgination name to be checked for keyword presence.
            orgs (np.array): array of organisations

        Returns:
            percentage(float): percentage of cases in which org was identified as org
            n_orgs(int): number if mentions within the text
        """
        org = self.org
        orgs = self.orgs
        n_orgs = self.count_number_of_mentions(org=org)

        if n_orgs >= 1 and org in orgs:
            n_orgs_found = self.counts[orgs == org][0]
            percentage = n_orgs_found/float(n_orgs)*100.
        elif org in orgs:
            percentage = -10
        else:
            percentage = 0.
        return percentage, n_orgs


    def strip_function_of_entity(self):
        """Strip the work roles of an potential org.
        
        This function removes terms indicating a persons role within a organisation off the organisation's name.

        Example: if fed with
        "Lid van de Raad van Advies bij Bedrijfsnaam", only "Bedrijfsnaam" would be returned.
        
        Args:
            org (str): The orgination name to be checked for keyword presence.

        Returns:
            org (str): The orgination name from which the role is removed if found.
        """         
        org = self.org
        
        for p in Org_Keywords.position:
            org = re.sub('^' + p + r"\b", '', org, flags=re.IGNORECASE).lstrip()

        for lv in Org_Keywords.lidwoord_voorzetsels:
            org = re.sub('^' + lv, '', org).lstrip()

        for p in Org_Keywords.position:
            org = re.sub('^' + p + r"\b", '', org, flags=re.IGNORECASE).lstrip()

        for lv in Org_Keywords.lidwoord_voorzetsels:
            org = re.sub('^' + lv, '', org).lstrip()

        for r in Org_Keywords.raad:
            org = re.sub('^' + r + r"\b", '', org, flags=re.IGNORECASE).lstrip()

        for lv in Org_Keywords.lidwoord_voorzetsels:
            org = re.sub('^' + lv, '', org).lstrip()

        for c in Org_Keywords.commissie:
            org = re.sub('^' + c + r"\b", '', org, flags=re.IGNORECASE).lstrip()

        for lv in Org_Keywords.lidwoord_voorzetsels:
            org = re.sub('^' + lv, '', org).lstrip()

        for f in Org_Keywords.functies:
            org = re.sub(f + '$', '', org, flags=re.IGNORECASE).rstrip()
        return org


    def count_number_of_mentions(self, org: str = None, doc = None):
        """Count the number of mentions of org in the text, taking into account word boundaries.
        
        Args:
            org (str): The orgination name to be checked for keyword presence.
            doc: stanza processed text in which to look for organisations.

        Returns:
            n_counts (int): number of mentions found.
        """
        if org is None: org=self.org
        if doc is None: doc=self.doc

        if '-' not in org:
            n_counts = len(re.findall(r"\b" + org + r"\b", doc.text.replace('-', '')))
        else:
            n_counts = len(re.findall(r"\b" + org + r"\b", doc.text))
        return n_counts
