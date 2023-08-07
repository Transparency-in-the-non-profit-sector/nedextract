"""The file contains functions used to extract organisations mentioned within a text.

Functions:
- collect_orgs
- decide_org
- match_anbis
- apply_matching
"""

import numpy as np
import pandas as pd
from helpers_org_extraction import check_single_orgs
from helpers_org_extraction import keyword_check
from helpers_org_extraction import percentage_considered_org
from helpers_org_extraction import single_org_check
from helpers_org_extraction import strip_function_of_entity
from auto_extract.preprocessing import preprocess_pdf
from keywords import Org_Keywords


def collect_orgs(infile: str, nlp: stanza.Pipeline):
    """Extract mentioned organisations from a PDF document.
    
    This function is used to extract mentioned organisations (ORGs) in a text using Stanza NER. 
    Candidates are select candidates by applying NER to different preprocessing choices. 
    Additional checks are performed to determine which candidates are most likely true orgs.
    It returns a list of filtered entities.
    
    Steps:
    1. preprocess the text in three different ways, as it is often unclear what the best way of 'reading'
       consequetive blacks lines, replacesent of end-of-line characters, or parentheses is, and gather for each way 
       NER entities defined as ORG.
    2. determine the unique entities mentioned as candidates.
    3. Determine which candidates are considered 'true' organisations based on:
       - whether is contains a typical orginastions keyword.
       - term length.
       - how often te term was identified as an organisation by NER.
       - wether it passes the check_single_orgs check

    Args:
        infile (str): Path to the input PDF file.
        nlp (stanza.Pipeline): The stanza language model used for text processing.

    Returns:
        list: A sorted list of filtered organizational entities extracted from the PDF document.
    """
    true_orgs = []
    single_orgs = []
    # preprocessing method 1
    doc_c = nlp(preprocess_pdf(infile, r_blankline=', ', r_par=', '))
    org_c = np.unique([ent.text.rstrip('.') for ent in doc_c.ents if ent.type == "ORG"],
                        return_counts=True)
    # Preprocessing method 2
    doc_p = nlp(preprocess_pdf(infile, r_blankline='. ', r_par=', '))
    org_p = np.unique([ent.text.rstrip('.') for ent in doc_p.ents if ent.type == "ORG"],
                        return_counts=True)
    # Preprocessing method 3
    doc_pp = nlp(preprocess_pdf(infile, r_blankline='. ', r_eol='. ', r_par=', '))
    org_pp = np.unique([ent.text.rstrip('.') for ent in doc_pp.ents if ent.type == "ORG"])

    # determine unique orgs candidates based on all 'forms' of entities gathered with the different preprocessing steps
    org_all = np.unique(np.concatenate((org_c[0], org_p[0], org_pp)))

    # steps to dertermine 'true' orgs
    for org in org_all:
        if any(kw in org.lower() for kw in Org_Keywords.search_strip):
            n_org = strip_function_of_entity(org)
        else:
            n_org = org
        if n_org != org and len(n_org) >= 3:
            single_orgs.append(n_org)
        else:
            pco = percentage_considered_org(doc_c, org, org_c[0], org_c[1]),
            percentage_considered_org(doc_p, org, org_p[0], org_p[1])
            decision = decide_org(org, pco, org_pp, org_c, nlp)
            # process conclusion
            if decision is True:
                true_orgs.append(org)
            elif decision == 'maybe':
                single_orgs.append(org)
    for org in single_orgs:
        true_orgs = check_single_orgs(org, true_orgs, doc_c)
    return sorted(list(set(true_orgs)))


def decide_org(org, pco, org_pp, org_c, nlp: stanza.Pipleline):
    """ Decision tree to determine if an potential ORG is likely to be a true org.
    Decisions are based on: the overall number of mentions of the pot. org in the text,
    the percentage of mentions in which it was actually considered an ORG by Stanza,
    whether a standalone pot. org is considered an ORG by Stanza,
    the precense of keywords that make it likely that the pot. org is an org,
    the precense of keywords that make it likely that the pot. org is NOT an org."""
    final = False
    is_org = single_org_check(org, nlp)
    per_c, n_c, per_p, n_p = pco[0][0], pco[0][1], pco[1][0], pco[1][1]
    # decision tree
    if n_p >= 5 or n_c >= 5:
        if per_p >= 50. and per_c >= 50.:
            final = True
    elif n_p >= 3 or n_c >= 3:
        if per_p >= 66. and per_c >= 66.:
            final = True
    elif n_p == 2:
        if per_p == 100.:
            final = True
    elif n_p == 1 and n_c == 1:
        kw_check = keyword_check(final, org)
        if per_p == per_c == 100. and ((org in org_pp) or (is_org is True) or (kw_check is True)):
            final = 'maybe'
        elif per_p == 100. and (org in o for o in org_c) and ((org in org_pp) or
                                                              (is_org is True) or
                                                              (kw_check is True)):
            final = 'maybe'
        elif (org in org_pp) and (kw_check is True):
            final = 'maybe'
        else:
            final = 'no'
    elif (is_org and org in org_pp):
        if per_p == -10 or per_c == -10:
            final = 'no'
        else:
            final = 'maybe'
    # check for hits and misses
    if final not in ('maybe', 'no') and n_p >= 1:
        final = keyword_check(final, org)
    return final


def match_anbis(df_in, anbis_file):
    df = pd.read_csv(anbis_file, usecols=["rsin", "currentStatutoryName", "shortBusinessName"],
                    dtype=str)
    df_match = df_in
    df_match['matched_anbi'] = df_match['mentioned_organization'].apply(lambda x: apply_matching(
                                                                        df,
                                                                        x, 'currentStatutoryName',
                                                                        'shortBusinessName'))
    df1 = df_match.merge(df[df['currentStatutoryName'].notnull()], how='left',
                         left_on='matched_anbi', right_on='currentStatutoryName')
    df2 = df1[df1['rsin'].isna()][['Input_file', 'mentioned_organization', 'n_mentions',
                                   'matched_anbi']]
    df1_out = df1[df1['rsin'].notnull()]
    df2_out = df2.merge(df[df['shortBusinessName'].notnull()], how='left',
                        left_on='matched_anbi', right_on='shortBusinessName')
    df_out = pd.concat([df1_out, df2_out])
    return df_out.sort_values(by=['Input_file', 'mentioned_organization'])


def apply_matching(df, m, c2, c3):
    cc2 = df[df[c2].notnull()][c2].to_numpy()
    cc3 = df[df[c3].notnull()][c3].to_numpy()
    match_options = np.unique(np.append(cc2, cc3))
    for mo in match_options:
        if mo.lower() == m.lower() or mo.lower() == 'stichting ' + m.lower():
            return mo
    return None
