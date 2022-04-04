import os
import numpy as np
import stanza
from auto_extract.read_pdf import download_stanza_NL, ots, atc, output_people, extract_pdf
from auto_extract.preprocessing import preprocess_pdf


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
                      'A.B. de Wit\nHendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\n' +
                      'Jan van Oranje\nKarel\nLodewijk\nMaria\nGerard Roze\n' +
                      'Mr. H. Hendrik Groen\nMohammed El Idrissi\nSaïda Benali\n')
    posities = ('A.B. de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
                'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
                'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
                'Mr. H. Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
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
                        'A.B. de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                        'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '',
                        'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '',
                        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                        '', '', '',
                        'Gerard Roze', 'Mr. H. Hendrik Groen', '', '', '',
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
              'Jane Doe\nDirkje Rooden\nEduard van Grijs\nFerdinand de Blauw\nA.B. de Wit\n' +
              'Hendrik Doe\nCornelis Geel\nBernard Zwartjes\nIsaak Paars\nJan van Oranje\n' +
              'Karel\nLodewijk\nMaria\nGerard Roze\nMr. H. Hendrik Groen\nMohammed El Idrissi\n' +
              'Saïda Benali\n',
              'A.B. de Wit - rvt - vice-voorzitter\nDirkje Rooden - bestuur - lid\n' +
              'Eduard van Grijs - bestuur - \nFerdinand de Blauw - bestuur - \n' +
              'Gerard Roze - kascommissie - voorzitter\nHendrik Doe - rvt - voorzitter\n' +
              'Mr. H. Hendrik Groen - kascommissie - \nJane Doe - directeur - directeur\n' +
              'Cornelis Geel - rvt - lid\nIsaak Paars - ledenraad - voorzitter\n' +
              'Jan van Oranje - ledenraad - penningmeester\nKarel - ledenraad - lid\n' +
              'Lodewijk - ledenraad - \nMaria - ledenraad - \n' +
              'Mohammed El Idrissi - controlecommissie - \nSaïda Benali - controlecommissie - \n' +
              'Bernard Zwartjes - rvt - \n',
              'Jane Doe', '', '', '', '',
              'A.B. de Wit', 'Hendrik Doe', 'Cornelis Geel', 'Bernard Zwartjes', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '',
              'Dirkje Rooden', 'Eduard van Grijs', 'Ferdinand de Blauw', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '',
              'Isaak Paars', 'Jan van Oranje', 'Karel', 'Lodewijk', 'Maria', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              'Gerard Roze', 'Mr. H. Hendrik Groen', '', '', '',
              'Mohammed El Idrissi', 'Saïda Benali', '', '', '']])
    e_og = [[infile, 'Bedrijf', 'Natuur en milieu']]
    e_oo = ([[infile, 'Bedrijf',
              'Bedrijf - 11 - none - none\nBedrijf2 - 1 - none - none\n' +
              'Financiën - 1 - none - none\nRaad van Toezicht RvT - 1 - none - none\n' +
              'RvT - 2 - none - none\n']])
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
    assert(e_oo == oo)
    infile = os.path.join(indir, 'test_report3.pdf')
    opd_p = []
    opd_g = []
    opd_o = []
    tasks = ['people']
    op, og, oo = extract_pdf(infile, opd_p, opd_g, opd_o, tasks)
    e_op = ([[infile, 'Bedrijf',
              'A.B. de Wit\nAnna de Wit\nBernard Zwartjes\nCornelis Geel\nH. Doe\nHendrik Doe\n' +
              'J. Doe\nJane Doe\nQuirine de Bruin\nRudolph de Bruin\nSimon de Zwart\n' +
              'Tinus de Zwart\nVictor Wit\nWillem Wit\nXantippe de Bruin\n',
              '',
              'Jane Doe\nA.B. de Wit\nHendrik Doe\nBernard Zwartjes\nCornelis Geel\n',
              'Jane Doe - directeur - directeur\nA.B. de Wit - rvt - \nHendrik Doe - rvt - \n' +
              'Bernard Zwartjes - rvt - \nCornelis Geel - rvt - \n',
              'Jane Doe', '', '', '', '',
              'A.B. de Wit', 'Hendrik Doe', 'Bernard Zwartjes', 'Cornelis Geel',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '']])
    assert(op == e_op)
