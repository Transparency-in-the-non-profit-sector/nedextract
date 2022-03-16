# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import stanza
import numpy as np
from datetime import datetime

from auto_extract.preprocessing import preprocess_pdf
from auto_extract.extract_persons import extract_persons
from auto_extract.extract_related_orgs import extract_orgs
from auto_extract.classify_organisation import predict_main_sector


def extract_pdf(infile, outputdata):
    """ Extract information from a pdf file using a stanza pipline. """

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Working on file:', infile)
    text = preprocess_pdf(infile)

    # Apply pre-trained Dutch stanza pipeline to text
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
        ambassadors, board, board_positions = extract_persons(doc)
        main_sector = predict_main_sector('./Pretrained_model/trained_sector_classifier.joblib',
                                          './Pretrained_model/labels_sector_classifier.joblib',
                                          './Pretrained_model/tf_idf_vectorizer.joblib',
                                          text)
        orgs_details = extract_orgs(text, organizations)
    except ValueError:
        (organization, ambassadors, board, board_positions, main_sector,
         orgs_details) = ([], [], [], [], [], [])

    outputdata.append([infile, organization, main_sector, ots(persons), ots(ambassadors),
                      ots(board), ots(board_positions), ots(orgs_details)])

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished file:', infile)
    return outputdata


def ots(input):
    """ Output to string: Convert array output to a backspace-seperated string """
    out_string = ""
    for element in input:
        out_string += str(element) + "\n"

    return out_string
