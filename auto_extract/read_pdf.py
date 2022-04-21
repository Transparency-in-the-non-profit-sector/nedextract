# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import os
from datetime import datetime
import numpy as np
import stanza
from auto_extract.classify_organisation import predict_main_sector
from auto_extract.extract_persons import extract_persons
from auto_extract.extract_related_orgs import extract_orgs
from auto_extract.preprocessing import preprocess_pdf


def extract_pdf(infile, opd_p, opd_g, opd_o, tasks):
    """ Extract information from a pdf file using a stanza pipline. """

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Working on file:', infile)
    text = preprocess_pdf(infile, ', ')
    if tasks == ['sectors']:
        main_sector = predict_main_sector('./Pretrained/trained_sector_classifier.joblib',
                                          './Pretrained/labels_sector_classifier.joblib',
                                          './Pretrained/tf_idf_vectorizer.joblib',
                                          text)
        outp_people = atc([infile], 91)
        orgs_details = []
        organization = ''
    else:
        # Apply pre-trained Dutch stanza pipeline to text
        download_stanza_NL()
        doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)

        # Extract all unique persons and organizations from the text using
        # the named entity recognition function of stanza
        organizations, corg = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "ORG"],
                                        return_counts=True)

        try:
            organization = organizations[np.argmax(corg)]
            if 'people' in tasks or 'all' in tasks:
                outp_people = output_people(infile, doc, organization)
            else:
                outp_people = atc([infile], 91)
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
            organization = []
            outp_people = atc([infile], 91)
            main_sector = []
            orgs_details = []

    # Output
    opd_p.append(outp_people)
    opd_g.append([infile, organization, main_sector])
    opd_o.append([infile, organization, ots(orgs_details)])

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished file:', infile)
    return opd_p, opd_g, opd_o


def output_people(infile, doc, organization):
    """ Gather information about people and structure the output."""
    persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
    (ambassadors, board_positions, p_directeur, p_rvt, p_bestuur, p_ledenraad,
     p_kasc, p_controlec) = extract_persons(doc, persons)
    board = np.concatenate([p_directeur, p_bestuur, p_rvt, p_ledenraad, p_kasc, p_controlec])
    # try again if unlikely results
    if (len(p_rvt) > 12 or len(p_bestuur) > 12 or (len(p_rvt) == 0 and len(p_bestuur) == 0) or
            len(board_positions) <= 3):
        text = preprocess_pdf(infile, '. ')
        doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)
        persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
        (ambassadors, board_positions, p_directeur, p_rvt, p_bestuur,
         p_ledenraad, p_kasc, p_controlec) = extract_persons(doc, persons)
        board = np.concatenate([p_directeur, p_bestuur, p_rvt, p_ledenraad, p_kasc, p_controlec])
    output = [infile, organization, ots(persons), ots(ambassadors), ots(board),
              ots(board_positions)]
    output.extend(atc(p_directeur, 5))
    output.extend(atc(p_rvt, 20))
    output.extend(atc(p_bestuur, 20))
    output.extend(atc(p_ledenraad, 30))
    output.extend(atc(p_kasc, 5))
    output.extend(atc(p_controlec, 5))
    return output


def ots(inp):
    """ Output to string: Convert array output to a backspace-seperated string """
    out_string = ""
    for element in inp:
        out_string += str(element) + "\n"
    return out_string


def atc(inp, length):
    """ Array to columns: Split array into [length] variables which will be converted into columns
        in the final output"""
    outlist = ['']*length
    if inp is not None:
        for i, c_inp in enumerate(inp):
            if i == length - 1 and len(inp) > length:
                print("Problem: there are more persons in one of the categories than allocated "
                      "columns.")
                outlist[i] = ots(inp[i:])
                break
            outlist[i] = c_inp
    return outlist


def download_stanza_NL():
    '''Download stanza Dutch library if not already present.'''
    outpath = os.path.join(os.getcwd(), 'stanza_resources')
    outf = os.path.join(outpath, 'nl')
    outfile = os.path.join(outf, 'default.zip')
    if not os.path.exists(outfile):
        stanza.download('nl', model_dir=outpath)
    return outfile
