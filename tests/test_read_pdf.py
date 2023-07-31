"""Tests for functions included in read_pdf"""
import os
import numpy as np
import stanza
from auto_extract.preprocessing import preprocess_pdf
from auto_extract.read_pdf import atc
from auto_extract.read_pdf import download_stanza_NL
from auto_extract.read_pdf import extract_pdf
from auto_extract.read_pdf import ots
from auto_extract.read_pdf import output_people


def test_stanza_NL():
    """Unit test function for the 'download_stanza_NL' function.

    This function tests the 'download_stanza_NL' function by checking if the downloaded
    stanza data file exists. The function downloads the required Stanza
    (NLP library) data for the Dutch language.
    
    Raises:
        AssertionError: If the 'download_stanza_NL' function fails to download the data
                        or if the downloaded file does not exist.
    """
    assert(os.path.exists(download_stanza_NL()))


def test_ots():
    """Unit test function for the 'ots' function.

    This function tests the 'ots' function, which converts a NumPy array of strings
    into a single concatenated string with each element separated by a newline.

    The test creates a sample NumPy array ('test') containing two strings, 'test' and 'test2',
    and asserts that the output of the 'ots' function matches the expected string:
    "test\ntest2\n".

    Raises:
        AssertionError: If the output of the 'ots' function does not match the expected string.
    """
    test = np.array(['test', 'test2'])
    assert(ots(test) == str('test\ntest2\n'))


def test_atc():
    test = np.array(['Jane', 'Doe', 'John Doe'])
    assert(atc(test, 2) == ['Jane', 'Doe\nJohn Doe\n'])


def test_ouput_people():
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    text = preprocess_pdf(infile, ' ')
    doc = stanza.Pipeline(lang='nl', processors='tokenize,ner')(text)
    people = ('A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nD.A. Rooden\n' +
              'Dirkje Rooden\nE. van Grijs\nEduard van Grijs\nF. de Blauw\nFerdinand de Blauw\n' +
              'G. Roze\nGerard Roze\nH. Doe\nHendrik Doe\nHendrik Groen\nIsaak Paars\nJ. Doe\n' +
              'Jan van Oranje\nJane Doe\nKarel\nLodewijk\nMaria\nMohammed El Idrissi\n' +
              'Mr. H. Hendrik Groen\nNico\nOtto\nPieter\nSarah\nSaïda Benali\nThomas\n')
    bestuursmensen = ('Jane Doe\nDirkje Rooden\nEduard van Grijs\nFerdinand de Blauw\n' +
                      'Anna de Wit\nHendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\n' +
                      'Jan van Oranje\nKarel\nLodewijk\nMaria\nGerard Roze\n' +
                      'Hendrik Groen\nMohammed El Idrissi\nSaïda Benali\n')
    posities = ('Anna de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
                'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
                'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
                'Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
                'Cornelis Geel - rvt - lid\nIsaak Paars - ledenraad - voorzitter\n' +
                'Jan van Oranje - ledenraad - penningmeester\nKarel - ledenraad - lid\n' +
                'Lodewijk - ledenraad - \nMaria - ledenraad - \n' +
                'Mohammed El Idrissi - controlecommissie - \n' +
                'Saïda Benali - controlecommissie - \nBernard Zwartjes - rvt - \n')
    expected_output = ([os.path.basename(infile),
                       'Bedrijf',
                        people,
                        'Sarah\nThomas\n',
                        bestuursmensen,
                        posities,
                        'Jane Doe', '', '', '', '',
                        'Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                        'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '',
                        'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                        '', '', '',
                        'Gerard Roze', 'Hendrik Groen', '', '', '',
                        'Mohammed El Idrissi', 'Saïda Benali', '', '', ''])
    assert(output_people(infile, doc, 'Bedrijf') == expected_output)


def test_extract_pdf():
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    tasks = ['all']
    opd_p = np.array([]).reshape(0,91)
    opd_g = np.array([]).reshape(0,3)
    opd_o = np.array([]).reshape(0,3)
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    e_op = np.array([[os.path.basename(infile), 'Bedrijf',
              'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nD.A. Rooden\n' +
              'Dirkje Rooden\nE. van Grijs\nEduard van Grijs\nF. de Blauw\nFerdinand de Blauw\n' +
              'G. Roze\nGerard Roze\nH. Doe\nHendrik Doe\nHendrik Groen\nIsaak Paars\nJ. Doe\n' +
              'Jan van Oranje\nJane Doe\nKarel\nLodewijk\nMaria\nMohammed El Idrissi\n' +
              'Mr. H. Hendrik Groen\nNico\nOtto\nPieter\nSarah\nSaïda Benali\nThomas\n',
              'Sarah\nThomas\n',
              'Jane Doe\nDirkje Rooden\nEduard van Grijs\nFerdinand de Blauw\nAnna de Wit\n' +
              'Hendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\nJan van Oranje\n' +
              'Karel\nLodewijk\nMaria\nGerard Roze\nHendrik Groen\nMohammed El Idrissi\n' +
              'Saïda Benali\n',
              'Anna de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
              'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
              'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
              'Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
              'Cornelis Geel - rvt - lid\nIsaak Paars - ledenraad - voorzitter\n' +
              'Jan van Oranje - ledenraad - penningmeester\nKarel - ledenraad - lid\n' +
              'Lodewijk - ledenraad - \nMaria - ledenraad - \n' +
              'Mohammed El Idrissi - controlecommissie - \nSaïda Benali - controlecommissie - \n' +
              'Bernard Zwartjes - rvt - \n',
              'Jane Doe', '', '', '', '',
              'Anna de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '',
              'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '',
              'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              'Gerard Roze', 'Hendrik Groen', '', '', '',
              'Mohammed El Idrissi', 'Saïda Benali', '', '', '']])
    e_og = np.array([[os.path.basename(infile), 'Bedrijf', 'Natuur en milieu']])
    e_oo = np.array([[os.path.basename(infile), 'Bedrijf2', '1'],
            [os.path.basename(infile), 'Bedrijf3', '1']])
    assert(np.alltrue(e_op == op))
    assert(np.alltrue(e_og == og))
    assert(np.alltrue(e_oo == oo))
    opd_p = np.array([]).reshape(0,91)
    opd_g = np.array([]).reshape(0,3)
    opd_o = np.array([]).reshape(0,3)
    tasks = ['sectors']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(np.alltrue(op == opd_p))
    assert(np.alltrue(og == np.array([[os.path.basename(infile), '', 'Natuur en milieu']])))
    assert(np.alltrue(oo == opd_o))
    opd_p = np.array([]).reshape(0,91)
    opd_g = np.array([]).reshape(0,3)
    opd_o = np.array([]).reshape(0,3)
    tasks = ['people']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(np.alltrue(e_op == op))
    assert(np.alltrue(og == opd_g))
    assert(np.alltrue(oo == opd_o))
    opd_p = np.array([]).reshape(0,91)
    opd_g = np.array([]).reshape(0,3)
    opd_o = np.array([]).reshape(0,3)
    tasks = ['orgs']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(np.alltrue(op == opd_p))
    assert(np.alltrue(og == opd_g))
    assert(np.alltrue(oo == e_oo))
    infile = os.path.join(indir, 'test_report3.pdf')
    opd_p = np.array([]).reshape(0,91)
    opd_g = np.array([]).reshape(0,3)
    opd_o = np.array([]).reshape(0,3)
    tasks = ['people']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    e_op = np.array(([[os.path.basename(infile), 'Bedrijf',
              'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nH. Doe\nHendrik Doe\n' +
              'J. Doe\nJane Doe\nQuirine de Bruin\nRudolph de Bruin\nSimon de Zwart\n' +
              'Tinus de Zwart\nVictor Wit\nWillem Wit\nXantippe de Bruin\nYolanda\nZander\n',
              '',
              'Jane Doe\nAnna de Wit\nHendrik Doe\nBernard Zwartjes\nCornelis Geel\n',
              'Anna de Wit - rvt - vice-voorzitter\nHendrik Doe - rvt - voorzitter\n' +
              'Jane Doe - directeur - directeur\nBernard Zwartjes - rvt - \n' +
              'Cornelis Geel - rvt - lid\n',
              'Jane Doe', '', '', '', '',
              'Anna de Wit', 'Hendrik Doe', 'Bernard Zwartjes', 'Cornelis Geel',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '']]))
    assert(np.alltrue(op == e_op))
