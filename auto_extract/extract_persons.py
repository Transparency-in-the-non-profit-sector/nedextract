# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import numpy as np
import re
from fuzzywuzzy import fuzz


def abbreviate(name, n_ab):
    '''Abbreviate the first n_ab terms in a name, except if they are tussenvoegsels, and as long
    as it is not the last term in a name. List of tussenvoegsels is taken from:
    https://publicaties.rvig.nl/dsresource?objectid=c5f84baf-ba01-41ef-a6a0-97cebec1c2d3&type=pdf
    One-letter tussenvoegsels have been omitted'''
    tussenvoegsels = ["'s", "'m", "'t", "aan", "af", "al", "am", "auf", "ben", "bij", "bin",
                      "boven", "da", "dal", "dal'", "dalla", "das", "de", "deca", "degli", "dei",
                      "del", "della", "dem", "den", "der", "des", "di", "die", "do", "don", "dos",
                      "du", "el", "gen", "het", "im", "in", "la", "las", "le", "les", "lo", "los",
                      "of", "onder", "op", "over", "te", "ten", "ter", "tho", "thoe", "thor", "to",
                      "toe", "tot", "uijt", "uit", "unter", "van", "ver", "vom", "von", "voor",
                      "vor", "zu", "zum", "zur"]
    splitname = name.split()
    abbreviation = ''
    for i in range(len(splitname)):
        if i < len(splitname)-1 and i <= n_ab and splitname[i] not in tussenvoegsels:
            abbreviation = abbreviation + splitname[i][0] + ' '
        else:
            abbreviation = abbreviation + splitname[i] + ' '
    return abbreviation


def find_duplicate_persons(persons):
    ''' From a list of names, find which names represent different writings of the same name,
    e.g. James Brown and J. Brown. Returns a list consisting of sublists, in which each sublist
    contains all versions of the same name. The token_set_ratio from the fuzzywuzzy package is
    used to determine how close to names are. Names are stripped from any titles, and when
    comparing two names where one contains initials (i.e. James Brown versus J. Brown), the first
    name is abbreviated to try to determine the initials.'''
    outnames = []
    titles = ['prof.', 'dr.', 'mr.', 'ir.', 'drs.', 'bacc.', 'kand.', 'dr.h.c.', 'ing.', 'bc.',
              'phd.', 'dhr.', 'mevr.', 'mw.', 'ds.', 'mgr.']
    # strip names from titles
    for title in titles:
        p = [person.lower().replace(title, '') for person in persons]
    # loop through list of input names to find matches
    for i in range(len(persons)):
        same_name = [persons[i]]
        # if a name consists of one term only, do not try to find matches (This prevents James from
        # being matched with both James Brown and James White, which would imply James Brown and
        # James White are also the same person. The remainder of the loop will make sure James
        # Brown and James will be matched, as well as James White and James.)
        if (len(p[i].split()) == 1):
            outnames.append(same_name)
            continue
        else:
            for j in range(len(persons)):
                if i != j:
                    Token_Set_Ratio = fuzz.token_set_ratio(p[i], p[j])
                    # if the second name is only one word
                    if len(p[j].split()) == 1:
                        req_score = 100
                    # if both names contain initials
                    elif (p[i].count('.') >= 1 and p[j].count('.') >= 1):
                        req_score = 90
                    # if one name contains initials, try to abbreviate the other one with up to
                    # the same number of initials and then compare
                    elif p[i].count('.') >= 1:
                        tsr = np.array(0)
                        for n_initials in range(1, p[i].count('.') + 1):
                            p_ab = abbreviate(p[j], n_initials)
                            tsr = np.append(tsr, fuzz.token_set_ratio(p[i], p_ab))
                        Token_Set_Ratio = max(tsr)
                        req_score = 95
                    elif p[j].count('.') >= 1:
                        tsr = np.array(0)
                        for n_initials in range(1, p[j].count('.') + 1):
                            p_ab = abbreviate(p[i], n_initials)
                            tsr = np.append(tsr, fuzz.token_set_ratio(p_ab, p[j]))
                        Token_Set_Ratio = max(tsr)
                        req_score = 95
                    # if name is normal
                    else:
                        req_score = 90
                    # check if required score is exceeded
                    if Token_Set_Ratio >= req_score:
                        same_name.extend([persons[j]])
            same_name.sort()
            outnames.append(same_name)

    outnames.sort(key=len, reverse=True)

    # remove duplicate lists of names
    for i in range(len(outnames)-1, -1, -1):
        if any(all(elem in names for elem in outnames[i]) for names in outnames[0:i]):
            outnames.pop(i)

    # remove items that appear in two sublists
    outlist = []
    for j in range(len(outnames)):
        x = outnames[j]
        for restlist in (outnames[:j] + outnames[j+1:]):
            if any(elem in outnames[j] for elem in restlist):
                x = [k for k in outnames[j] if k not in restlist]
        outlist.append(x)

    return outlist


def surrounding_words(text, search_names):
    """ for a given text and search words (names), returns an array of words that are
    found before and after the search word"""
    surrounding_words = np.array([])
    text = np.array2string(text, separator=' ')
    search_names.sort(key=len, reverse=True)
    for search_name in search_names:
        text = text.replace(search_name.lower(), 'search4term')
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
    ''' return the summed total of occurrences of search words in text'''
    fulltext = np.array2string(text, separator=' ')
    fulltext = re.sub(r"[\[\]']", '', fulltext)
    totalcount = 0
    totalcount_sentence = 0
    for item in search_words:
        totalcount += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(item), fulltext))
    for sentence in text:
        count = 0
        for item in search_words:
            count = count + sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(item), sentence))
        if count > 0:
            totalcount_sentence += 1
    return totalcount, totalcount_sentence


def determine_main_job(main_jobs, sentences, surroundings):
    '''Determine main job category based on:
    The most occuring category in the direct text based on sentence frequency (fs, i.e. number of
    sentences in which category+name is found)
    If none can be identified, or there is a tie: try based on sentence frequency from surrounding
    sentences (fss).
    If none can be identified: try based on overall frequency in main text
    If non can be identified: try based on overall frequency in surrounding text
    If still none can be identified, eliminate name from board'''
    fs = np.empty(len(main_jobs))  # sentence frequency direct sentences
    fss = np.empty(len(main_jobs))  # sentence frequency incl. surrounding sentences
    ft = np.empty(len(main_jobs))  # total frequency direct sentences
    fts = np.empty(len(main_jobs))  # total frequency incl. surrounding sentences
    main_job = np.array([mj[0] for mj in main_jobs])
    for m in range(len(main_jobs)):
        ft[m], fs[m] = count_occurrence(sentences, main_jobs[m])
        fts[m], fss[m] = count_occurrence(np.append(sentences, surroundings), main_jobs[m])

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
    return main_cat, ft_director, fts_bestuur, fts_rvt


def extract_persons(doc, all_persons):
    ''' Determine from a text which persons (identified with stanza) are ambassadors or
    board members, using a rule based method. Identify potential ambassadors and board members
    based on key words occuring in sentences in which a name is mentioned. Next, for board members,
    a main and sub position are identified (if possible). The rules for main position are based on
    the frequency of key words occuring in sentences in which names are mentioned, or the sentences
    surrounding those in which names are mentioned.
    Sub positions are determined based on the frequency of key words directly next to the name.

    For the position of director, an additional filter is applied: if more than 2 persons are
    identified as director, persons are not considered a director if:
    - they are mentioned in director context < 2 (ft), while the max mentioning is > 2
    - the subposition (obtained from words directly surrounding name) is not director.'''
    ambassadors = np.array([])  # identified ambassadors
    pot_per = np.array([])  # people with potential significant position
    people = []  # list of all writing forms of names of people in pot_per
    board = np.array([])    # identified people with significant positions
    b_position = np.array([])   # people with significant positions + main and sub position
    pot_director = []  # list potential directors, subjob, and context count
    p_directeur = np.array([])  # array of identified directors
    pot_rvt = []  # list of potential rvt members
    p_rvt = np.array([])  # array of identified rvt members
    pot_bestuur = []  # list of potential board member
    p_bestuur = np.array([])  # array of identified board members
    p_ledenraad = np.array([])  # array of identified ledenraad members
    p_kasc = np.array([])  # array of identified members of kascommissie
    p_controlec = np.array([])  # array of identified members of controlecommissie

    # words and categories for main jobs
    directeur = ['directeur', 'directrice', 'directie', 'bestuurder']
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

    # identify potential ambassadors and board members based on keywords in sentences
    for sentence in doc.sentences:
        stripped_sentence = sentence.text.lower().replace(',', ' ').replace('.', ' ')
        if any(item in stripped_sentence for item in (main_job_all + sub_job_all)):
            per = [f'{ent.text}' for ent in sentence.ents if ent.type == "PER"]
            pot_per = np.append(pot_per, per)

    # Find duplicates (i.e. J Brown and James Brown) and concatenate all ways of writing
    # the name of one persons that is potentially of interest
    peoples = find_duplicate_persons(list(np.unique(all_persons)))
    for p in peoples:
        if any(item in pot_per for item in p):
            people.append(p)

    # Determine most likely position of board members
    # Collect all sentences containing a particular board member name +
    # the sentences before and after the occurrences
    for members in people:
        c_sub_job = np.array([])
        sentences = np.array([])
        prevsentence = ''
        surroundings = np.array([])
        need_next_sentence = False

        # Determine relevant sentences
        for sentence in doc.sentences:
            if any(member in sentence.text for member in members):
                sentences = np.append(sentences, sentence.text.lower())
                if prevsentence not in list(surroundings):
                    surroundings = np.append(surroundings, prevsentence)
                need_next_sentence = True
            elif need_next_sentence:
                if sentence.text.lower() not in surroundings:
                    surroundings = np.append(surroundings, sentence.text.lower())
                need_next_sentence = False
            prevsentence = sentence.text.lower()

        # Determine main job category
        main_cat, ft_direc, fts_bestuur, fts_rvt = determine_main_job(main_jobs, sentences,
                                                                      surroundings)
        if main_cat is None:
            continue

        # Determine sub job category based on positions mentioned directely before or after name
        surrounding_w = surrounding_words(sentences, members)
        if surrounding_w.size > 0:
            for sj in sub_jobs:
                c_sub_job = np.append(c_sub_job, count_occurrence(surrounding_w, sj)[0])
        else:
            c_sub_job = np.append(c_sub_job, 0)

        if max(c_sub_job) > 0 and len(np.where(c_sub_job == max(c_sub_job))[0]) == 1:
            sub_cat = backup_sub_cat = sub_job[np.where(c_sub_job == max(c_sub_job))[0]][0]
            if main_cat == 'directeur' and sub_cat != 'directeur':
                sub_cat = ''
            elif main_cat == 'directeur' and sub_cat == 'directeur':
                backup_sub_cat = ''
        else:
            sub_cat = backup_sub_cat = ''

        # Add final results
        member = max(members, key=len)
        if main_cat == 'ambassadeur':
            if sub_cat != '':
                main_cat = determine_main_job(main_jobs_no_amb, sentences, surroundings)[0]
            else:
                ambassadors = np.append(ambassadors, member)
        if main_cat != 'ambassadeur':
            board = np.append(board, member)
            b_position = np.append(b_position, member + ' - ' + main_cat + ' - ' + sub_cat)
            if main_cat == 'directeur':
                p_directeur = np.append(p_directeur, member)
                if sub_cat == '':
                    backup_main_cat = determine_main_job(main_jobs_backup, sentences,
                                                         surroundings)[0]
                else:
                    backup_main_cat = determine_main_job(main_jobs_backup_noamb, sentences,
                                                         surroundings)[0]
                pot_director.append([member, sub_cat, ft_direc, backup_main_cat, backup_sub_cat,
                                     fts_bestuur, fts_rvt])
            elif main_cat == 'rvt':
                pot_rvt.append([member, sub_cat, fts_rvt])
            elif main_cat == 'bestuur':
                pot_bestuur.append([member, sub_cat, fts_bestuur])
            elif main_cat == 'ledenraad':
                p_ledenraad = np.append(p_ledenraad, member)
            elif main_cat == 'kascommissie':
                p_kasc = np.append(p_kasc, member)
            elif main_cat == 'controlecommissie':
                p_controlec = np.append(p_controlec, member)

    # **** Additional check
    # if there are > 2 potential directors, a potential director is not considered a director if:
    # - they are mentioned in director context < 2 (ft), while the max mentioning is > 2
    # - or if the subposition (obtained from words directly surrounding name) is not director.
    #   In this case, use the second highest scoring main category instead
    pot_director = np.array(pot_director, dtype=object)
    if len(pot_director) > 1:
        for i in range(len(pot_director)):
            if ((pot_director[i, 2] <= 1 and int(max(pot_director[:, 2])) > 2) or
               (pot_director[i, 1] != 'directeur')):
                b_position = b_position[b_position != (pot_director[i, 0] + ' - directeur - ' +
                                                       pot_director[i, 1])]
                p_directeur = p_directeur[p_directeur != pot_director[i, 0]]
                # Use backup
                if str(pot_director[i, 3]) == 'rvt':
                    pot_rvt.append([pot_director[i, 0], pot_director[i, 1], pot_director[i, 6]])
                elif str(pot_director[i, 3]) == 'bestuur':
                    pot_bestuur.append([pot_director[i, 0], pot_director[i, 1],
                                       pot_director[i, 5]])
                elif str(pot_director[i, 3]) == 'ledenraad':
                    p_ledenraad = np.append(p_ledenraad, pot_director[i, 0])
                elif str(pot_director[i, 3]) == 'kascommissie':
                    p_kasc = np.append(p_kasc, pot_director[i, 0])
                elif str(pot_director[i, 3]) == 'controlecommissie':
                    p_controlec = np.append(p_controlec, pot_director[i, 0])
                else:
                    board = board[board != pot_director[i, 0]]
                if pot_director[i, 3] == 'ambassadeur':
                    ambassadors = np.append(ambassadors, pot_director[i, 0])
                elif pot_director[i, 3] is not None:
                    b_position = np.append(b_position, (str(pot_director[i, 0]) + ' - ' +
                                           str(pot_director[i, 3]) + ' - ' +
                                           str(pot_director[i, 4])))

    # If there are more than 10 people in rvt or bestuur, remove them if they have an fts <= 3
    # and do not have an sub position assigned
    pot_rvt = np.array(pot_rvt, dtype=object)
    for i in range(len(pot_rvt)):
        if len(pot_rvt) > 10 and pot_rvt[i, 2] <= 3:
            board = board[board != pot_rvt[i, 0]]
            b_position = b_position[b_position != pot_rvt[i, 0] + ' - rvt - ' + pot_rvt[i, 1]]
        else:
            p_rvt = np.append(p_rvt, pot_rvt[i, 0])

    pot_bestuur = np.array(pot_bestuur, dtype=object)
    for i in range(len(pot_bestuur)):
        if len(pot_bestuur) > 10 and pot_bestuur[i, 2] <= 3:
            board = board[board != pot_bestuur[i, 0]]
            b_position = b_position[b_position != (pot_bestuur[i, 0] + ' - bestuur - ' +
                                                   pot_bestuur[i, 1])]
        else:
            p_bestuur = np.append(p_bestuur, pot_bestuur[i, 0])

    return (ambassadors, board, b_position, p_directeur, p_rvt, p_bestuur, p_ledenraad, p_kasc,
            p_controlec)
