"""Classes with keywords.

Classes:
- JobKeywords: keywords related to main jobs (directors, bestuur, raad van toezicht) and
    related to positions within certain commissions etc (related to main jobs)
- Tussenvoegsels: a list of common tussenvoegsels in names found in the Netherlands
- Titles: a list of common titles.
- Org_Keywords: multiple lists used to extract organisations from a text.
"""
import numpy as np


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
              'phd', 'phd.', 'dhr.', 'mevr.', 'mw.', 'ds.', 'mgr.', 'mevrouw', 'meneer', 'jhr.',
              'pastor', 'pastoor', 'dominee', 'priester', 'imam', 'rabbi', 'rabbijn']


class Org_Keywords:
    """Class that stored lists with various keywords used to extract organisations from a text."""

    # keywords that indicate that, when present in an pot. organisation, it is likely a true org, independently of cases
    true_keys = ['bv', r'b\.v', 'congregatie', r'fonds\b', r'fondsen\b', r'fund\b',
                 'ministerie', 'umc', r'nederland\b']

    # keywords that indicate that, when present in an pot. organisation, it is likely a true org, but only when found with
    # the included caps.
    true_keys_cap = ['Association', 'Coöperatie', r'\bCBF\b', 'Firma', 'Foundation',
                     'Hospice', 'Hogeschool', 'Holding',
                     'Institute', 'Instituut', r'Inc\.',
                     'Koninklijk Nederlands', 'Koninklijke Nederlandse',
                     'Loterij', 'LLP',
                     'Medisch Centrum', 'Museum', 'NV', r'N\.V',
                     'Stichting', 'Trust', r'U\.A', 'Universiteit', 'University', 'Vereniging',
                     'Ziekenhuis', 'Ziekenhuizen']

    # keywords that, when found in an pot. org., it is likely to be a false org, independently of cases.
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

    # keywords that, when found in whole as a pot. org., indicate a false org, indipendently of cases
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
