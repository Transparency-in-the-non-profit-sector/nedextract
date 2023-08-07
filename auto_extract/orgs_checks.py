"""
Functions:
- percentage_considered_org
- strip_function_of_entity
- count_number_of_mentions
- part_of_other
- keyword_check
- check_single_orgs
- single_org_check
"""
import re
from keywords import Org_Keywords


class OrgExtraction:
    def __init__(self) -> None:
        pass

    def keyword_check(final: bool, org: str):
        """Check if org is likely to be or not be an organisation based on keywords.
        
        This function contains a decision tree that determines if it is likely that a candidate organisation is a
        true orginasation, taking into account the presence of 'organisational' keywords.

        Args:
            final (bool): The current decision status .
            org (str): The organizational name to be checked for keyword presence.

        Returns:
            bool: The updated decision status based on keyword presence.
        """
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


    def check_single_orgs(org, true_orgs, doc_c):
        '''append org to true or false list depending on whether part_of_other
        is false or true respectively, and it is not blocked by the keyword check.'''
        final = True
        keyword = keyword_check(final, org)
        poo = part_of_other(true_orgs, org, doc_c)
        if poo is False and keyword is True:
            true_orgs.append(org)
        return true_orgs


    @staticmethod
    def part_of_other(orgs, org, doc):
        '''Check if a part of org is in orgs, and if that member of orgs is common.
        Only allow for a match if the member of orgs is long enough'''
        is_part = False
        for o in orgs:
            if org != o and o in org and len(o) > 5:
                n_orgs = len(re.findall(r"\b" + o + r"\b", doc.text))
                if n_orgs > 5:
                    kw_final = False
                    kw_o = keyword_check(kw_final, o)
                    kw_org = keyword_check(kw_final, org)
                    if not (kw_o is False and kw_org is True):
                        is_part = True
        return is_part


    def single_org_check(org, nlp):
        '''Check if an potential ORG is considered and ORG if just that name is analysed by Stanza NER.
        (Without the context of any sentences)'''
        doc_o = nlp(org)
        o_t = [f'{ent.text}' for ent in doc_o.ents if ent.type == "ORG"]
        is_org = bool(len(o_t) == 1 and org in o_t)
        return is_org


    def percentage_considered_org(doc, org, orgs, counts):
        '''identify all sentences in which the org is found. Then calculate in what fraction of the
        total number of mentions, the org is identified as org by NER'''
        n_orgs = count_number_of_mentions(doc, org)
        if n_orgs >= 1 and org in orgs:
            n_orgs_found = counts[orgs == org][0]
            percentage = n_orgs_found/float(n_orgs)*100.
        elif org in orgs:
            percentage = -10
        else:
            percentage = 0.
        return percentage, n_orgs


    def strip_function_of_entity(org):
        '''Strip the function of an potential org. Example: if fed with
        "Lid van de Raad van Advies bij Bedrijfsnaam", only "Bedrijfsnaam"
        would be returned.'''
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

    @staticmethod
    def count_number_of_mentions(doc, org):
        ''' Count the number of mentions of org in the text, taking into account word boundaries.'''
        if '-' not in org:
            n_counts = len(re.findall(r"\b" + org + r"\b", doc.text.replace('-', '')))
        else:
            n_counts = len(re.findall(r"\b" + org + r"\b", doc.text))
        return n_counts
