"""Run auto extract program.

Functions:
- main
- write_output

Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""

import argparse
import os
import time
from argparse import RawTextHelpFormatter
from datetime import datetime
import numpy as np
import pandas as pd
from nedextract.extract_related_orgs import match_anbis
from nedextract.preprocessing import delete_downloaded_pdf
from nedextract.preprocessing import download_pdf
from nedextract.read_pdf import PDFInformationExtractor


def main(testarg=None):
    """Annual report information extraction.

    This program is designed to read Dutch annual report pdf files from non-profit organisation.
    and extract relevant information.

    The following general steps are taken:
    - Read in the pdf files(s) and preprocess the text.
    - (optional) Extract mentioned people from the text and identify their position within the organisation.
      Which of the people named in the text can be found to likely hold any of the positions of board members (directors,
      bestuur, raad van toezicht, kascommissie, controlecommissie, edenraad), or ambassadors
    - (optional) Extract mentioned organisations in the text
    - (optional) Classify the sector in which the organisation is active.
    - The gathered information is converted into structured output in the form of an Excel file.
    """
    # start time
    start_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"

    # Parse command line arguments
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('-d', '--directory',
                        help='Directory containing annual reports to be processed.')
    parser.add_argument('-f', '--file', help='Specific pdf file to be processed.')
    parser.add_argument('-u', '--url', help='URL to pdf file to be processed.')
    parser.add_argument('-uf', '--url_file', help='File containing url paths to be processed.')
    parser.add_argument('-t', '--tasks', choices=['all', 'people', 'orgs', 'sectors'],
                        nargs='*', default='all', help='tasks to be performed. Default=all')
    parser.add_argument('-af', '--anbis_file',
                        default=os.path.join(os.path.join(os.getcwd(), 'Data'), 'anbis_clean.csv'),
                        help='CSV file to be used for org matching,conly used for task org')
    parser.add_argument('-pf_m', '--file_model',
                        default=os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'trained_sector_classifier.joblib'),
                        help='file containing pretrained model for sector classification')
    parser.add_argument('-pf_l', '--file_labels',
                        default=os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'labels_sector_classifier.joblib'),
                        help='file containing labels for pretrained sector classification')
    parser.add_argument('-pf_v', '--file_vectors',
                        default=os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'tf_idf_vectorizer.joblib'),
                        help='file containing tf_idf vectors')

    if testarg:
        args = parser.parse_args(testarg)
    else:
        args = parser.parse_args()

    if not (args.directory or args.file or args.url or args.url_file):
        raise FileNotFoundError('No input provided. Run with -h for help on arguments to be provided.')

    # Create the output directory if it does not exist already
    if not os.path.exists(os.path.join(os.getcwd(), 'Output')):
        os.makedirs(os.path.join(os.getcwd(), 'Output'))
    opd_p = np.array([]).reshape(0, 91)
    opd_g = np.array([]).reshape(0, 3)
    opd_o = np.array([]).reshape(0, 3)

    # convert tasks to list
    args.tasks = [args.tasks] if isinstance(args.tasks, str) else args.tasks

    # Create an instance of the PDFInformationExtractor class
    pdf_extractor = PDFInformationExtractor(args.tasks, args.file_model, args.file_labels, args.file_vectors)

    # Read all files
    countfiles = 0
    if args.file:
        infile = os.path.join(os.getcwd(), args.file)
        opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
    elif args.directory:
        totalfiles = len([name for name in os.listdir(os.path.join(os.getcwd(), args.directory))
                         if name.lower().endswith('.pdf')])
        for filename in os.listdir(os.path.join(os.getcwd(), args.directory)):
            if filename.lower().endswith('.pdf'):
                countfiles += 1
                print('Working on file:', countfiles, 'out of', totalfiles)
                infile = os.path.join(os.getcwd(), args.directory, filename)
                opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
    elif args.url:
        infile = download_pdf(args.url)
        opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
        delete_downloaded_pdf()
    elif args.url_file:
        with open(args.url_file, mode='r', encoding='UTF-8') as u:
            urls = u.readlines()
        for url in urls:
            print(url)
            infile = download_pdf(url)
            opd_p, opd_g, opd_o = pdf_extractor.extract_pdf(infile, opd_p, opd_g, opd_o)
            delete_downloaded_pdf()

    # Write output to files
    write_output(args.tasks, opd_p, opd_g, opd_o, args.anbis_file)

    # end time
    print('The start time was: ', start_time)
    print('The end time is: ', f"{datetime.now():%Y-%m-%d %H:%M:%S}")
    return args


def write_output(tasks: list, opd_p: np.array, opd_g: np.array, opd_o: np.array, anbis_file: str):
    """Write extracted information to output files.

    Create three output files for people, sectors, and organisations.

    Args:
        tasks (list): list of arguments used to define which tasks had to be executed
        opd_p (np.array): output results for people task
        opd_g (np.array): output results for sectors tasks
        opd_o (np.array): output results for organisations task
        anbis_file (str): name of the anbis file used to match organisations with info of known organisations
    Returns:
    """
    outtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    # Define outputfiles
    opf_p = os.path.join(os.path.join(os.getcwd(), 'Output'),
                         'output' + str(outtime) + '_people.xlsx')
    opf_g = os.path.join(os.path.join(os.getcwd(), 'Output'),
                         'output' + str(outtime) + '_general.xlsx')
    opf_o = os.path.join(os.path.join(os.getcwd(), 'Output'),
                         'output' + str(outtime) + '_related_organizations.xlsx')

    # Write extracted people to output file
    if 'all' in tasks or 'people' in tasks:
        cols_p = ['Input_file', 'Organization', 'Persons', 'Ambassadors',
                  'Board_members', 'Job_description']
        cols_p.extend([f'directeur{n}' for n in range(1, 6)])
        cols_p.extend([f'rvt{n}' for n in range(1, 21)])
        cols_p.extend([f'bestuur{n}' for n in range(1, 21)])
        cols_p.extend([f'ledenraad{n}' for n in range(1, 31)])
        cols_p.extend([f'kascommissie{n}' for n in range(1, 6)])
        cols_p.extend([f'controlecommissie{n}' for n in range(1, 6)])
        df1 = pd.DataFrame(opd_p, columns=cols_p)
        df1.to_excel(opf_p, engine='xlsxwriter')
        print('Output people written to:', opf_p)

    # Write sectors to output file
    if 'all' in tasks or 'sectors' in tasks:
        cols_g = ['Input_file', 'Organization', 'Main_sector']
        df2 = pd.DataFrame(opd_g, columns=cols_g)
        df2.to_excel(opf_g, engine='xlsxwriter')
        print('Output sectors written to:', opf_g)

    # Write extracted organisations to output file
    if 'all' in tasks or 'orgs' in tasks:
        cols_o = ['Input_file', 'mentioned_organization', 'n_mentions']
        df3 = pd.DataFrame(opd_o, columns=cols_o)
        df3 = match_anbis(df3, anbis_file)
        df3.to_excel(opf_o, engine='xlsxwriter')
        print('Output organisations written to:', opf_o)


if __name__ == "__main__":
    main()
