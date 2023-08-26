[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency)
[![github license badge](https://img.shields.io/github/license/Transparency-in-the-non-profit-sector/np-transparency)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency)
[![RSD](https://img.shields.io/badge/rsd-auto_extract-00a3e3.svg)](https://research-software-directory.org/projects/transparency-in-non-profit) 
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)
[![build](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/build.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/Transparency-in-the-non-profit-sector/np-transparency/badge.svg)](https://coveralls.io/github/Transparency-in-the-non-profit-sector/np-transparency)
[![cffconvert](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/cffconvert.yml)
[![markdown-link-check](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/Transparency-in-the-non-profit-sector/np-transparency/actions/workflows/markdown-link-check.yml)
[![OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/projects/7733/badge)](https://bestpractices.coreinfrastructure.org/projects/7733)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8286579.svg)](https://doi.org/10.5281/zenodo.8286579)
<br/><br/>

## Nedextract
nedextract is being developed to extract specific information from annual report PDF files that are written in Dutch. Currently it tries to do the following:

- Read the PDF file, and perform Named Entity Recognition (NER) using Stanza to extract all persons and all organisations named in the document, which are then processed by the processes listed below.
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

- Extract related organisations:
    - After Stanza NER collects all candidates for mentioned organisations, postprocessing tasks try to determine which of these candidates are most likely true candidates. This is done by considering: how often the terms is mentioned in the document, how often the term was identified as an organisation by Stanza NER, whether the term contains keywords that make it likely to be a true positive, and whether the term contains keywords that make it likely to be a false positive. For candidates that are mentioned only once in the text, it is also considered whether the term by itself (i.e. without context) is identified as an organisation by Stanza NER. Additionally, for candidates that are mentioned only once, an extra check is performed to determine whether part of the candidate org is found to be a in the list of orgs that are already identified as true, and whether that true org is common within the text. In that case the candidate is found to be 'already part of another true org', and not added to the true orgs. This is done, because sometimes an additional random word is identified by NER as being part of an organisation's name. 
    - For those terms that are identified as true organisations, the number of occurrences in the document of each of them (in it's entirety, enclosed by word boudaries) is determined.
    - Finally, the identified organisations are attempted to be matched on a list of provided organisations using the `anbis` argument, to collect their rsin number for further analysis. An empty file `./Data/Anbis_clean.csv` is availble that serves as template for such a file. Matching is attempted both on currentStatutoryName and shortBusinessName. Only full matches (independent of capitals) and full matches with the additional term 'Stichting' at the start of the identified organisation (again independent of capitals) are considered for matching. Fuzzy matching is not used here, because during testing, this was found to lead to a significant amount of false positives.


- Classify the sector in which the organisation is active. The code uses a pre-trained model to identify one of eight sectors in which the organisation is active. The model is trained on the 2020 annual report pdf files of CBF certified organisations.


## Prerequisites
1. [Python 3.8, 3.9, 3.10, 3.11](https://www.python.org/downloads/)
2. [miniconda](https://docs.conda.io/en/latest/miniconda.html); please note that miniconda is only required to install poppler, a requirements for pdftext.

## Installation

nedextract can be installed using pip:

```console
pip install nedextract
```

The required packages that are installed are: [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy), [NumPy](https://numpy.org), [openpyxl](https://openpyxl.readthedocs.io/en/stable/), [poppler](https://anaconda.org/conda-forge/poppler), [pandas](https://pandas.pydata.org), [pdftotext](https://github.com/jalan/pdftotext), [python-Levenshtein](https://pypi.org/project/python-Levenshtein/), [scikit-learn](https://scikit-learn.org/stable/), [Stanza](https://github.com/stanfordnlp/stanza), and [xlsxwriter](https://github.com/jmcnamara/XlsxWriter).[^1]

[^1]: If you encounter problems with the installation, these often arise from the installation of poppler, which is a requirement for pdftotext. Help can generally be found on [pdftotext](https://pypi.org/project/pdftotext/).
<br/><br/>


## Usage

#### Input
The full pipeline can ben run with the `run_nedextract.run`` function. Input can be provided in four different forms.
It takes in the following arguments:
- Input data, one or more pdf files, using one of the following arguments:
    - file: path to a single pdf file
    - directory: path to a directory containing pdf files
    - url: link to a pdf file
    - urlf: text file containing one or multiple urls to pdf files. The text file should contain one url per line, without headers and footers.
- tasks (optional): can either be 'people', 'orgs', 'sectors' or 'all'. Indicates which tasks to be performed. Defualts to 'people'.
- anbis (option): path to a .csv file which will be used with the `orgs` task. The file should contain (at least) the columns rsin, currentStatutoryName, and shortBusinessName. An empty example file, that is also the default file, can be found in the folder 'Data'. The data in the file will be used to try to match identified named organisations on to collect their rsin number provided in the file.
- model, labels, vectors (optional): each referring to a path containing a pretraining classifyer model, label encoding and tf-idf vectors respectively. These will be used for the sector classification task. A model can be trained using the `classify_organisation.train` function.
- write_output: TRUE/FALSE, defaults to FALSE, setting weither to write the output data to an excel file.

  
#### Returns:
Three dataframes, one for the 'people' task, one for the 'sectors' task, and one for the 'orgs' task. If write_output=True, the gathered information is written to auto-named xlsx files in de folder <i>Output</i>. The output of the different tasks are written to separate xlsx files with the following naming convention:

- <i>'./Output/outputYYYYMMDD_HHMMSS_people.xlsx' 
- './Output/outputYYYYMMDD_HHMMSS_related_organisations.xlsx'
- './Output/outputYYYYMMDD_HHMMSS_general.xlsx'</i>

Here YYYYMMDD and HHMMSS refer to the date and time at which the execution started.

#### Turorials
Tutorials on the full pipeline and (individual) useful analysis tools can be found in the Tutorials folder.

## Contributing

If you want to contribute to the development of nedextract,
have a look at the [contribution guidelines](CONTRIBUTING.md).
<br/><br/>

## How to cite us
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8286579.svg)](https://doi.org/10.5281/zenodo.8286579)
[![RSD](https://img.shields.io/badge/rsd-auto_extract-00a3e3.svg)](https://research-software-directory.org/projects/transparency-in-non-profit) 

If you use this package for your scientific work, please consider citing it as:
<br/><br/>
Ootes, L.S. (2023). nedextract (v0.2.0). Zenodo. https://doi.org/10.5281/zenodo.8286579
<br/><br/>
See also the [Zenodo page](https://zenodo.org/record/8286579) for exporting the citation to BibTteX and other formats.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
