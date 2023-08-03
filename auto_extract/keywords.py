"""Class with keywords.

This class contains:
- keywords related to main jobs (directors, bestuur, raad van toezicht) and 
    related to positions within certain commissions etc (related to main jobs)
- a list of common tussenvoegsels in names found in the Netherlands
- a list of common titles.
"""


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
              'phd', 'phd.', 'dhr.', 'mevr.', 'mw.', 'ds.', 'mgr.', 'mevrouw', 'meneer', 'jhr.']


