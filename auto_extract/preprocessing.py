"""This file contains functions used to download pdf files from an url and preprocess the text in pdf files.

Functions:
- preprocess_pdf
- download_pdf
- delete_downloaded_pdf
"""

import os
import urllib.request
import pdftotext


def preprocess_pdf(infile: str, r_blankline: str = ', ', r_eol: str = ' ', r_par: str = ''):
    """Preprocesses the text extracted from a PDF file.

    This function takes the path of a PDF file, reads the text content, and performs several text
    preprocessing steps to clean and format the text.

    Args:
        infile (str): The path to the PDF file.
        r_blankline (str, optional): The replacement for consecutive blank lines. Defaults to ', '.
        r_eol (str, optional): The replacement for end-of-line characters. Defaults to ' '.
        r_par (str, optional): The replacement for parentheses. Defaults to ''.

    Returns:
        str: The preprocessed text extracted from the PDF file.
    """
    with open(infile, 'rb') as f:
        pdf = pdftotext.PDF(f)

    # preprocessing steps
    text = "\n".join(pdf)
    text = text.replace('\n\n', r_blankline).replace('\r\n\r\n', r_blankline).replace('\n', r_eol)
    text = text.replace('\r', ' ').replace('\t', ' ')
    text = text.replace('(', r_par).replace(')', r_par).replace(';', ',')
    text = text.replace('\x0c', ' ').replace('\x07', ' ').replace('\x08', ' ').replace('\xad', ' ')
    text = text.replace('•', ', ').replace('', ', ').replace('◼', ', ').replace('\uf0b7', ' ')
    text = text.replace('/', ' / ')
    while ':.' in text:
        text = text.replace(':.', ':')
    text = text.replace(':', ', ')
    while '  ' in text:
        text = text.replace('  ', ' ')
    while ', ,' in text:
        text = text.replace(', ,', ',')
    while ',,' in text:
        text = text.replace(',,', ',')
    while ' ,' in text:
        text = text.replace(' ,', ',')
    text = text.replace('.,', '.')
    while '. .' in text:
        text = text.replace('. .', '.')
    while '..' in text:
        text = text.replace('..', '.')
    while ' .' in text:
        text = text.replace(' .', '.')
    return text


def download_pdf(url):
    """Download a pdf file from an url and safe it in the cwd."""
    with urllib.request.urlopen(url) as urlfile:
        filename = os.path.join(os.getcwd(), "downloaded.pdf")
        with open(filename, 'wb') as file:
            file.write(urlfile.read())
    return filename


def delete_downloaded_pdf():
    """Delete downloaded file.

    Delete the file that is downloaded with the function download_pdf and saved as
    downloaded.pdf from the cwd.
    """
    os.remove(os.path.join(os.getcwd(), "downloaded.pdf"))
