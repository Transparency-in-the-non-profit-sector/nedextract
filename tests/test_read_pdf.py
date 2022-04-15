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
    assert(os.path.exists(download_stanza_NL()))


def test_ots():
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
    expected_output = ([infile,
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
    opd_p = []
    opd_g = []
    opd_o = []
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    e_op = ([[infile, 'Bedrijf',
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
    e_og = [[infile, 'Bedrijf', 'Natuur en milieu']]
    e_oo = ([[infile, 'Bedrijf',
               'Bedrijf - 11 - none - none\nBedrijf2 - 1 - none - none\n' +
               'Bedrijf3 - 1 - none - none\nFinanciën - 1 - none - none\n' +
               'Raad van Toezicht RvT - 1 - none - none\nRvT - 2 - none - none\n']])
    assert(e_op == op)
    assert(e_og == og)
    assert(e_oo == oo)
    opd_p = []
    opd_g = []
    opd_o = []
    tasks = ['sectors']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(op == [[[], [], [], [], [], [], [], [], [], [], []]])
    assert(og == ([[infile, '', 'Natuur en milieu']]))
    assert(oo == [[infile, '', '']])
    opd_p = []
    opd_g = []
    opd_o = []
    tasks = ['people']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(e_op == op)
    assert(og == ([[infile, 'Bedrijf',
                    []]]))
    assert(oo == [[infile, 'Bedrijf', '']])
    opd_p = []
    opd_g = []
    opd_o = []
    tasks = ['orgs']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    assert(op == [[[], [], [], [], [], [], [], [], [], [], []]])
    assert(og == ([[infile, 'Bedrijf', []]]))
    assert(oo == e_oo)
    infile = os.path.join(indir, 'test_report3.pdf')
    opd_p = []
    opd_g = []
    opd_o = []
    tasks = ['people']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    e_op = ([[infile, 'Bedrijf',
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
              '', '', '', '', '', '', '', '', '', '', '', '', '']])
    e_op2 = ([[infile, 'Bedrijf',
               'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nH. Doe\nHendrik Doe\n' +
               'J. Doe\nJane Doe\nQuirine de Bruin\nRudolph de Bruin\nSimon de Zwart\n' +
               'Tinus de Zwart\nVictor Wit\nWillem Wit\nXantippe de Bruin\nYolanda\nZander\n',
               '',
               'Jane Doe\n',
               'Jane Doe - directeur - directeur\n',
               'Jane Doe', '', '', '', '',
               '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '', '', '', '']])
    assert(op in (e_op, e_op2))
