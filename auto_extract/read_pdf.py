# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import os
import stanza
import numpy as np
from datetime import datetime

from auto_extract.preprocessing import preprocess_pdf
from auto_extract.extract_persons import extract_persons
from auto_extract.extract_related_orgs import extract_orgs
from auto_extract.classify_organisation import predict_main_sector


def extract_pdf(infile, opd_p, opd_g, opd_o, tasks):
    """ Extract information from a pdf file using a stanza pipline. """

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Working on file:', infile)
    text = preprocess_pdf(infile, ' ')
    if tasks == ['sectors']:
        main_sector = predict_main_sector('./Pretrained/trained_sector_classifier.joblib',
                                          './Pretrained/labels_sector_classifier.joblib',
                                          './Pretrained/tf_idf_vectorizer.joblib',
                                          text)
        persons, organization, ambassadors, board, board_positions, orgs_details = ([], [], [], [],
                                                                                    [], [])
    else:
        # Apply pre-trained Dutch stanza pipeline to text
        download_stanza_NL()
        nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
        doc = nlp(text)

        # Extract all unique persons and organizations from the text using
        # the named entity recognition function of stanza
        persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
        orgs = [f'{ent.text}' for ent in doc.ents if ent.type == "ORG"]
        organizations, corg = np.unique(orgs, return_counts=True)

        try:
            imc = np.argmax(corg)
            organization = organizations[imc]
            if 'people' in tasks or 'all' in tasks:
                (ambassadors, board, board_positions, p_directeur, p_rvt, p_bestuur, p_ledenraad,
                 p_kasc, p_controlec) = extract_persons(doc, persons)
                # try again if unlikely results
                if ((len(p_rvt) == 0 and len(p_bestuur) == 0) or (len(p_rvt) > 10)
                   or (len(p_bestuur) > 10)):
                    text2 = preprocess_pdf(infile, '. ')
                    doc2 = nlp(text2)
                    persons2 = np.unique([f'{ent.text}' for ent in doc2.ents
                                          if ent.type == "PER"])
                    (ambassadors, board, board_positions, p_directeur, p_rvt, p_bestuur,
                     p_ledenraad, p_kasc, p_controlec) = extract_persons(doc2, persons2)
            else:
                ambassadors, board, board_positions = [], [], []
            if 'orgs' in tasks or 'all' in tasks:
                orgs_details = extract_orgs(text, organizations)
            else:
                orgs_details = []
            if 'sectors' in tasks or 'all' in tasks:
                main_sector = predict_main_sector('./Pretrained/trained_sector_classifier.joblib',
                                                  './Pretrained/labels_sector_classifier.joblib',
                                                  './Pretrained/tf_idf_vectorizer.joblib',
                                                  text)
            else:
                main_sector = []
        except ValueError:
            (organization, ambassadors, board, board_positions, p_directeur, p_rvt, p_bestuur,
             p_ledenraad, p_kasc, p_controlec, main_sector,
             orgs_details) = ([], [], [], [], [], [], [], [], [], [], [], [])

    # Output
    output = [infile, organization, main_sector, ots(persons), ots(ambassadors), ots(board),
              ots(board_positions)]
    output.extend(atc(p_directeur, 5))
    output.extend(atc(p_rvt, 20))
    output.extend(atc(p_bestuur, 20))
    output.extend(atc(p_ledenraad, 30))
    output.extend(atc(p_kasc, 5))
    output.extend(atc(p_controlec, 5))
    opd_p.append(output)
    opd_g.append([infile, organization, main_sector])
    opd_o.append([infile, organization, ots(orgs_details)])

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished file:', infile)
    return opd_p, opd_g, opd_o


def ots(input):
    """ Output to string: Convert array output to a backspace-seperated string """
    out_string = ""
    for element in input:
        out_string += str(element) + "\n"
    return out_string


def atc(input, length):
    """ Array to columns: Split array into 5 variables which will be converted into columns
        in the final output"""
    outlist = ['']*length
    if input is not None:
        for i in range(len(input)):
            if i == length - 1 and len(input) > length:
                print("Problem: there are more persons in one of the categories than allocated "
                      "columns.")
                outlist[i] = ots(input[i:])
                break
            else:
                outlist[i] = input[i]
    return outlist


def download_stanza_NL():
    outpath = os.path.join(os.getcwd(), 'stanza_resources')
    outf = os.path.join(outpath, 'nl')
    outfile = os.path.join(outf, 'default.zip')
    if not os.path.exists(outfile):
        stanza.download('nl', model_dir=outpath)
    return outfile
