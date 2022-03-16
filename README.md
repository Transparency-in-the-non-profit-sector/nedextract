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

## How to use auto_extract
What does it do?
Auto_extract is being developed to extract specific information from annual report PDF files that are written in Dutch. Currently it tries to do the following:

- Read the PDF file, and perform Named Entity Recognition (NER) using Stanza to extract all persons named in the document
- Extract persons: using a rule-based method that searches for specific keywords, this module tries to identify:
    - Ambassadors
    - People in important positions in the organization. The code tries to determine a main job description (e.g. director or board) and a sub-job description (e.g. chairman or treasurer). Note: these positions are identified and outputted in Dutch.
- Extract related organizations (under development). 
- Classify the sector in which the organization is active. The code uses a pre-trained model to identify one of eight sectors in which the organization is active. 

Output

Methods of running:

Command to run:
python auto_extract/run_auto_extract.py 


## Installation

To install auto_extract from GitHub repository, do:

```console
git clone https://github.com/Transparency-in-the-non-profit-sector/np-transparency.git
cd np-transparency
python3 -m pip install .
```

## Documentation

Include a link to your project's full documentation here.

## Contributing

If you want to contribute to the development of auto_extract,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
