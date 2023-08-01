# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

import os
from datetime import datetime
import numpy as np
import stanza
from auto_extract.classify_organisation import predict_main_sector
from auto_extract.extract_persons import extract_persons
from auto_extract.extract_related_orgs import collect_orgs
from auto_extract.extract_related_orgs import count_number_of_mentions
from auto_extract.preprocessing import preprocess_pdf


def extract_pdf(infile: str, opd_p: np.array, opd_g: np.array, opd_o: np.array, tasks: list,
                pf_m: str = os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'trained_sector_classifier.joblib'),
                pf_l: str = os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'labels_sector_classifier.joblib'),
                pf_v: str = os.path.join(os.path.join(os.getcwd(), 'Pretrained'), 'tf_idf_vectorizer.joblib')):
    """Extract information from a PDF file using the stanza pipeline.

    This function extracts information from a given PDF file ('infile') using the stanza pipeline.
    It takes the following steps:

    1. Preprocesses the PDF file using the 'preprocess_pdf' function.
    2. Based on the specified 'tasks', different extraction processes are performed:
       - If the only 'task' specified is 'sectors', it predicts the main sector using a 
         pretrained classifier (given by the files pf_m, pf_l, pf_v) and updates the output 'opd_g'.
       - Otherwise, it applies the pretrained Dutch stanza pipeline to the text
         and extracts unique persons and organizations. Next, depending on the specified 'tasks',
         the functions output_people ('task' 'people'), output_related_orgs ('task' 'orgs'), 
         and predict_main_sector ('task', 'sectors') are appied. Results are used to update opd_p,
         opd_o, and opd_g respectively.

    Args:
        infile (str): The path to the input PDF file for information extraction.
        opd_p (numpy.ndarray): A numpy array containing output for people mentioned in pdf.
        opd_g (numpy.ndarray): A numpy array containing predicted sector in a pdf.
        opd_o (numpy.ndarray): A numpy array containing related organizations mentioned in a pdf.
        tasks (list): A list of tasks to perform during extraction, e.g., ['sectors'],
                      ['people'], ['orgs'], or ['all'].

    Returns:
        opd_p (identified people), opd_g (predicted sector), opd_o (related organisations); all stored
        in updated np.arrays
    """

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Working on file:', infile)
    text = preprocess_pdf(infile, ', ')
    if tasks == ['sectors']:
        main_sector = predict_main_sector(pf_m, pf_l, pf_v, text)
        opd_g = np.concatenate((opd_g,
                                np.array([[os.path.basename(infile), '', main_sector]])),
                                axis=0)
    else:
        # Apply pre-trained Dutch stanza pipeline to text
        download_stanza_NL()
        nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
        doc = nlp(text)

        # Extract all unique persons and organizations from the text using
        # the named entity recognition function of stanza
        organizations, corg = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "ORG"],
                                        return_counts=True)

        try:
            organization = organizations[np.argmax(corg)]
            if 'people' in tasks or 'all' in tasks:
                outp_people = output_people(infile, doc, organization)
                opd_p = np.concatenate((opd_p, np.array([outp_people])), axis=0)
            if 'orgs' in tasks or 'all' in tasks:
                orgs_details = output_related_orgs(infile, doc, nlp)
                for org_details in orgs_details:
                    opd_o = np.concatenate((opd_o, np.array([org_details])), axis=0)
            if 'sectors' in tasks or 'all' in tasks:
                main_sector = predict_main_sector(pf_m, pf_l, pf_v, text)
                opd_g = np.concatenate((opd_g,
                           np.array([[os.path.basename(infile), organization, main_sector]])),
                           axis=0)
        except ValueError:
            organization = ''
            outp_people = atc([os.path.basename(infile)], 91)
            opd_p = np.concatenate((opd_p, np.array([outp_people])), axis=0)
            opd_g = np.concatenate((opd_g,
                           np.array([[os.path.basename(infile), organization, '']])),
                           axis=0)
            opd_o = np.concatenate((opd_o, np.array([['', '', '']])), axis=0)

    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished file:', infile)
    return opd_p, opd_g, opd_o


def output_people(infile, doc, organization):
    """ Gather information about people and structure the output.

    This function gathers information about people (persons) mentioned in the provided 'doc'
    (a stanza-processed document) and structures the output for further processing. The function
    performs the following steps:

    1. Extracts unique persons using named entity recognition (NER) from the 'doc' document.
    2. Calls the 'extract_persons' function to categorize the extracted persons into different roles,
       such as ambassadors, board positions, directors, etc.
    3. If the initial extraction results seem unlikely or insufficient, the function preprocesses the
       text content of the input PDF file ('infile') and reprocesses it using the stanza pipeline
       for more accurate results.
    4. Structures the output data (organization, persons, ambassadors, bestuursleden,
       and board positions (i.e. directors, raad van toezicht, bestuur, ledenraad, kascommissie, controlecommisie)
       using the 'ots' and 'atc' functions for formatting.

    Args:
        infile (str): The path to the input PDF file for information extraction.
        doc (stanza.Document): A stanza-processed document containing named entity recognition results.
        organization (str): The main organization mentioned in the text.

    Returns:
        list: A list containing structured output information, including:
              - The filename of the input file.
              - The main organization mentioned in the text, i.e. the analyzed organization.
              - The extracted persons.
              - The ambassadors, bestuur.
              - Specified board member roles for members identified as bestuur:
                directors, raad van toezicht, bestuursleden, ledenraad, kascommissie, controlecommisie
    """

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
    output = [os.path.basename(infile), organization, ots(persons), ots(ambassadors), ots(board),
              ots(board_positions)]
    output.extend(atc(p_directeur, 5))
    output.extend(atc(p_rvt, 20))
    output.extend(atc(p_bestuur, 20))
    output.extend(atc(p_ledenraad, 30))
    output.extend(atc(p_kasc, 5))
    output.extend(atc(p_controlec, 5))
    return output


def output_related_orgs(infile, doc, nlp):
    """ Gather information about all mentioned orgnaizations in the text and structure the
    output.
    
    Args:
        infile (str): The path to the input PDF file for information extraction.
        doc (stanza.Document): A stanza-processed document containing information about named entities.
        nlp (stanza.Pipeline): The stanza pipeline object for natural language processing.

    Returns:
        list: A list of lists, where each sublist contains the following information:
              - The filename of the input file.
              - The name of the organization mentioned in the text.
              - The number of times the organization is mentioned in the text.
    """
    orgs = collect_orgs(infile, nlp)
    output = []
    for o in orgs:
        n_org = count_number_of_mentions(doc, o)
        op = [os.path.basename(infile), o, str(n_org)]
        if n_org > 0:
            output.append(op)
    return output


def ots(inp: np.array):
    """Output to string: Convert array output to a backspace-seperated string.
    
    Args:
        inp (np.array): array to be converted to string
    
    Returns:
        out_string: a string containing the elements of the of the 'inp' array, 
        converted into a backspace-separed string
    """
    out_string = ""
    for element in inp:
        out_string += str(element) + "\n"
    return out_string


def atc(inp, length):
    """Array to columns: Split array into [length] variables which will be converted into columns
        in the final output.
    
    args:
    """
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
