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
import stanza
from auto_extract.preprocessing import preprocess_pdf


nlp = stanza.Pipeline(lang='nl', processors='tokenize, ner')

class Org_Keywords:
    true_keys = ['bv', 'b.v', 'fonds', 'fondsen', 'ministerie', 'umc', 'nederland']
    true_keys_cap = ['Association', 'Hospice', 'Hogeschool', 'Institute', 'Instituut',
                     'Medisch Centrum', 'Stichting', 'Universiteit', 'University', 'Vereniging',
                     'Ziekenhuis', 'Ziekenhuizen'
                    ]
    false_keys = ['raad', 'bestuur', 'board', 'corona', 'covid', 'directeur', 'docent', 'activa', 'passiva', 
                 'reserve', 'www.', '.nl', '.com', 'overige', 'baten', 'saldo', 'interim',
                 'managing', 'manager', 'afdeling', 'regeling', 'rj640', 'rj 640', 'rj 650','rj 2016', 'penningmeester',
                 'voorzitter', 'kosten', 'bedrijfsvoering', 'congres', 'akkoord', 'overhead', 'fy2'
                 'cao', 'begroting', 'commissie', 'committee', 'richtlijn', 'emeritus', 'abonnement', 'startdatum', 'portefeuille',
                 'netwerk', 'lid ', 'functie', 'review']
    false_keys_s = ['avg', 'mt', 'db', 'ab', 'managementteam', 'management team', 'management', 'marketing', 'p&o', 'rj', 'ict',
                    'hr', 'hrm', 'crm', 'arbo', 'rvt', 'eur', 'bhv', 'fondsenwerving', 'pensioenfonds', 'pensioenfondsen',
                    'eindredactie', 'fte', 'ceo', 'cio', 'cto', 'cfo', 'vgba', 'vio', 'industrie', 'b&a', 
                    'beheer & administratie', 'beweging', 'huisvesting', 'ebola', 'sars', 'finance & operations', 'GDPR',
                    'Human Resources']


def collect_orgs(infile):
    '''Determine all entities in the text using NER. Select candidates by applying NER
    to different preprocessing choices. Perform additional checks to determine which
    candidates are most likely true entities.'''
    true_orgs = []
    false_orgs = []
    single_orgs = []
    doc_c = nlp(preprocess_pdf(infile, r_blankline=', ', r_par=', '))
    org_c = np.unique([f'{ent.text}' for ent in doc_c.ents if ent.type == "ORG"], return_counts=True)
    doc_p = nlp(preprocess_pdf(infile, r_blankline='. ', r_par=', '))
    org_p = np.unique([ent.text.rstrip('.') for ent in doc_p.ents if ent.type == "ORG"], return_counts=True)
    doc_pp = nlp(preprocess_pdf(infile, r_blankline='. ', r_eol='. ', r_par=', '))
    org_pp = np.unique([ent.text.rstrip('.') for ent in doc_pp.ents if ent.type == "ORG"])
    org_all = np.unique(np.concatenate((org_c[0], org_p[0], org_pp)))
    for org in org_all:
        org = org.rstrip('.')
        print(org)
        pco_c = percentage_considered_org(doc_c, org, org_c[0], org_c[1])
        print('c', pco_c)
        pco_p = percentage_considered_org(doc_p, org, org_p[0], org_p[1])
        print('p', pco_p)
        decision = decide_org(org, pco_p, pco_c, org_pp, org_c)
        if org in org_pp: 
            print('in org_pp')
        print('decision = ', org, decision)
        # input()
        # process conclusion
        if decision is True:
            true_orgs.append(org)
        elif decision is False or decision == 'no':
            false_orgs.append(org)
        elif decision == 'maybe':
            single_orgs.append(org)
    for org in single_orgs:
        true_orgs, false_orgs = check_single_orgs(org, true_orgs, false_orgs, doc_c)
    print(sorted(true_orgs))
    print(sorted(false_orgs))
    return true_orgs


def decide_org(org, pco_p, pco_c, org_pp, org_c):
    final = False
    is_org = single_org_check(org)
    per_p, n_p = pco_p
    per_c, n_c = pco_c
    # decision tree
    print('is org', is_org)
    print('n_p', n_p, 'n_c', n_c)
    if n_p >= 5 or n_c >= 5:
        if per_p >= 50. and per_c >= 50.:
            final = True
    elif n_p >= 3 or n_c >= 3:
        if per_p >= 66. and per_c >= 66.:
            final = True
    elif n_p == 2:
        final = 'no'
        if per_p == 100.:
            final = True
    elif n_p == 1 and n_c == 1:
        kw_check = keyword_check(final, org)
        if per_p == per_c == 100. and ((org in org_pp) or (is_org is True) or (kw_check is True)):
            final = 'maybe'
        elif per_p == 100. and (org in o for o in org_c) and ((org in org_pp) or (is_org is True) or (kw_check is True)):
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
    print('pre final', final)
    if final not in ('maybe', 'no') and n_p>=1:
        final = keyword_check(final, org)
    print('final', final)
    return final


def keyword_check(final, org):
    ''' Check if org is likely to be or not be an organisation based on keywords.'''
    for kw in Org_Keywords.true_keys:
        if kw in org.lower():
            final = True
            if len(org)==len(kw):
                final = False
    for kw in Org_Keywords.true_keys_cap:
        if len(re.findall((r"\b" + kw + r"\b"), org)) > 0:
            final = True
            if len(org)==len(kw):
                final = False
    if final is True:
        for kw in Org_Keywords.false_keys:
            if kw in org.lower():
                final = False
        if org.lower() in Org_Keywords.false_keys_s: 
            final = False
    return final


def check_single_orgs(org, true_orgs, false_orgs, doc_c):
    '''append org to true or false list depending on whether part_of_other 
    is false or true respectively, and it is not blocked by teh keyword check.'''
    final = True
    keyword = keyword_check(final, org)
    poo = part_of_other(true_orgs, org, doc_c)
    if poo is False and keyword is True:
        true_orgs.append(org)
    else:
        false_orgs.append(org)
    return true_orgs, false_orgs


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
                if kw_o is False and kw_org is True:
                    print('true,', org, 'can be found in', o, ', n=', n_orgs, ', but has additional keyword')
                else:
                    print('true,', org, 'can be found in', o, ', n=', n_orgs)
                    is_part = True
    return is_part


def single_org_check(org):
    doc_o = nlp(org)
    o_t = [f'{ent.text}' for ent in doc_o.ents if ent.type == "ORG"]
    is_org = bool(len(o_t) == 1 and org in o_t)
    return is_org


def percentage_considered_org(doc, org, orgs, counts):
    '''identify all sentences in which the org is found. Then calculate in what fraction of the total number of mentions, 
    the org is identified as org by NER'''
    # sentences = np.array([])
    # for sentence in doc.sentences:
    #    if re.search(r"\b" + org + r"\b", sentence.text):
    #        sentences = np.append(sentences, sentence.text)
    # text_select = np.array2string(sentences)
    # print(org)
    # print(text_select)
    if '-' not in org:
        n_orgs = len(re.findall(r"\b" + org + r"\b", doc.text.replace('-', '')))
    else:
        n_orgs = len(re.findall(r"\b" + org + r"\b", doc.text))
    # print('n_orgs', n_orgs)
    if n_orgs >= 1 and org in orgs:
        n_orgs_found = counts[orgs == org][0]
        # print('n_orgs found', n_orgs_found)
        percentage = n_orgs_found/float(n_orgs)*100.
    elif org in orgs:
        percentage = -10
    else:
        percentage = 0.
        # print('n_orgs found', 0)
    return percentage, n_orgs
