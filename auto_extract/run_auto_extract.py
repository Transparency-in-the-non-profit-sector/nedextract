# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import argparse
import os
import time
from argparse import RawTextHelpFormatter
from datetime import datetime
import pandas as pd
from auto_extract.preprocessing import delete_downloaded_pdf
from auto_extract.preprocessing import download_pdf
from auto_extract.read_pdf import extract_pdf


def main(testarg=None):
    desc = """This script can read annual report pdf files and extract relevant information about:
    - Board members (directors, bestuur, raad van toezicht, kascommissie, controlecommissie,
      ledenraad)
    - Ambassadors
    - Other organizations mentioned in the text
    - Classify the sector of the organisation

    To do:
    - Classify the subsector
    - Determine mission statements
    - Determine activities
    - Determine the type of related organizations (use kvk data/wiki data?)
    - Determine the type of relationship with related organizations
    - Determine financial information

    The information is converted into structured output in the form of an Excel file.

    Run with either -d, -f, -u or -uf. """

    # start time
    start_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-d', '--directory',
                        help='Directory containing annual reports to be processed.')
    parser.add_argument('-f', '--file', help='Specific pdf file to be processed.')
    parser.add_argument('-u', '--url', help='URL to pdf file to be processed.')
    parser.add_argument('-uf', '--url_file', help='File containing url paths to be processed.')
    parser.add_argument('-t', '--tasks', choices=['all', 'people', 'orgs', 'sectors'],
                        nargs='*', default='all', help='tasks to be performed. Default=all')
    args = parser.parse_args()

    if testarg:
        args.file = testarg

    if not (args.directory or args.file or args.url or args.url_file):
        raise Exception('No input provided. Run with -h for help on arguments to be provided.')

    # Create the output directory if it does not exist already
    if not os.path.exists(os.path.join(os.getcwd(), 'Output')):
        os.makedirs(os.path.join(os.getcwd(), 'Output'))
    opd_p = []
    opd_g = []
    opd_o = []

    # convert tasks to list
    args.tasks = [args.tasks] if isinstance(args.tasks, str) else args.tasks

    # Read all files
    countfiles = 0
    if args.file:
        infile = os.path.join(os.getcwd(), args.file)
        opd_p, opd_g, opd_o = extract_pdf(infile, opd_p, opd_g, opd_o, args.tasks)
    elif args.directory:
        totalfiles = len([name for name in os.listdir(os.path.join(os.getcwd(), args.directory))
                         if name.lower().endswith('.pdf')])
        for filename in os.listdir(os.path.join(os.getcwd(), args.directory)):
            countfiles += 1
            print('Working on file:', countfiles, 'out of', totalfiles)
            if filename.lower().endswith('.pdf'):
                infile = os.path.join(os.getcwd(), args.directory, filename)
                opd_p, opd_g, opd_o = extract_pdf(infile, opd_p, opd_g, opd_o, args.tasks)
    elif args.url:
        infile = download_pdf(args.url)
        opd_p, opd_g, opd_o = extract_pdf(infile, opd_p, opd_g, opd_o, args.tasks)
        delete_downloaded_pdf()
    elif args.url_file:
        with open(args.url_file, mode='r', encoding='UTF-8') as u:
            urls = u.readlines()
        for url in urls:
            print(url)
            infile = download_pdf(url)
            opd_p, opd_g, opd_o = extract_pdf(infile, opd_p, opd_g, opd_o, args.tasks)
            delete_downloaded_pdf()

    write_output(args.tasks, opd_p, opd_g, opd_o)

    # end time
    print('The start time was: ', start_time)
    print('The end time is: ', f"{datetime.now():%Y-%m-%d %H:%M:%S}")
    return(args)


def write_output(tasks, opd_p, opd_g, opd_o):
    '''Return extracted information to output'''
    outdir_path = os.path.join(os.getcwd(), 'Output')
    outtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    opf_p = os.path.join(outdir_path, 'output' + str(outtime) + '_people.xlsx')
    opf_g = os.path.join(outdir_path, 'output' + str(outtime) + '_general.xlsx')
    opf_o = os.path.join(outdir_path, 'output' + str(outtime) + '_related_organizations.xlsx')
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
        df1.to_excel(opf_p)

    if 'all' in tasks or 'sectors' in tasks:
        cols_g = ['Input_file', 'Organization', 'Main_sector']
        df2 = pd.DataFrame(opd_g, columns=cols_g)
        df2.to_excel(opf_g)

    if 'all' in tasks or 'orgs' in tasks:
        cols_o = ['Input_file', 'Organization', 'Related_organizations']
        df3 = pd.DataFrame(opd_o, columns=cols_o)
        df3.to_excel(opf_o)


if __name__ == "__main__":
    main()
