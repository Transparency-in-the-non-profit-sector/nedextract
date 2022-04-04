import os
from auto_extract.preprocessing import delete_downloaded_pdf
from auto_extract.preprocessing import download_pdf
from auto_extract.preprocessing import preprocess_pdf


def test_preprocess_pdf():
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    text = preprocess_pdf(infile, ' ')
    text = preprocess_pdf(infile, '. ')
    text = preprocess_pdf(infile, ', ')
    assert(isinstance(text, str))


def test_download_pdf():
    url = ("https://github.com/Transparency-in-the-non-profit-sector/" +
           "np-transparency/blob/main/tests/test_report.pdf")
    filename = download_pdf(url)
    assert(os.path.exists(filename))


def test_delete_downloaded_pdf():
    delete_downloaded_pdf()
    filename = os.path.join(os.getcwd(), "downloaded.pdf")
    assert(os.path.exists(filename) is False)
