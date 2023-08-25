"""This file contains the lass PDFInformationExtractor wiht functions to extract information from pdf files.

The different functions use the stanza Dutch pipeline to extract
information on persons and organisations from pdf files and structure the output.
"""

import os
from datetime import datetime
import numpy as np
import stanza
from nedextract.classify_organisation import predict_main_sector
from nedextract.extract_persons import extract_persons
from nedextract.extract_related_orgs import collect_orgs
from nedextract.preprocessing import preprocess_pdf
from nedextract.utils.orgs_checks import OrganisationExtraction


class PDFInformationExtractor:
    """Class for extracting information from PDF files using the stanza pipeline.

    This class provides functionality to extract information from PDF files using the stanza pipeline.
    It encapsulates various methods for preprocessing PDFs, predicting main sectors, extracting
    unique persons and organizations, and structuring the output. The class uses pretrained models
    for sector classification and named entity recognition.

    Attributes:
        tasks (list): A list of tasks to perform during extraction, e.g., ['sectors'],
                     ['people'], ['orgs'], or ['all'].
        pf_m (str): The path to the pretrained classifier file for sector prediction.
        pf_l (str): The path to the pretrained label encoding file for sector prediction.
        pf_v (str): The path to the pretrained tf-idf vectorizer file for sector prediction.

    Methods:
        extract_pdf(infile: str, opd_p: np.array, opd_g: np.array, opd_o: np.array):
            Extract information from a PDF file using the stanza pipeline
        output_people(infile: str, doc, organization: str): Gathers information about people
                                                            and structures the output.
        output_related_orgs(infile: str, doc: stanza.doc, nlp: stanza.Pipeline):
            Gathers information about mentioned organizations and structures the output.
        ots(inp: np.array): Converts array output to a backspace-seperated string
        atc(inp: np.array, length: int): Splits an array into [length] variables for output columns.
        download_stanza_NL(): Downloads the stanza Dutch library if not already present.
    """

    def __init__(self, tasks, pf_m: str = None, pf_l: str = None, pf_v: str = None):
        """Initialize the PDFInformationExtractor class with pretrained model file paths.

        Args:
            tasks (list): a A list of tasks to perform during extraction, e.g., ['sectors'],
                     ['people'], ['orgs'], or ['all']
            pf_m (str): The path to the pretrained classifier file for sector prediction.
            pf_l (str): The path to the pretrained label encoding file for sector prediction.
            pf_v (str): The path to the pretrained tf-idf vectorizer file for sector prediction.
        """
        self.tasks = tasks
        self.pf_m = pf_m or os.path.join(os.getcwd(), 'Pretrained', 'trained_sector_classifier.joblib')
        self.pf_l = pf_l or os.path.join(os.getcwd(), 'Pretrained', 'labels_sector_classifier.joblib')
        self.pf_v = pf_v or os.path.join(os.getcwd(), 'Pretrained', 'tf_idf_vectorizer.joblib')
        self.nlp = None

    def extract_pdf(self, infile: str, opd_p: np.array, opd_g: np.array, opd_o: np.array):
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

        Returns:
            opd_p (identified people), opd_g (predicted sector), opd_o (related organisations); all stored
            in updated np.arrays
        """
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Working on file:', infile)
        text = preprocess_pdf(infile, ', ')
        if self.tasks == ['sectors']:
            main_sector = predict_main_sector(self.pf_m, self.pf_l, self.pf_v, text)
            opd_g = np.concatenate((opd_g,
                                    np.array([[os.path.basename(infile), '', main_sector]])),
                                   axis=0)
        else:
            # Apply pre-trained Dutch stanza pipeline to text
            self.download_stanza_NL()
            nlp = stanza.Pipeline(lang='nl', processors='tokenize,ner')
            doc = nlp(text)

            # Extract all unique persons and organizations from the text using the named entity recognition function of stanza
            organizations, corg = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "ORG"],
                                            return_counts=True)

            # call corresponding functions for each specified tasks
            try:
                organization = organizations[np.argmax(corg)]
                if 'people' in self.tasks or 'all' in self.tasks:
                    outp_people = self.output_people(infile, doc, organization)
                    opd_p = np.concatenate((opd_p, np.array([outp_people])), axis=0)
                if 'orgs' in self.tasks or 'all' in self.tasks:
                    orgs_details = self.output_related_orgs(infile, doc, nlp)
                    for org_details in orgs_details:
                        opd_o = np.concatenate((opd_o, np.array([org_details])), axis=0)
                if 'sectors' in self.tasks or 'all' in self.tasks:
                    main_sector = predict_main_sector(self.pf_m, self.pf_l, self.pf_v, text)
                    opd_g = np.concatenate((opd_g,
                                            np.array([[os.path.basename(infile), organization, main_sector]])),
                                           axis=0)
            except ValueError:
                organization = ''
                outp_people = self.atc([os.path.basename(infile)], 91)
                opd_p = np.concatenate((opd_p, np.array([outp_people])), axis=0)
                opd_g = np.concatenate((opd_g,
                                        np.array([[os.path.basename(infile), organization, '']])),
                                       axis=0)
                opd_o = np.concatenate((opd_o, np.array([['', '', '']])), axis=0)

        print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished file:', infile)
        return opd_p, opd_g, opd_o

    def output_people(self, infile: str, doc, organization: str):
        """Gather information about people and structure the output.

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
        # Collect unique persons named in text
        persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])

        # call extract_persons function
        (ambassadors, board_positions, p_directeur, p_rvt, p_bestuur, p_ledenraad,
         p_kasc, p_controlec) = extract_persons(doc, persons)

        # Combine results
        board = np.concatenate([p_directeur, p_bestuur, p_rvt, p_ledenraad, p_kasc, p_controlec])

        # try again if unlikely results
        if (len(p_rvt) > 12 or len(p_bestuur) > 12 or (len(p_rvt) == 0 and len(p_bestuur) == 0) or
                len(board_positions) <= 3):
            doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(preprocess_pdf(infile, '. '))
            persons = np.unique([f'{ent.text}' for ent in doc.ents if ent.type == "PER"])
            (ambassadors, board_positions, p_directeur, p_rvt, p_bestuur,
             p_ledenraad, p_kasc, p_controlec) = extract_persons(doc, persons)
            board = np.concatenate([p_directeur, p_bestuur, p_rvt, p_ledenraad, p_kasc, p_controlec])

        # Structure output
        output = [os.path.basename(infile), organization, self.ots(persons), self.ots(ambassadors), self.ots(board),
                  self.ots(board_positions)]
        output.extend(self.atc(p_directeur, 5))
        output.extend(self.atc(p_rvt, 20))
        output.extend(self.atc(p_bestuur, 20))
        output.extend(self.atc(p_ledenraad, 30))
        output.extend(self.atc(p_kasc, 5))
        output.extend(self.atc(p_controlec, 5))
        return output

    @staticmethod
    def output_related_orgs(infile: str, doc, nlp):
        """Gather information about all mentioned orgnaizations in the text and structure the output.

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
        for org in orgs:
            n_org = OrganisationExtraction(doc=doc, org=org).count_number_of_mentions()
            output_p = [os.path.basename(infile), org, str(n_org)]
            if n_org > 0:
                output.append(output_p)
        return output

    @staticmethod
    def ots(inp: np.array):
        r"""Output to string: Convert array output to a backspace-seperated string.

        Steps:
        - define an empty string 'out_string'
        - for each element in 'inp', add the element to 'out_string', followed by the string '\n'

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

    def atc(self, inp, length: int):
        """Array to columns: Split array into [length] list variables which will be converted into columns in the final output.

        This function takes the following steps:

        - Initializes an output list ('outlist') with [length] empty strings.
        - If the input array 'inp' is not None, the function iterates through its elements and fills
        the 'outlist' with the first [length] elements. If there are more elements in the 'inp' array
        than the specified 'length', it prints a warning message and includes the remaining elements
        as a single element in the last column.

        Args:
            inp (list or None): The input array to be split into columns.
            length (int): The number of columns desired in the final output.

        Returns:
            outlist: A list of length 'length' containing the elements of the input array. If the input
                array has more elements than 'length', the last column will contain the remaining
                elements as a single element (concatenated using the 'ots' function).
        """
        outlist = ['']*length
        if inp is not None:
            for i, c_inp in enumerate(inp):
                if i == length - 1 and len(inp) > length:
                    print("Problem: there are more persons in one of the categories than allocated "
                          "columns.")
                    outlist[i] = self.ots(inp[i:])
                    break
                outlist[i] = c_inp
        return outlist

    @staticmethod
    def download_stanza_NL():
        """Download stanza Dutch library if not already present.

        This function checks if the stanza Dutch library is already downloaded. If not, it downloads
        the necessary files for Dutch language processing and saves them to the 'stanza_resources'
        directory within the current working directory. The function performs the following steps:

        - Defines the output path and file names for the downloaded Dutch language model files.
        - Checks if the output file 'outfile' exists in the 'stanza_resources' directory.
        - If the output file is not present, it uses the 'stanza.download' function to download
        the Dutch language model ('nl') and saves it in the 'outpath' directory.

        Returns:
            str: The path to the downloaded Dutch language model file.
        """
        outpath = os.path.join(os.getcwd(), 'stanza_resources')
        outf = os.path.join(outpath, 'nl')
        outfile = os.path.join(outf, 'default.zip')
        if not os.path.exists(outfile):
            stanza.download('nl', model_dir=outpath)
        return outfile
