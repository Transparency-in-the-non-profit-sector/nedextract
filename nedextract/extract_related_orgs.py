"""The file contains functions used to extract organisations mentioned within a text.

Functions:
- collect_orgs
- decide_org
- match_anbis
- apply_matching
"""

import numpy as np
import pandas as pd
import stanza
from nedextract.preprocessing import preprocess_pdf
from nedextract.utils.keywords import Org_Keywords
from nedextract.utils.orgs_checks import OrganisationExtraction


def collect_orgs(infile: str, nlp: stanza.Pipeline):  # pylint: disable=too-many-locals'
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
       - whether it passes the check_single_orgs check

    Args:
        infile (str): Path to the input PDF file.
        nlp (stanza.Pipeline): The stanza language model used for text processing.

    Returns:
        list: A sorted list of filtered organizational entities extracted from the PDF document.
    """
    true_orgs = []
    single_orgs = []
    extraction = OrganisationExtraction()

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
        extraction.org = org
        if any(kw in org.lower() for kw in Org_Keywords.search_strip):
            n_org = extraction.strip_function_of_entity()
        else:
            n_org = org
        if n_org != org and len(n_org) >= 3:
            single_orgs.append(n_org)
        else:
            extraction.doc = doc_c
            extraction.orgs = org_c[0]
            extraction.counts = org_c[1]
            pco_c = extraction.percentage_considered_org()
            extraction.doc = doc_p
            extraction.orgs = org_p[0]
            extraction.counts = org_p[1]
            pco_p = extraction.percentage_considered_org()
            pco = pco_c, pco_p
            decision = decide_org(org, pco, org_pp, org_c, nlp)

            # process conclusion
            if decision is True:
                true_orgs.append(org)
            elif decision == 'maybe':
                single_orgs.append(org)
    for org in single_orgs:
        extraction.org = org
        extraction.true_orgs = true_orgs
        extraction.doc = doc_c
        true_orgs = extraction.check_single_orgs()
    return sorted(list(set(true_orgs)))


def decide_org(org: str, pco: tuple, org_pp: np.array, org_c: np.array, nlp: stanza.Pipeline):
    """Decision tree to determine if an potential ORG is likely to be a true org.

    Decisions are based on: the overall number of mentions of the pot. org in the text,
    the percentage of mentions in which it was actually considered an ORG by Stanza,
    whether a standalone pot. org is considered an ORG by Stanza,
    the precense of keywords that make it likely that the pot. org is an org,
    the precense of keywords that make it likely that the pot. org is NOT an org.

    Args:
        infile (str): Path to the input PDF file.
        pco (tuple): tuple of percentage (float), percentage of mentioned at which the organisation was found as org,
            n_orgs (int) number of times the oganisation was mentioned in the text
        org_pp (np.array): array of unique organoisations found in the text found using preprocessing mentod 3
        org_c (np.array): array of unique organoisations found in the text found using preprocessing mentod 1
        nlp (stanza.Pipeline): The stanza language model used for text processing.

    Returns:
        list: final True, False no or maybe indication the decision on whether the organistion candidate
        is likely a true organisation
    """
    extraction = OrganisationExtraction(org=org, nlp=nlp)
    final = False

    is_org = extraction.individual_org_check()
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
        kw_check = extraction.keyword_check(final=final)
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
        final = extraction.keyword_check(final=final)
    return final


def match_anbis(df_in: pd.DataFrame, anbis_file: str):
    """Match potential organizations with known ANBI information.

    This function takes an input DataFrame 'df_in' containing potential organisations,
    and an file 'anbis_file' (CSV format) containing information about known ANBI organisions.
    Potential organizations from 'df_in' are matched with ANBI records based on their names.

    Args:
        df_in (pd.DataFrame): Input DataFrame containing potential organisations.
        anbis_file (str): Path to the ANBI file (CSV format) containing known ANBIs.

    Returns:
        pd.DataFrame: A DataFrame containing the matched organisations and ANBI information.
    """
    df = pd.read_csv(anbis_file, usecols=["rsin", "currentStatutoryName", "shortBusinessName"],
                     dtype=str)
    df_match = df_in
    df_match['matched_anbi'] = df_match['mentioned_organization'].apply(lambda x: apply_matching(
                                                                        df,
                                                                        x, 'currentStatutoryName',
                                                                        'shortBusinessName'))

    # perform join between df_match and df based on matched_anbi and currentStatutoryName
    df1 = df_match.merge(df[df['currentStatutoryName'].notnull()], how='left',
                         left_on='matched_anbi', right_on='currentStatutoryName')

    # select data from d1 with unknown rsin
    df2 = df1[df1['rsin'].isna()][['Input_file', 'mentioned_organization', 'n_mentions',
                                   'matched_anbi']]

    # select df1s with rsin
    df1_out = df1[df1['rsin'].notnull()]

    # match df with df2 using shortBusinessName
    df2_out = df2.merge(df[df['shortBusinessName'].notnull()], how='left',
                        left_on='matched_anbi', right_on='shortBusinessName')

    # combine df1 and df2 output
    df_out = pd.concat([df1_out, df2_out])
    return df_out.sort_values(by=['Input_file', 'mentioned_organization'])


def apply_matching(df: pd.DataFrame, m: str, c2: str, c3: str):
    """Apply matching of name to df.

    This funcion tries to match name 'm' with values in either the c2 or c3 column of a dataframe,
    allowing for the term 'stichting' to be added to the name m for matching.

     Args:
        df (pandas.DataFrame): The DataFrame containing potential matching options.
        m (str): The organisation name to be matched.
        c2 (str): The name of the first column to search for matches.
        c3 (str): The name of the second column to search for matches.

    Returns:
        str or None: The matched organizational name if found, or None if no match is found.

    """
    cc2 = df[df[c2].notnull()][c2].to_numpy()
    cc3 = df[df[c3].notnull()][c3].to_numpy()
    match_options = np.unique(np.append(cc2, cc3))
    for mo in match_options:
        if mo.lower() == m.lower() or mo.lower() == 'stichting ' + m.lower():
            return mo
    return None
