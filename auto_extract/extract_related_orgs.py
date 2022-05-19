# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import re
# Extract all named organisations in annual report
# Count the number of times each is mentioned
# Classify relation type:
#   - interne organisatieafhankelijkheid (i.e. daughter or mother company)
#   - financiële relatie
#   - partner (supplies funds, knowledge, goods, people)
#   - marktrelatie (hired to do something)
#   - politiek (is a political bystander or opponent)
# Classify type of organisation:
#   - bedrijf
#   - overheidsinstantie
#   - politieke/belangenorganisatie
#   - NGO
#   - onderwijs-/kennisinstelling
import numpy as np
import pandas as pd
import stanza
from auto_extract.preprocessing import preprocess_pdf


nlp = stanza.Pipeline(lang='nl', processors='tokenize, ner')


class Org_Keywords:
    # keywords that indicate that, when present in an pot. organisation, it is likely a true org,
    # independently of cases
    true_keys = ['bv', r'b\.v', 'congregatie', r'fonds\b', r'fondsen\b', r'fund\b',
                 'ministerie', 'umc', r'nederland\b']
    # keywords that indicate that,  when present in an pot. organisation, it is likely a true org,
    # but only when found with the included caps.
    true_keys_cap = ['Association', 'Coöperatie', r'\bCBF\b', 'Firma', 'Foundation',
                     'Hospice', 'Hogeschool', 'Holding',
                     'Institute', 'Instituut', r'Inc\.',
                     'Koninklijk Nederlands', 'Koninklijke Nederlandse',
                     'Loterij', 'LLP',
                     'Medisch Centrum', 'Museum', 'NV', r'N\.V',
                     'Stichting', 'Trust', r'U\.A', 'Universiteit', 'University', 'Vereniging',
                     'Ziekenhuis', 'Ziekenhuizen']
    # keywords that, when found in an pot. org., it is likely to be a false org,
    # independently of cases.
    false_keys = ['abonnement', 'activa', 'afdeling', 'akkoord', 'assembly',
                  'baten', 'bedrijfsvoering', 'begroting', 'beleid', 'bestuur', 'board',
                  'cao', 'commissie', 'commissaris', 'committee', 'congres', 'corona', 'council',
                  'covid', 'directeur', 'directie', 'docent', 'emeritus',
                  'fonds op naam', 'fondsen op naam', 'functie', 'fy2', 'interim',
                  'jaarrekening', 'jaarverslag', 'jury', r'lid\b', 'kosten',
                  'magazine', 'manager', 'managing', 'netwerk',
                  'overhead', 'overige', 'passiva', 'penningmeester', 'portefeuille', 'premie',
                  'president',
                  'raad', 'regeling', 'reserve', 'review', 'richtlijn', 'rj640', 'rj 640',
                  'rj 650', 'rj 2016', 'saldo', 'startdatum', r'\btbv\b', 'traineeship',
                  'van toezicht', 'verkiezing',
                  'voorzitter', r'www\.', r'\.nl', r'\.com']
    # keywords that, when found in whole as a pot. org., indicate a false org,
    # idnepoendenlty of cases
    false_keys_s = ['aandelen', 'ab', 'agile', 'algemeen nut beogende instelling', 'anbi', 'arbo',
                    'avg', 'beheer & administratie', 'beheer en administratie', 'beweging', 'bhv',
                    'bic', 'b&a', 'bw', 'ceo', 'cfo', 'cio', 'corporate', 'country offices',
                    'crm', 'customer relationship management', 'cto',
                    'db', 'derden', 'ebola', 'eindredactie', 'eur',
                    'finance & operations', 'financiën', 'finance', 'fondsenwerving',
                    'fonds', 'fondsen', 'fte', 'fundraising',
                    'gdpr', 'great fundraising', 'good governance', 'governance',
                    'hr', 'hrm', 'huisvesting', 'human resources', 'iban', 'ict', 'industrie',
                    'integrity', 'leasing', 'lobby', 'lobbyen',
                    'managementteam', 'management team', 'management', 'marketing', 'mt',
                    'naam', 'national organization',
                    'national organizations', 'pensioenfonds', 'pensioenfondsen',
                    'personeelsopbouw', 'program offices', 'project offices', 'p&o',
                    'risk and audit', 'rj', 'rvt', 'rvb', 'sar', 'sars', 'sv', 'tv',
                    'vgba', 'vio', 'vog', 'war']
    # Keywords to be stripped of pot. orgs (case insensitive)
    position = ['adviseur', 'bestuurslid', 'ceo', 'cfo', 'chief technology officer', 'cio',
                'commissaris', 'cto', 'directeur', 'lid', 'penningmeester', 'secretaris',
                'vice voorzitter', 'vicevoorzitter', 'vice-voorzitter', 'voorzitter']
    lidwoord_voorzetsels = [r'van\b', r'voor\b', r'bij\b', r'in\b', r'v\.', r'en\b', r'de\b',
                            r'het\b', r'een\b']
    raad = ['raad']
    commissie = ['wetenschappelijke adviesraad', 'maatschappelijke adviesraad', 'bestuur',
                 'toezicht', 'advies', 'commissarissen', 'adviesraad', 'rvt', 'rvc', 'rvb']
    # keywords that, when present in pot org, call for the attempt of keyword strip
    search_strip = position + commissie
    functies = ['hoofdfuncties', 'hoofdfunctie', 'nevenfuncties', 'nevenfunctie']


def collect_orgs(infile):
    '''Determine all ORGs in the text using Stanza NER. Select candidates by applying NER
    to different preprocessing choices. Perform additional checks to determine which
    candidates are most likely true orgs.'''
    true_orgs = []
    single_orgs = []
    doc_c = nlp(preprocess_pdf(infile, r_blankline=', ', r_par=', '))
    org_c = np.unique([ent.text.rstrip('.') for ent in doc_c.ents if ent.type == "ORG"],
                      return_counts=True)
    doc_p = nlp(preprocess_pdf(infile, r_blankline='. ', r_par=', '))
    org_p = np.unique([ent.text.rstrip('.') for ent in doc_p.ents if ent.type == "ORG"],
                      return_counts=True)
    doc_pp = nlp(preprocess_pdf(infile, r_blankline='. ', r_eol='. ', r_par=', '))
    org_pp = np.unique([ent.text.rstrip('.') for ent in doc_pp.ents if ent.type == "ORG"])
    org_all = np.unique(np.concatenate((org_c[0], org_p[0], org_pp)))
    for org in org_all:
        if any(kw in org.lower() for kw in Org_Keywords.search_strip):
            n_org = strip_function_of_entity(org)
        else:
            n_org = org
        if n_org != org and len(n_org) >= 3:
            single_orgs.append(n_org)
        else:
            pco_c = percentage_considered_org(doc_c, org, org_c[0], org_c[1])
            pco_p = percentage_considered_org(doc_p, org, org_p[0], org_p[1])
            decision = decide_org(org, pco_p, pco_c, org_pp, org_c)
            # input()
            # process conclusion
            if decision is True:
                true_orgs.append(org)
            elif decision == 'maybe':
                single_orgs.append(org)
    for org in single_orgs:
        true_orgs = check_single_orgs(org, true_orgs, doc_c)
    return sorted(list(set(true_orgs)))


def decide_org(org, pco_p, pco_c, org_pp, org_c):
    ''' Decision tree to determine if an potential ORG is likely to be a true org.
    Decisions are based on: the overall number of mentions of the pot. org in the text,
    the percentage of mentions in which it was actually considered an ORG by Stanza,
    whether a standalone pot. org is considered an ORG by Stanza,
    the precense of keywords that make it likely that the pot. org is an org,
    the precense of keywords that make it likely that the pot. org is NOT an org.'''
    final = False
    is_org = single_org_check(org)
    per_p, n_p = pco_p
    per_c, n_c = pco_c
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


def keyword_check(final, org):
    ''' Check if org is likely to be or not be an organisation based on keywords.'''
    for kw in Org_Keywords.true_keys:
        if len(re.findall(kw, org.lower())) > 0:
            final = True
            if len(org) == len(kw):
                final = False
    for kw in Org_Keywords.true_keys_cap:
        if len(re.findall((r"\b" + kw + r"\b"), org)) > 0:
            final = True
            if len(org) == len(kw):
                final = False
    if final is True:
        for kw in Org_Keywords.false_keys:
            if len(re.findall(kw, org.lower())) > 0:
                final = False
        if org.lower() in Org_Keywords.false_keys_s:
            final = False
    return final


def check_single_orgs(org, true_orgs, doc_c):
    '''append org to true or false list depending on whether part_of_other
    is false or true respectively, and it is not blocked by teh keyword check.'''
    final = True
    keyword = keyword_check(final, org)
    poo = part_of_other(true_orgs, org, doc_c)
    if poo is False and keyword is True:
        true_orgs.append(org)
    return true_orgs


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


def single_org_check(org):
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


def count_number_of_mentions(doc, org):
    ''' Count the number of mentions of org in the text, taking into account word boundaries.'''
    if '-' not in org:
        n_counts = len(re.findall(r"\b" + org + r"\b", doc.text.replace('-', '')))
    else:
        n_counts = len(re.findall(r"\b" + org + r"\b", doc.text))
    return n_counts


def match_anbis(df_in, anbis_file):
    df = pd.read_csv(anbis_file, usecols=["rsin", "currentStatutoryName", "shortBusinessName"])
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
