"""Run auto extract program.

Functions:
- run
- write_output

Copyright 2022 Netherlands eScience Center
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""

import os
import time
from datetime import datetime
import numpy as np
import pandas as pd
from nedextract.extract_related_orgs import match_anbis
from nedextract.preprocessing import delete_downloaded_pdf
from nedextract.preprocessing import download_pdf
from nedextract.read_pdf import PDFInformationExtractor


def run(directory=None, file=None, url=None, urlf=None,  # pylint: disable=too-many-arguments, too-many-locals
        tasks='people', anbis=None, model=None, labels=None,
        vectors=None, write_o=False):
    """Annual report information extraction.

    This function runs the full nedextract pipleline. The pipeline is originally designed to read
    Dutch annual report pdf files from non-profit organisation and extract relevant information.
    It can extract information about people (task 'people') engaged in the organisation and the position they hold,
    entities named in the file (task 'orgs'), and/or identify the sector in which the organisation is active
    based on a provided pretrained model.


    The following general steps are taken:
    - Read in the pdf files(s) and preprocess the text.
    - (optional) Extract mentioned people from the text and identify their position within the organisation.
      Which of the people named in the text can be found to likely hold any of the positions of board members (directors,
      bestuur, raad van toezicht, kascommissie, controlecommissie, edenraad), or ambassadors
    - (optional) Extract mentioned organisations in the text. If an anbis csv file is profided, it will try to match
      the found organisations with those in the goven file, and add additonal information from the csv file to the output.
    - (optional) Classify the sector in which the organisation is active.
    - The gathered information is converted into a pandas DataFrame and optionally saved to excel files.

    Args:
        directory (str): Directory containing annual reports to be processed.
        file (str): Path to specific pdf file to be processed.
        url (str): URL to pdf file to be processed.
        urlf (str): txt file containing url paths to be processed.
        tasks (list or string): the tasks to execute. Options for tasks: 'all', 'people', 'sectors', 'orgs'
        anbis (str), optional, only for task 'orgs': csv file for matching mentioned organisations (for task orgs)
        model (str), only with option 'sectors': The path to the pretrained classifier file for sector prediction.
        labels (str), only with option 'sectors': The path to the pretrained label encoding file for sector prediction.
        vectors (str), only with option 'sectors': The path to the pretrained tf-idf vectorizer file for sector prediction.
        write_output (bool): if true, the output will be written to an excel file

    Returns:
        df_p, df_g, df_o: pd.DataFrames with results of the three respective tasks
    """
    # start time
    start_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"

    if not (directory or file or url or urlf):
        raise FileNotFoundError('No input provided. Run with -h for help on arguments to be provided.')

    # Create the output directory if it does not exist already
    if not os.path.exists(os.path.join(os.getcwd(), 'Output')):
        os.makedirs(os.path.join(os.getcwd(), 'Output'))
    opd_p = np.array([]).reshape(0, 91)
    opd_g = np.array([]).reshape(0, 3)
    opd_o = np.array([]).reshape(0, 3)

    # convert tasks to list
    tasks = [tasks] if isinstance(tasks, str) else tasks

    # Create an instance of the PDFInformationExtractor class
    pdf_extractor = PDFInformationExtractor(tasks, model, labels, vectors)

    # Read all files
    countfiles = 0
    if file:
        infile = os.path.join(os.getcwd(), file)
        opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
    elif directory:
        totalfiles = len([name for name in os.listdir(os.path.join(os.getcwd(), directory))
                         if name.lower().endswith('.pdf')])
        for filename in os.listdir(os.path.join(os.getcwd(), directory)):
            if filename.lower().endswith('.pdf'):
                countfiles += 1
                print('Working on file:', countfiles, 'out of', totalfiles)
                infile = os.path.join(os.getcwd(), directory, filename)
                opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
    elif url:
        infile = download_pdf(url)
        opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
        delete_downloaded_pdf()
    elif urlf:
        with open(urlf, mode='r', encoding='UTF-8') as u_url:
            urls = u_url.readlines()
        for urlp in urls:
            print('working on url:', urlp)
            infile = download_pdf(url)
            opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
            delete_downloaded_pdf()

    df_p, df_g, df_o = output_to_df(opd_p, opd_g, opd_o, anbis)
    # Write output to files
    if write_o:
        write_output(tasks, df_p, df_g, df_o)

    # end time
    print('The start time was: ', start_time)
    print('The end time is: ', f"{datetime.now():%Y-%m-%d %H:%M:%S}")
    return df_p, df_g, df_o


def output_to_df(opd_p=None, opd_g=None, opd_o=None, anbis_file=None):
    """
    Convert extracted data in numpy arrays to pandas dataframes with correct column names.

    Args:
        opd_p (numpy.ndarray): A numpy array containing output for people mentioned in pdf.
        opd_g (numpy.ndarray): A numpy array containing predicted sector in a pdf.
        opd_o (numpy.ndarray): A numpy array containing related organizations mentioned in a pdf.

    Returns
        df_p, df_g, df_o: three pd.DataFrames containing the input information on people, sectors,
        and organizations repectively
    """
    df_p, df_g, df_o = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    if opd_p is not None:
        cols_p = ['Input_file', 'Organization', 'Persons', 'Ambassadors',
                  'Board_members', 'Job_description']
        cols_p.extend([f'directeur{n}' for n in range(1, 6)])
        cols_p.extend([f'rvt{n}' for n in range(1, 21)])
        cols_p.extend([f'bestuur{n}' for n in range(1, 21)])
        cols_p.extend([f'ledenraad{n}' for n in range(1, 31)])
        cols_p.extend([f'kascommissie{n}' for n in range(1, 6)])
        cols_p.extend([f'controlecommissie{n}' for n in range(1, 6)])
        df_p = pd.DataFrame(opd_p, columns=cols_p)

    # Convert sectors to df
    if opd_g is not None:
        cols_g = ['Input_file', 'Organization', 'Main_sector']
        df_g = pd.DataFrame(opd_g, columns=cols_g)

    # convert organisations to df
    if opd_o is not None:
        cols_o = ['Input_file', 'mentioned_organization', 'n_mentions']
        df_o = pd.DataFrame(opd_o, columns=cols_o)
        if anbis_file is not None:
            df_o = match_anbis(df_o, anbis_file)
    return df_p, df_g, df_o


def write_output(tasks: list,
                 dfp: pd.DataFrame = None, dfg: pd.DataFrame = None, dfo: pd.DataFrame = None):
    """Write extracted information to output files.

    Create three output excel files for people, sectors, and organisations.

    Args:
        tasks (list): list of arguments used to define which tasks had to be executed
        dfp (pd.DataFrame): output results df for people task
        dfg (pd.DataFrame): output results df for sectors tasks
        dfo (pd.DataFrame): output results df for organisations task
    """
    outtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    # Write extracted people to output file
    if 'all' in tasks or 'people' in tasks:
        opf_p = os.path.join(os.path.join(os.getcwd(), 'Output'),
                             'output' + str(outtime) + '_people.xlsx')
        dfp.to_excel(opf_p, engine='xlsxwriter')
        print('Output people written to:', opf_p)

    # Write sectors to output file
    if 'all' in tasks or 'sectors' in tasks:
        opf_g = os.path.join(os.path.join(os.getcwd(), 'Output'),
                             'output' + str(outtime) + '_general.xlsx')
        dfg.to_excel(opf_g, engine='xlsxwriter')
        print('Output sectors written to:', opf_g)

    # Write extracted organisations to output file
    if 'all' in tasks or 'orgs' in tasks:
        opf_o = os.path.join(os.path.join(os.getcwd(), 'Output'),
                             'output' + str(outtime) + '_related_organizations.xlsx')
        dfo.to_excel(opf_o, engine='xlsxwriter')
        print('Output organisations written to:', opf_o)
