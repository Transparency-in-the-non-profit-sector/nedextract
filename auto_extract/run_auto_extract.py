# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import os
import pandas as pd
from datetime import datetime
import time
import argparse
from argparse import RawTextHelpFormatter

from read_pdf import extract_pdf
from auto_extract.preprocessing import download_pdf, delete_downloaded_pdf

desc = """This script can read annual report pdf files and extract relevant information about:
- Board members (directors, bestuur, raad van toezicht, kascommissie, controlecommissie, ledenraad)
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
args = parser.parse_args()

if not (args.directory or args.file or args.url or args.url_file):
    raise Exception('No input provided. Run with -h for help on arguments to be provided.')


# Create the output directory if it does not exist already
if not os.path.exists(os.path.join(os.getcwd(), 'Output')):
    os.makedirs(os.path.join(os.getcwd(), 'Output'))
outdir_path = os.path.join(os.getcwd(), 'Output')
outtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
fn = 'output' + str(outtime) + '.xlsx'
outputfile = os.path.join(outdir_path, fn)
outputdata = []


# Read all files
countfiles = 0
if args.file:
    infile = os.path.join(os.getcwd(), args.file)
    outputdata = extract_pdf(infile, outputdata)
elif args.directory:
    totalfiles = len([name for name in os.listdir(os.path.join(os.getcwd(), args.directory))
                     if name.lower().endswith('.pdf')])
    for filename in os.listdir(os.path.join(os.getcwd(), args.directory)):
        countfiles += 1
        print('Working on file:', countfiles, 'out of', totalfiles)
        if filename.lower().endswith('.pdf'):
            infile = os.path.join(os.getcwd(), args.directory, filename)
            outputdata = extract_pdf(infile, outputdata)
elif args.url:
    infile = download_pdf(args.url)
    outputdata = extract_pdf(infile, outputdata)
    delete_downloaded_pdf()
elif args.url_file:
    with open(args.url_file, 'r') as u:
        urls = u.readlines()
    for url in urls:
        print(url)
        infile = download_pdf(url)
        outputdata = extract_pdf(infile, outputdata)
        delete_downloaded_pdf()


# Return extrcated information to output
outpufile = './Output/output'
df1 = pd.DataFrame(outputdata, columns=['Input file', 'Organization', 'Main sector', 'Persons',
                   'Ambassadors', 'Board members', 'Job description', 'Related organizations'])
df1.to_excel(outputfile)

# end time
end_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
print('The start time was: ', start_time)
print('The end time is: ', end_time)
