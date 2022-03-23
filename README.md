## Badges

(Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.)

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/Transparency-in-the-non-profit-sector/np-transparency)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency) |
| (3/5) community registry           | [![RSD](https://img.shields.io/badge/rsd-auto_extract-00a3e3.svg)](https://www.research-software.nl/software/auto_extract) [![workflow pypi badge](https://img.shields.io/pypi/v/auto_extract.svg?colorB=blue)](https://pypi.python.org/project/auto_extract/) |
| (4/5) citation                     | [![DOI](https://zenodo.org/badge/DOI/<replace-with-created-DOI>.svg)](https://doi.org/<replace-with-created-DOI>) |
| (5/5) checklist                    | [![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>) |
| howfairis                          | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| Static analysis                    | [![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=Transparency-in-the-non-profit-sector_np-transparency&metric=alert_status)](https://sonarcloud.io/dashboard?id=Transparency-in-the-non-profit-sector_np-transparency) |
| Coverage                           | [![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=Transparency-in-the-non-profit-sector_np-transparency&metric=coverage)](https://sonarcloud.io/dashboard?id=Transparency-in-the-non-profit-sector_np-transparency) |
| Documentation                      | [![Documentation Status](https://readthedocs.org/projects/np-transparency/badge/?version=latest)](https://np-transparency.readthedocs.io/en/latest/?badge=latest) |
| **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/build.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/build.yml) |
| Citation data consistency               | [![cffconvert](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/cffconvert.yml) |
| SonarCloud                         | [![sonarcloud](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/sonarcloud.yml) |
| MarkDown link checker              | [![markdown-link-check](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/markdown-link-check.yml) |
<br/><br/>

## How to use auto_extract
<b>What does it do?</b>  
Auto_extract is being developed to extract specific information from annual report PDF files that are written in Dutch. Currently it tries to do the following:

- Read the PDF file, and perform Named Entity Recognition (NER) using Stanza to extract all persons named in the document
- Extract persons: using a rule-based method that searches for specific keywords, this module tries to identify:
    - Ambassadors
    - People in important positions in the organisation. The code tries to determine a main job description (e.g. director or board) and a sub-job description (e.g. chairman or treasurer). Note that these positions are identified and outputted in Dutch.  
    The main jobs that are considered are: 
        - directeur
        - raad van toezicht
        - bestuur
        - ledenraad
        - kascommissie
        - controlecommisie.  

        The sub positions that are considered are:
        - directeur
        - voorzitter
        - vicevoorzitter
        - lid
        - penningmeester
        - commissaris
        - adviseur
    
    For each person that is identified, the code searches for keywords in the sentences in which the name appears to determine the main position, or the sentence directly before or after that. Subjobs are determine based on words appearing directly before or after the name of a person for whom a main job has been determined. For the main jobs and sub positions, various ways of writing are considered in the keywords. Also before the search for the job-identification starts, name-deduplication is performed by creating lists of names that (likely) refer to one and the same person (e.g. Jane Doe and J. Doe).

- Extract related organisations (under development). 
- Classify the sector in which the organisation is active. The code uses a pre-trained model to identify one of eight sectors in which the organisation is active. 

<br/><br/>
<b>How to run</b>  
To run auto_extract the script `auto_extract/run_auto_extract.py` has to be executed and provided with input data and tasks. The input data (annual report pdf files) can be supplied as a single file, an entire folder, an url (referring to an online pdf file), or a text file containing a list of urls. The input data is supplied using one of the following arguments:

- `-f`: to supply a single pdf file as argument. The full command would for example be: `python ./auto_extract/run_auto_extract.py -f 'annual_report.pdf'`
- `-d`: to supply a directory containing pdf files as argument. The code will process all pdf files in the folder. If the folder contains subfolders or non-pdf files, these will be ignored. E.g. `python ./auto_extract/run_auto_extract.py -d './Annual_reports'`
- `-u`: to supply an url to a pdf file as argument. E.g. `python ./auto_extract/run_auto_extract.py -u https://www.website.com/annual_report.pdf`
- `-uf`: to supply a text file containing a list of urls as argument. E.g. `python ./auto_extract/run_auto_extract.py -uf 'my_urls.txt'`.  
The text file should simply contain one url per line, without headers and footers. 

Additionally, it is possible to define which tasks should be performed using the `-t` argument with one or more of the options: `people` (to perform the tasks described under extract persons), `orgs` (to perform tge tasks described under extract related organisations), `sector` (to classify the sector in which the organisation is active) or `all` (to perform all tasks). It is possible to supply multiple tasks. E.g.:  
`python ./auto_extract/run_auto_extract.py -f 'annual_report.pdf' -t people sector`  
If the `-t` argument is not provided, the code will perform all tasks by default.

<br/><br/>
<b>Output</b>  
The gathered information is written to auto-named xlsx files in de folder <i>Output</i>. The output of the different tasks are written to separate xlsx files with the following naming convention:

- <i>'./Output/outputYYYYMMDD_HHMMSS_people.xlsx' 
- './Output/outputYYYYMMDD_HHMMSS_related_organisations.xlsx'
- './Output/outputYYYYMMDD_HHMMSS_general.xlsx'</i>

Here YYYYMMDD and HHMMSS refer to the date and time at which the execution started.
<br/><br/>

## Installation

To install auto_extract from GitHub repository, do:

```console
git clone https://github.com/Transparency-in-the-non-profit-sector/np-transparency.git
cd np-transparency
python3 -m pip install .
```

Auto_extract requires the following Python packages: [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy), [pdftotext](https://github.com/jalan/pdftotext), [NumPy](https://numpy.org), [pandas](https://pandas.pydata.org), and [Stanza](https://github.com/stanfordnlp/stanza).
<br/><br/>

## Contributing

If you want to contribute to the development of auto_extract,
have a look at the [contribution guidelines](CONTRIBUTING.md).
<br/><br/>

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
